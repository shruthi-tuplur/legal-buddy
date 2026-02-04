# llm_client_openai.py
import os
import json
from typing import Dict, Any, Optional, List

from dotenv import load_dotenv
from openai import OpenAI


class LLMError(Exception):
    pass


print("LOADED llm_client_openai.py")

# Load env early in this module so any downstream imports have access.
# (Still prefer lazy client initialization below to avoid import-time failures.)
load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_client() -> OpenAI:
    """
    Create the OpenAI client at call-time (not import-time) to avoid issues where
    environment variables are not loaded yet in uvicorn reload subprocesses.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LLMError("OPENAI_API_KEY is not set. Check your .env and load_dotenv() usage.")
    return OpenAI(api_key=api_key)


def pack_to_brief_text(context_pack: Dict[str, Any]) -> str:
    cs = context_pack.get("case_summary", {})
    stage = context_pack.get("stage", {})
    card = context_pack.get("stage_card", {})

    charge = cs.get("charge", {})
    timeline = cs.get("timeline", {})
    bond = cs.get("bond", {})
    missing = cs.get("missing_fields") or []
    missing_str = ", ".join(missing) if missing else "None shown"

    def join_list(x):
        if isinstance(x, list):
            return " ".join(str(i) for i in x)
        return str(x) if x is not None else ""

    return f"""
FACTS (public dataset)
Case ID: {cs.get('case_id', 'N/A')}
Participant ID: {cs.get('participant_id', 'N/A')}
Charge: {charge.get('charge_title', 'N/A')} | Category: {charge.get('offense_category', 'N/A')} | Class: {charge.get('class', 'N/A')}
Timeline: Incident {timeline.get('incident_date', 'N/A')}, Arrest {timeline.get('arrest_date', 'N/A')}, Received {timeline.get('received_date', 'N/A')}, Arraignment {timeline.get('arraignment_date', 'N/A')}
Bond: {bond.get('bond_type', 'N/A')} {bond.get('bond_amount', 'N/A')}
Missing fields: {missing_str}

STAGE (deterministic)
Stage: {stage.get('stage_label', 'N/A')} (id={stage.get('stage_id', 'N/A')}, confidence={stage.get('confidence', 'N/A')})
Reasons: {"; ".join(stage.get("reasons", []) or [])}

STAGE CARD
Where you are: {card.get('where_you_are', '')}
What this means: {join_list(card.get('what_this_means', []))}
What usually happens next: {join_list(card.get('what_usually_happens_next', []))}
What has not happened yet: {join_list(card.get('what_not_yet', []))}
Data limits: {card.get('data_limits', '')}
""".strip()


SYSTEM_PROMPT = """
You are looking at the user’s court record together with them.

Your stance is peer-to-peer.
You are not a support agent, counselor, narrator, or authority.
You are simply walking through what the record shows, side by side.

Speak directly to the user as “you”.
Do not explain your role or intentions.
Do not frame yourself as helping, supporting, or guiding.
Just talk normally and clearly, the way one person explains something to another.

Tone:
- Natural, grounded, human.
- Calm but not formal.
- Warm through clarity, not through emotional language.
- Never scripted, patronizing, or performatively empathetic.

Hard bans (these create customer-support energy):
- “It’s understandable that…”
- “You might be feeling…”
- “This can feel…”
- “I know this is confusing…”
- “You’re not alone…”
- “Importantly,”
- “Based on the information provided…”

Do NOT label or mirror emotions.
Do NOT acknowledge feelings explicitly.
If reassurance is needed, let it emerge from facts and process.

How reassurance should work:
- Reassure by explaining *how the system works*.
- Normalize by describing *what usually shows up at this stage*.
- Use plain observations, not emotional commentary.

Good reassurance (implicit, peer-like):
- “At this stage, the record is usually pretty bare.”
- “This part tends to look quiet on paper.”
- “Nothing here suggests a resolution yet — it just hasn’t reached that point.”
- “The record stops short here, which is normal for pretrial.”

Opening:
- Start directly with the situation.
Examples:
- “Here’s where your case is right now.”
- “Right now, your record shows you’re in the pretrial phase.”
- “Let’s ground this in what the record actually shows.”

Content:
- Translate legal terms into everyday language.
- Anchor everything to “you” (“your case,” “what you can see here”).
- Clearly say what has happened, what hasn’t, and what the record does not show.
- If information is missing, say so plainly and attribute it to the public record.

Structure:
- 2–4 short paragraphs.
- No headings.
- No lists unless dates/events need clarity (max 5 bullets).

Ending:
- End casually and steady, not supportive or motivational.
Examples:
- “That’s everything the record shows at this point.”
- “We can keep working with what’s visible here.”
- “This is as far as the public record goes right now.”

If comparison_stats is present, summarize it plainly and explain what “similar cases” means.
If the user asks how similar cases usually turn out, you must call get_outcome_stats.
Do not predict outcomes.



""".strip()


def call_llm_with_context_pack(context_pack: dict, history: Optional[List[dict]] = None) -> str:
    history = history or []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # include prior turns
    for m in history:
        if m.get("role") in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m.get("content", "")})

    # add the current case context as a user blob (so the model treats it as provided input)
    messages.append({
        "role": "user",
        "content": f"CONTEXT_PACK_JSON:\n{context_pack}\n\n"
                   f"Now respond to my latest question using this context."
    })

    # --- TOOL DEFINITIONS (reliable, in-process tools) ---
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_case_record",
                "description": (
                    "Search the already-loaded case context for dates/charges/disposition/bond/stage or text matches. "
                    "Use this when the user asks to find a date, list events, or search fields."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["all", "dates", "charges", "disposition", "bond", "stage"],
                            "description": "Which slice of the record to search."
                        },
                        "after_date": {"type": "string", "description": "Optional ISO date like 2016-01-01 to only return dates after this."},
                        "before_date": {"type": "string", "description": "Optional ISO date like 2016-12-31 to only return dates before this."},
                        "contains_text": {"type": "string", "description": "Optional text to match against keys/values."},
                    },
                    "required": ["query_type"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_outcome_stats",
                "description": (
                    "Compute outcome statistics for 'similar closed cases' based on the user's current case context. "
                    "Use when the user asks how similar cases usually turn out, outcomes, percentages, or statistics."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "stage_id": {
                            "type": "string",
                            "description": "User's current stage_id from context_pack['stage']['stage_id']."
                        },
                        "offense_category": {
                            "type": "string",
                            "description": "Offense category from the user's charge (offense_category or updated_offense_category)."
                        },
                        "charge_class": {
                            "type": "string",
                            "description": "Charge class from the user's charge (e.g., '4', 'X')."
                        },
                    },
                    "required": ["stage_id"],
                },
            },
        },
    ]

    client = get_client()

    # First call: allow the model to decide if it needs a tool
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.2,
    )

    msg = resp.choices[0].message

    # If the model called tools, run them and do a second call with results
    if getattr(msg, "tool_calls", None):
        from tools import search_case_record, get_outcome_stats  # local import to avoid circulars

        tool_results = []

        for tc in msg.tool_calls:
            name = tc.function.name
            args = tc.function.arguments

            parsed = json.loads(args) if isinstance(args, str) else (args or {})

            if name == "search_case_record":
                result = search_case_record(
                    context_pack=context_pack,
                    query_type=parsed.get("query_type", "all"),
                    after_date=parsed.get("after_date"),
                    before_date=parsed.get("before_date"),
                    contains_text=parsed.get("contains_text"),
                )

            elif name == "get_outcome_stats":
                # fallback to pulling values from context_pack if model omits them
                cs = context_pack.get("case_summary", {}) or {}
                charge = cs.get("charge", {}) or {}
                stage = context_pack.get("stage", {}) or {}

                result = get_outcome_stats(
                    stage_id=parsed.get("stage_id") or stage.get("stage_id"),
                    offense_category=parsed.get("offense_category") or charge.get("offense_category") or charge.get("updated_offense_category"),
                    charge_class=parsed.get("charge_class") or charge.get("class") or charge.get("charge_class"),
                )

            else:
                result = {"error": f"Unknown tool: {name}"}

            tool_results.append((tc.id, result))

        # Append the assistant tool-call message + tool outputs
        messages.append(msg)
        for tool_call_id, result in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        # Second call: model writes final answer using tool output
        resp2 = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
        )
        return (resp2.choices[0].message.content or "").strip()

    # No tools needed; return directly
    return (msg.content or "").strip()
