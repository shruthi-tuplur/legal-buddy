from dotenv import load_dotenv
import os

load_dotenv()
print("OPENAI_API_KEY loaded:", os.getenv("OPENAI_API_KEY"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from typing import Optional, List, Any, Dict

from main import fetch_case_by_id, build_llm_context_pack
from llm_client_openai import call_llm_with_context_pack
from memory_store import InMemorySessionStore
from stats_service import compute_comparison_stats_for_user_context
from tools import build_timeline

from simulator_tree_loader import get_sim_tree_v1, pick_root_for_stage  # ✅ new


app = FastAPI()
print("LOADED api.py")


@app.get("/health")
def health():
    return {"status": "ok"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CaseRequest(BaseModel):
    case_id: str


@app.post("/explain-case")
def explain_case(req: CaseRequest):
    case_data = fetch_case_by_id(req.case_id)
    if not case_data:
        return {"error": "Case not found"}

    context = build_llm_context_pack(case_data)
    explanation = call_llm_with_context_pack(context)

    return {
        "case_id": req.case_id,
        "explanation": explanation,
        "stage": context.get("stage"),
    }


store = InMemorySessionStore()


def is_timeline_intent(text: str) -> bool:
    t = (text or "").strip().lower()
    if "timeline" in t:
        return True
    triggers = [
        "show my timeline",
        "show timeline",
        "court dates",
        "next court date",
        "chronological",
        "in order",
        "sequence of events",
        "what happened so far",
        "what has happened so far",
    ]
    return any(p in t for p in triggers)


def is_simulator_intent(text: str) -> bool:
    t = (text or "").strip().lower()
    triggers = [
        "procedural simulator",
        "simulator",
        "choose your own adventure",
        "choose-your-own-adventure",
        "what happens next",
        "what usually happens next",
        "what comes next",
        "next steps",
        "what usually comes next",
        "plea discussion",
        "plea discussions",
        "motions",
        "motion to suppress",
        "motion to dismiss",
        "discovery",
        "trial-setting",
        "trial setting",
    ]
    return any(p in t for p in triggers)


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    case_id: Optional[str] = None
    user_message: str
    wantsStats: Optional[bool] = False  # ok if frontend sends it


class ChatResponse(BaseModel):
    session_id: str
    stage_label: Optional[str] = None
    explanation: str
    ui_cards: List[Dict[str, Any]] = []


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = store.get_or_create(req.session_id)

    if req.case_id:
        session.case_id = req.case_id

    store.append(session, "user", req.user_message)

    if not session.case_id:
        reply = "Please enter a case ID first so I can ground the conversation in your case."
        store.append(session, "assistant", reply)
        return ChatResponse(session_id=session.session_id, explanation=reply, ui_cards=[])

    case_data = fetch_case_by_id(session.case_id)
    if not case_data:
        reply = f"I can’t find case ID {session.case_id} in the public record sources I'm checking right now."
        store.append(session, "assistant", reply)
        return ChatResponse(session_id=session.session_id, explanation=reply, ui_cards=[])

    context_pack = build_llm_context_pack(case_data)

    # -------------------------
    # Outcome stats (only when asked)
    # -------------------------

        # Collect UI cards for this response (stats, simulator, timeline, etc.)
    ui_cards_out: List[Dict[str, Any]] = []

    msg = (req.user_message or "").lower()
    wants_stats = bool(req.wantsStats) or any(
        k in msg
        for k in [
            "similar cases",
            "cases like mine",
            "how do cases like",
            "how do similar",
            "outcome stats",
            "statistics",
            "stats",
            "how often",
            "rate of",
            "usually turn out",
            "what do outcomes look like",
        ]
    )

    if wants_stats:
        try:
            user_stage_id = (context_pack.get("stage") or {}).get("stage_id")
            charge = ((context_pack.get("case_summary") or {}).get("charge") or {})
            user_offense_category = charge.get("offense_category") or charge.get("updated_offense_category")
            user_charge_class = charge.get("class") or charge.get("charge_class")

            stats = compute_comparison_stats_for_user_context(
                user_stage_id=user_stage_id,
                user_offense_category=user_offense_category,
                user_charge_class=user_charge_class,
            )
            context_pack["comparison_stats"] = stats
            context_pack["ui_stats"] = stats

        except Exception as e:
            context_pack["comparison_stats"] = {
                "skipped": True,
                "reason": f"Stats hook failed: {type(e).__name__}",
            }

        # -------------------------
    # Stats card (only when asked)
    # -------------------------
    if wants_stats:
        stats_payload = context_pack.get("comparison_stats") or {}

        if stats_payload and not stats_payload.get("skipped"):
            ui_cards_out.append({
                "type": "stats_card",
                "payload": {
                    "title": "Similar case outcomes",
                    "subtitle": f"Sample size: {stats_payload.get('sample_size', 0)}",
                    "outcomes_pct": stats_payload.get("outcomes_pct", {}),
                    "outcomes_counts": stats_payload.get("outcomes_counts", {}),
                    "time_to_disposition_days": stats_payload.get("time_to_disposition_days", {}),
                    "top_raw_dispositions": stats_payload.get("top_raw_dispositions", []),
                }
            })
        else:
            # Show a small "unavailable" card so it doesn't feel broken
            ui_cards_out.append({
                "type": "stats_card",
                "payload": {
                    "title": "Similar case outcomes",
                    "subtitle": "Stats unavailable right now",
                    "skipped": True,
                    "reason": stats_payload.get("reason", "No cohort available."),
                }
            })



    # -------------------------
    # History
    # -------------------------
    history_lines = []
    for m in session.messages[-12:]:
        prefix = "User" if m.role == "user" else "Assistant"
        history_lines.append(f"{prefix}: {m.content}")
    context_pack["chat_history"] = "\n".join(history_lines)

    context_pack["active_case_id"] = session.case_id
    context_pack["latest_user_message"] = req.user_message

    history = []
    for m in session.messages[-13:-1]:
        if m.role in ("user", "assistant"):
            history.append({"role": m.role, "content": m.content})

    stage_label = (context_pack.get("stage") or {}).get("stage_label") or ""

    # -------------------------
    # SIMULATOR INTENT
    # -------------------------
    if is_simulator_intent(req.user_message):
        tree = get_sim_tree_v1()
        root_id = pick_root_for_stage(tree, stage_label)

        ui_cards_out.append({
            "type": "simulator_card",
            "payload": {
                "tree": tree,
                "root_id": root_id,
                "stage_label": stage_label,
            }
        })

        explanation = (
            "Here’s a procedural simulator rooted at your current stage. "
            "Tap any option to explore what’s common at that fork (educational, not a prediction)."
        )
        store.append(session, "assistant", explanation)

        return ChatResponse(
            session_id=session.session_id,
            stage_label=stage_label,
            explanation=explanation,
            ui_cards=ui_cards_out,
        )

    # -------------------------
    # TIMELINE INTENT
    # -------------------------
    if is_timeline_intent(req.user_message):
        try:
            timeline_payload = build_timeline(context_pack)
            ui_cards_out.append({"type": "timeline_card", "payload": timeline_payload})
            context_pack["ui_timeline"] = timeline_payload
        except Exception as e:
            fallback = {
                "stage": stage_label or "",
                "now_node_id": None,
                "nodes": [],
                "future_placeholders": [],
                "warnings": [f"Timeline build failed: {type(e).__name__}"],
            }
            ui_cards_out.append({"type": "timeline_card", "payload": fallback})
            context_pack["ui_timeline"] = fallback

        context_pack["latest_user_message"] = (
            "The user asked to see their timeline. "
            "Briefly describe what the timeline shows (events + dates). "
            "Then explain what the highlighted 'current' node means. "
            "Keep it short (6-10 lines)."
        )

        explanation = call_llm_with_context_pack(context_pack, history=history)
        store.append(session, "assistant", explanation)

        return ChatResponse(
            session_id=session.session_id,
            stage_label=stage_label,
            explanation=explanation,
            ui_cards=ui_cards_out,
        )

    # -------------------------
    # NORMAL CHAT
    # -------------------------
    explanation = call_llm_with_context_pack(context_pack, history=history)
    store.append(session, "assistant", explanation)

    return ChatResponse(
        session_id=session.session_id,
        stage_label=stage_label,
        explanation=explanation,
        ui_cards=ui_cards_out,
    )


