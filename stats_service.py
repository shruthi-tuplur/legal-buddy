# stats_service.py
# v1: build a comparison cohort from Cook County disposition rows and compute simple outcome stats.
# - Uses the public dispositions endpoint: https://datacatalog.cookcountyil.gov/resource/apwk-dzx8.json
# - No ML/regression yet: deterministic stats first (counts, percentages, time-to-disposition)
#
# Major upgrades:
# (2) server-side filtering using Socrata $where (smaller + faster)
# (3) in-process caching per cohort key
# (4) graceful fallback on timeouts / API hiccups (no crashing chat)
# (5) Socrata app token supported via SOCRATA_APP_TOKEN (already in your code)

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Tuple
import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DISPOSITIONS_ENDPOINT = "https://datacatalog.cookcountyil.gov/resource/apwk-dzx8.json"

# -------------------------
# (3) Simple in-process cache
# -------------------------
# Keyed by: (stage_id, offense_category_lower, charge_class)
_COMPARISON_STATS_CACHE: Dict[Tuple[str, str, str], Dict[str, Any]] = {}


# -------------------------
# Requests session w/ retries
# -------------------------

def _requests_session_with_retries() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=4,
        backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


# -------------------------
# Helpers: parsing / mapping
# -------------------------

def _parse_iso_date(s: Optional[str]) -> Optional[datetime]:
    """Parse dates like '2014-12-17T00:00:00.000' safely."""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        try:
            return datetime.strptime(s[:10], "%Y-%m-%d")
        except Exception:
            return None


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _escape_socrata_string(s: str) -> str:
    # Basic escaping for single quotes in Socrata $where
    return s.replace("'", "''")


def map_outcome_bucket(charge_disposition: Optional[str]) -> str:
    """Conservative mapping from raw charge_disposition to outcome buckets."""
    cd = _norm(charge_disposition)
    if not cd:
        return "other_or_unknown"

    if "nolle" in cd or "nol pros" in cd or "dismiss" in cd or "stricken" in cd:
        return "dismissed_or_nolle"
    if "not guilty" in cd or "acquit" in cd:
        return "acquitted"
    if "guilty" in cd or "convict" in cd or "judgment" in cd:
        return "convicted"
    if "plea" in cd:
        return "plea"

    return "other_or_unknown"


# -------------------------
# Stage “reached” logic
# -------------------------

SUPPORTED_STAGE_IDS_FOR_STATS = {
    "POST_ARRAIGNMENT_EARLY_PRETRIAL",
    "POST_ARRAIGNMENT_PRETRIAL",
}

def reached_stage(row: Dict[str, Any], user_stage_id: str) -> bool:
    """
    Decide whether a closed disposition row indicates that case reached the user's stage.
    v1 logic:
    - For post-arraignment stages: require arraignment_date present.
    - Otherwise: return False (unsupported for cohort filtering).
    """
    if user_stage_id in SUPPORTED_STAGE_IDS_FOR_STATS:
        return bool(row.get("arraignment_date"))
    return False


# -------------------------
# Fetch dispositions (Socrata)
# -------------------------

@dataclass
class DispositionQuery:
    where: Optional[str] = None
    limit: int = 50000
    timeout_sec: int = 60


def fetch_dispositions(query: DispositionQuery) -> List[Dict[str, Any]]:
    """
    Fetch rows from the dispositions endpoint with Socrata pagination.
    Uses retries and a (connect, read) timeout.
    """
    headers = {}
    token = os.getenv("SOCRATA_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token

    session = _requests_session_with_retries()

    all_rows: List[Dict[str, Any]] = []
    offset = 0

    while True:
        params = {"$limit": query.limit, "$offset": offset}
        if query.where:
            params["$where"] = query.where

        resp = session.get(
            DISPOSITIONS_ENDPOINT,
            params=params,
            headers=headers,
            timeout=(10, query.timeout_sec),
        )

        # If the API returns a non-200 with retries exhausted, raise here
        resp.raise_for_status()

        chunk = resp.json()
        if not chunk:
            break

        all_rows.extend(chunk)
        if len(chunk) < query.limit:
            break

        offset += query.limit

    return all_rows


# -------------------------
# Cohort + stats computation
# -------------------------

def _time_to_disposition_days(row: Dict[str, Any]) -> Optional[int]:
    disp = _parse_iso_date(row.get("disposition_date"))
    if not disp:
        return None

    start = (
        _parse_iso_date(row.get("received_date"))
        or _parse_iso_date(row.get("arrest_date"))
        or _parse_iso_date(row.get("incident_begin_date"))
        or _parse_iso_date(row.get("arraignment_date"))
    )
    if not start:
        return None

    days = int((disp - start).days)
    return days if days >= 0 else None


def _percent_dict(counts: Counter) -> Dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        return {}
    return {k: round((v / total) * 100.0, 1) for k, v in counts.items()}


def _quantiles(sorted_vals: List[int]) -> Dict[str, Optional[float]]:
    if not sorted_vals:
        return {"p25": None, "median": None, "p75": None}

    def pick(p: float) -> float:
        idx = int(round(p * (len(sorted_vals) - 1)))
        return float(sorted_vals[idx])

    return {"p25": pick(0.25), "median": pick(0.50), "p75": pick(0.75)}


def build_cohort_definition(
    *,
    user_stage_id: str,
    offense_category: Optional[str],
    charge_class: Optional[str],
) -> Dict[str, Any]:
    return {
        "closed_only": True,
        "user_stage_id": user_stage_id,
        "require_reached_same_stage": True,
        "offense_category": offense_category,
        "disposition_charged_class": charge_class,
    }


def filter_similar_closed_rows(
    rows: Iterable[Dict[str, Any]],
    *,
    user_stage_id: str,
    offense_category: Optional[str],
    charge_class: Optional[str],
) -> List[Dict[str, Any]]:
    """
    Python-side filtering still stays for safety because:
    - Socrata data can be messy
    - we also enforce reached_stage here
    """
    oc_norm = _norm(offense_category) if offense_category else ""
    cls_norm = (charge_class or "").strip()

    cohort: List[Dict[str, Any]] = []
    for r in rows:
        if not r.get("disposition_date"):
            continue

        if oc_norm:
            if _norm(r.get("offense_category")) != oc_norm and _norm(r.get("updated_offense_category")) != oc_norm:
                continue

        if cls_norm:
            if (r.get("disposition_charged_class") or "").strip() != cls_norm:
                continue

        if not reached_stage(r, user_stage_id):
            continue

        cohort.append(r)

    return cohort


def compute_comparison_stats(
    rows: List[Dict[str, Any]],
    *,
    user_stage_id: str,
    offense_category: Optional[str],
    charge_class: Optional[str],
) -> Dict[str, Any]:
    cohort = filter_similar_closed_rows(
        rows,
        user_stage_id=user_stage_id,
        offense_category=offense_category,
        charge_class=charge_class,
    )

    outcome_counts = Counter(map_outcome_bucket(r.get("charge_disposition")) for r in cohort)

    raw_disp_counts = Counter((_norm(r.get("charge_disposition")) or "unknown") for r in cohort)
    top_raw_dispositions = [{"label": label, "count": count} for label, count in raw_disp_counts.most_common(8)]

    ttd = [_time_to_disposition_days(r) for r in cohort]
    ttd = [x for x in ttd if isinstance(x, int)]
    ttd.sort()
    q = _quantiles(ttd)

    return {
        "cohort_definition": build_cohort_definition(
            user_stage_id=user_stage_id,
            offense_category=offense_category,
            charge_class=charge_class,
        ),
        "sample_size": len(cohort),
        "outcomes_pct": _percent_dict(outcome_counts),
        "outcomes_counts": dict(outcome_counts),
        "top_raw_dispositions": top_raw_dispositions,
        "time_to_disposition_days": {
            "n": len(ttd),
            **q,
        },
    }


# -------------------------
# (2) Build a tight Socrata $where for a user's cohort
# -------------------------

def build_disposition_where_clause(
    *,
    offense_category: Optional[str],
    charge_class: Optional[str],
    require_arraignment_date: bool,
) -> str:
    """
    Server-side filter to reduce payload:
    - closed only
    - optionally offense_category OR updated_offense_category
    - optionally disposition_charged_class
    - optionally require arraignment_date (post-arraignment cohort)
    """
    parts = ["disposition_date IS NOT NULL"]

    if require_arraignment_date:
        parts.append("arraignment_date IS NOT NULL")

    if offense_category:
        oc = _escape_socrata_string(offense_category.strip())
        parts.append(
            f"(lower(offense_category) = lower('{oc}') OR lower(updated_offense_category) = lower('{oc}'))"
        )

    if charge_class:
        cc = _escape_socrata_string(charge_class.strip())
        parts.append(f"disposition_charged_class = '{cc}'")

    return " AND ".join(parts)


# -------------------------
# (2)(3)(4) One call for /chat: cached + filtered + safe
# -------------------------

def compute_comparison_stats_for_user_context(
    *,
    user_stage_id: str,
    user_offense_category: Optional[str],
    user_charge_class: Optional[str],
) -> Dict[str, Any]:
    """
    Friendly wrapper so your /chat code is tiny.
    - Uses server-side filtering
    - Caches by cohort key
    - Gracefully returns {"skipped": True, ...} on timeout/API issues
    """
    stage_id = user_stage_id or ""
    oc_key = (user_offense_category or "").strip().lower()
    cls_key = (user_charge_class or "").strip()
    cache_key = (stage_id, oc_key, cls_key)

    if cache_key in _COMPARISON_STATS_CACHE:
        return _COMPARISON_STATS_CACHE[cache_key]

    # Only compute stats for supported stages
    if user_stage_id not in SUPPORTED_STAGE_IDS_FOR_STATS:
        result = {
            "skipped": True,
            "reason": "Stats are currently supported only for post-arraignment stages.",
            "user_stage_id": user_stage_id,
        }
        _COMPARISON_STATS_CACHE[cache_key] = result
        return result

    where = build_disposition_where_clause(
        offense_category=user_offense_category,
        charge_class=user_charge_class,
        require_arraignment_date=True,
    )

    try:
        rows = fetch_dispositions(DispositionQuery(where=where, limit=50000, timeout_sec=60))
        result = compute_comparison_stats(
            rows,
            user_stage_id=user_stage_id,
            offense_category=user_offense_category,
            charge_class=user_charge_class,
        )
    except requests.exceptions.RequestException as e:
        # (4) graceful fallback – do not crash chat
        result = {
            "skipped": True,
            "reason": f"Dispositions endpoint error: {type(e).__name__}",
            "hint": "Public data portals sometimes rate-limit or stall. Try again in a moment.",
        }
    except Exception as e:
        result = {
            "skipped": True,
            "reason": f"Stats computation failed: {type(e).__name__}",
        }

    _COMPARISON_STATS_CACHE[cache_key] = result
    return result
