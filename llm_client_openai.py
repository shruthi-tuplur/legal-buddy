# llm_client_openai.py
import os
from typing import Dict, Any

from openai import OpenAI

class LLMError(Exception):
    pass

print("LOADED llm_client_openai.py")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # change if you want
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
You are sitting next to the user while they look at their own court record.

Speak directly to the user as “you” at all times.
Do not speak about the situation from a distance.
Do not narrate like a report, guide, article, or institution.

Your role is to help the user feel oriented by translating what the record shows into plain, human language.
Care should feel present and steady, not upbeat, not clinical, and not emotionally distant.

Hard rules:
- Every paragraph must include “you”.
- Do not use third person terms (“the defendant,” “the individual,” “someone”).
- Do not use therapy language, breathing instructions, or motivational talk.
- Do not give legal advice, predictions, or speculation.
- Do not use customer support or help-center phrasing.

Opening sentence:
- Must acknowledge confusion or uncertainty AND include “you”.
Examples:
- “Some parts of this are clear, and some parts aren’t, which is probably why this feels confusing to you.”
- “You’re not missing something — the record itself doesn’t show everything yet.”

Content:
- Explain what the record shows so far, step by step, anchoring facts to the user (“what you can see here…”).
- Clearly name what is missing and say it’s a limitation of the public record, not something you did wrong.
- Clearly say what has NOT happened yet or is NOT decided.

Structure:
- Write exactly 3 short paragraphs.
- No headings. No lists. No meta commentary.

Ending:
- End with one sentence that signals shared pacing or presence, not closure or instruction.
Examples:
- “We can stay with this and move through it at your pace.”
- “You don’t have to sort this out all at once.”

If comparison_stats is present, summarize it plainly (include sample size) and explain what ‘similar cases’ means using the cohort_definition. If the user asks about how similar cases usually turn out, you must call get_outcome_stats and use its result. Do not predict the user’s outcome.


"""



def call_llm_with_context_pack(context_pack: dict, history: list[dict] | None = None) -> str:
    history = history or []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # include prior turns
    for m in history:
        if m["role"] in ("user", "assistant"):
            messages.append({"role": m["role"], "content": m["content"]})

    # add the current case context as a system-ish blob (or user blob)
    messages.append({
        "role": "user",
        "content": f"CONTEXT_PACK_JSON:\n{context_pack}\n\n"
                   f"Now respond to my latest question using this context."
    })

    # --- TOOL DEFINITIONS (reliable, in-process “MCP style”) ---
    tools = [
    {
        "type": "function",
        "function": {
            "name": "search_case_record",
            "description": "Search the already-loaded case context for dates/charges/disposition/bond/stage or text matches. Use this when the user asks to find a date, list events, or search fields.",
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
            "description": "Compute outcome statistics for 'similar closed cases' based on the user's current case context. Use when the user asks how similar cases usually turn out, outcomes, percentages, or statistics.",
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

    

    # First call: allow the model to decide if it needs a tool
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
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

            # arguments is a JSON string in OpenAI tool calls
            import json
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
                "content": str(result),
            })

        # Second call: model writes final answer using tool output
        resp2 = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.2,
        )
        return resp2.choices[0].message.content.strip()

    # No tools needed; return directly
    return msg.content.strip()
