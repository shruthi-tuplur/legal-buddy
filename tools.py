# tools.py
from __future__ import annotations
from typing import Any, Dict, Optional, List, Tuple
from datetime import datetime, timedelta

# -----------------------------
# Existing search tool constants
# -----------------------------

DATE_KEYS = [
    "incident_begin_date",
    "incident_date",
    "arrest_date",
    "received_date",
    "felony_review_date",
    "arraignment_date",
    "disposition_date",
    "sentence_date",
]

EVENT_LABELS = {
    "incident_begin_date": "Incident began",
    "incident_date": "Incident",
    "arrest_date": "Arrest",
    "received_date": "Case received / filed",
    "felony_review_date": "Felony review",
    "arraignment_date": "Arraignment",
    "disposition_date": "Disposition / resolution",
    "sentence_date": "Sentencing",
}

OUTCOME_BUCKETS = {
    "dismiss": ["dismiss", "dismissed"],
    "nolle": ["nolle", "nolle prosequi", "nol-pros", "nol pros"],
    "guilty": ["guilty", "convict", "convicted", "plea of guilty"],
    "not_guilty": ["not guilty", "acquit", "acquitted"],
    "probation": ["probation"],
    "stricken": ["stricken"],
    "transfer": ["transfer", "transferred"],
}

ACTOR_KEYS = [
    "judge",
    "sentence_judge",
    "court_name",
    "court_facility",
    "law_enforcement_agency",
    "prosecutor",
    "defense_attorney",
]


def _parse_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None

    # If it's already a datetime
    if isinstance(value, datetime):
        return value

    # Epoch timestamps (seconds or ms)
    if isinstance(value, (int, float)):
        try:
            v = float(value)
            if v > 1e12:  # ms
                return datetime.fromtimestamp(v / 1000.0)
            if v > 1e9:   # seconds
                return datetime.fromtimestamp(v)
        except Exception:
            return None

    # Dict wrappers (common in some APIs)
    if isinstance(value, dict):
        for k in ("date", "$date", "value", "timestamp"):
            if k in value:
                return _parse_dt(value.get(k))
        return None

    # Strings
    if not isinstance(value, str):
        value = str(value)

    raw = value.strip()
    if not raw:
        return None

    raw = raw.replace("Z", "")  # strip Z
    # ISO attempts
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        pass

    fmts = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S.%f",
        "%b %d, %Y",  # Sep 01, 2013
        "%B %d, %Y",  # September 01, 2013 (just in case)

    ]
    for fmt in fmts:
        try:
            return datetime.strptime(raw, fmt)
        except Exception:
            continue

    return None




def _normalize(s: Any) -> str:
    return str(s).strip().lower() if s is not None else ""


def _bucket_outcome(text: str) -> Optional[str]:
    t = _normalize(text)
    if not t:
        return None
    for bucket, needles in OUTCOME_BUCKETS.items():
        for n in needles:
            if n in t:
                return bucket
    return None


def _charge_level_from_class(charge_class: Any) -> Dict[str, Any]:
    raw = str(charge_class) if charge_class is not None else ""
    c = raw.strip().upper()

    if c == "X":
        level = "Felony Class X (very severe)"
        rank = 1
    elif c == "1":
        level = "Felony Class 1 (severe)"
        rank = 2
    elif c == "2":
        level = "Felony Class 2"
        rank = 3
    elif c == "3":
        level = "Felony Class 3"
        rank = 4
    elif c == "4":
        level = "Felony Class 4"
        rank = 5
    elif c == "M":
        level = "Misdemeanor (class not specified here)"
        rank = 6
    else:
        level = f"Unknown / not provided ({raw})" if raw else "Unknown / not provided"
        rank = None

    return {"raw_class": raw, "level_label": level, "severity_rank": rank}


def _build_events_from_timeline(timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for k in DATE_KEYS:
        v = timeline.get(k)
        if not v:
            continue
        dt = _parse_dt(str(v))
        if not dt:
            continue
        events.append({
            "event_type": EVENT_LABELS.get(k, k),
            "key": k,
            "date_raw": v,
            "dt_iso": dt.isoformat(),
        })
    events.sort(key=lambda e: e["dt_iso"])
    return events


def _find_matches(fields: List[Dict[str, Any]], needle: str) -> List[Dict[str, Any]]:
    n = needle.lower()
    return [
        f for f in fields
        if n in str(f["key"]).lower() or n in str(f["value"]).lower()
    ]


def search_case_record(
    context_pack: Dict[str, Any],
    query_type: str = "all",
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    contains_text: Optional[str] = None,
) -> Dict[str, Any]:
    cs = context_pack.get("case_summary", {}) or {}
    stage = context_pack.get("stage", {}) or {}
    charge = (cs.get("charge") or {})
    timeline = (cs.get("timeline") or {})
    bond = (cs.get("bond") or {})
    stage_card = context_pack.get("stage_card", {}) or {}
    disposition = context_pack.get("disposition", {}) or {}

    fields: List[Dict[str, Any]] = []

    def add(source: str, key: str, value: Any):
        fields.append({"source": source, "key": key, "value": value})

    for k, v in charge.items():
        add("charge", k, v)
    for k, v in timeline.items():
        add("timeline", k, v)
    for k, v in bond.items():
        add("bond", k, v)
    for k, v in stage.items():
        add("stage", k, v)
    for k, v in stage_card.items():
        add("stage_card", k, v)
    for k, v in disposition.items():
        add("disposition", k, v)

    events = _build_events_from_timeline(timeline)

    qt = (query_type or "all").strip().lower()

    if qt == "event_type":
        ev = events
        if contains_text:
            needle = contains_text.lower()
            ev = [e for e in ev if needle in e["event_type"].lower() or needle in e["key"].lower()]
        return {"query_type": "event_type", "match_count": len(ev), "events": ev[:40]}

    if qt == "charge_level":
        charge_class = charge.get("class") or charge.get("disposition_charged_class")
        level = _charge_level_from_class(charge_class)
        return {
            "query_type": "charge_level",
            "charge_title": charge.get("charge_title") or charge.get("disposition_charged_offense_title"),
            "offense_category": charge.get("offense_category"),
            "class_info": level,
        }

    if qt == "outcome":
        disp_text = ""
        if disposition:
            disp_text = _normalize(disposition.get("charge_disposition") or disposition.get("disposition") or "")
        if not disp_text:
            for f in fields:
                if "disposition" in str(f["key"]).lower():
                    disp_text = _normalize(f["value"])
                    if disp_text:
                        break

        bucket = _bucket_outcome(disp_text)
        disp_date = timeline.get("disposition_date") or disposition.get("disposition_date")

        return {
            "query_type": "outcome",
            "disposition_text": disp_text or None,
            "outcome_bucket": bucket,
            "disposition_date": disp_date,
            "resolution_fields": [f for f in fields if "disposition" in str(f["key"]).lower()][:25],
        }

    if qt == "actors":
        actor_fields = []
        for f in fields:
            if str(f["key"]) in ACTOR_KEYS:
                actor_fields.append(f)
        if not actor_fields:
            for f in fields:
                k = str(f["key"]).lower()
                if "judge" in k or "court" in k or "agency" in k:
                    actor_fields.append(f)

        if contains_text:
            actor_fields = _find_matches(actor_fields, contains_text)

        return {"query_type": "actors", "match_count": len(actor_fields), "matches": actor_fields[:40]}

    if qt == "find_it":
        needle = (contains_text or "").strip()
        if not needle:
            return {
                "query_type": "find_it",
                "match_count": 0,
                "matches": [],
                "note": "contains_text is required for find_it (e.g., 'bond', 'arraignment', 'John', 'Markham')",
            }

        matches = _find_matches(fields, needle)
        ev_matches = [e for e in events if needle.lower() in e["event_type"].lower() or needle.lower() in e["key"].lower()]
        return {
            "query_type": "find_it",
            "match_count": len(matches) + len(ev_matches),
            "matches": matches[:30],
            "event_matches": ev_matches[:15],
        }

    if qt == "dates":
        fields = [f for f in fields if f["key"] in DATE_KEYS]
    elif qt == "charges":
        fields = [f for f in fields if f["source"] == "charge"]
    elif qt == "disposition":
        fields = [f for f in fields if "disposition" in str(f["key"]).lower()]
    elif qt == "bond":
        fields = [f for f in fields if f["source"] == "bond"]
    elif qt == "stage":
        fields = [f for f in fields if f["source"] in ("stage", "stage_card")]

    after_dt = _parse_dt(after_date) if after_date else None
    before_dt = _parse_dt(before_date) if before_date else None
    if after_dt or before_dt:
        filtered = []
        for f in fields:
            dt = _parse_dt(str(f["value"])) if f["key"] in DATE_KEYS else None
            if dt is None:
                continue
            if after_dt and dt < after_dt:
                continue
            if before_dt and dt > before_dt:
                continue
            filtered.append(f)
        fields = filtered

    if contains_text:
        fields = _find_matches(fields, contains_text)

    return {
        "query_type": qt,
        "match_count": len(fields),
        "matches": fields[:40],
        "events": events[:40] if qt == "all" else None,
    }


# -----------------------------
# Outcome stats tool (unchanged)
# -----------------------------

from stats_service import (
    fetch_dispositions,
    DispositionQuery,
    compute_comparison_stats_for_user_context,
)

_DISP_CACHE: dict[str, Any] = {"rows": None, "fetched_at": None}

from typing import Optional, Dict, Any


def get_outcome_stats(
    *,
    stage_id: Optional[str],
    offense_category: Optional[str] = None,
    charge_class: Optional[str] = None,
) -> Dict[str, Any]:
    if not stage_id:
        return {"skipped": True, "reason": "Missing stage_id"}

    if stage_id not in {"POST_ARRAIGNMENT_EARLY_PRETRIAL", "POST_ARRAIGNMENT_PRETRIAL"}:
        return {
            "skipped": True,
            "reason": "Stats currently supported only for post-arraignment stages.",
            "user_stage_id": stage_id,
        }

    q = DispositionQuery(where="disposition_date IS NOT NULL", limit=50000)
    rows = fetch_dispositions(q)

    stats = compute_comparison_stats_for_user_context(
        all_disposition_rows=rows,
        user_stage_id=stage_id,
        user_offense_category=offense_category,
        user_charge_class=charge_class,
    )
    return stats


# -----------------------------
# NEW: Timeline builder (clean)
# -----------------------------

def build_timeline(context_pack: Dict[str, Any], max_nodes: int = 12) -> Dict[str, Any]:
    stage_label = (context_pack.get("stage") or {}).get("stage_label") or ""
    cs = context_pack.get("case_summary") or {}

    # Timeline can be nested, OR dates might live directly in case_summary
    timeline = cs.get("timeline")
    if not isinstance(timeline, dict) or not timeline:
        timeline = cs if isinstance(cs, dict) else {}

    nodes: List[Dict[str, Any]] = []

    def label_for_key(k: str) -> str:
        if k in EVENT_LABELS:
            return EVENT_LABELS[k]
        # fallback: make "arraignment_date" -> "Arraignment date"
        return k.replace("_", " ").strip().title()

    for key, raw_val in (timeline or {}).items():
        k = str(key)
        if not k.lower().endswith("_date"):
         continue


        dt = _parse_dt(raw_val)
        if not dt:
            continue

        nodes.append({
            "id": k,
            "type": k.upper(),
            "date": dt.date().isoformat(),
            "title": label_for_key(k),
            "subtitle": "",
            "source_refs": [{"source": "case_summary.timeline", "key": k, "value": raw_val}],
        })

    # Sort + cap
    nodes = sorted(nodes, key=lambda n: (n.get("date") or "9999-99-99"))
    if len(nodes) > max_nodes:
        nodes = nodes[:max_nodes]

    now_node_id = nodes[-1]["id"] if nodes else None

    return {
        "stage": stage_label,
        "now_node_id": now_node_id,
        "nodes": nodes,
        "future_placeholders": [
            {
                "id": "typical_next",
                "type": "TYPICAL_STEP",
                "title": "Typical next steps at this stage",
                "subtitle": "General info (not a prediction)",
                "kind": "future_general",
            }
        ],
        "warnings": ["Future steps are general information, not a prediction."],
    }
