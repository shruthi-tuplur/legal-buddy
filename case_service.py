# service.py
from typing import Any, Dict
from main import fetch_case_by_id, build_llm_context_pack, infer_stage
from llm_client_openai import call_llm_with_context_pack

import os
import subprocess
import time
import requests

import subprocess, time, requests




def explain_case(case_id: str) -> Dict[str, Any]:
    """
    Core pipeline for both CLI and UI.
    Returns JSON-serializable output (no prints).
    """
    case_id = (case_id or "").strip()
    if not case_id:
        raise ValueError("No case ID provided")

    case_data = fetch_case_by_id(case_id)
    if not case_data:
        raise ValueError(f"Case '{case_id}' not found in any dataset")

    # Deterministic stage + context pack
    llm_pack = build_llm_context_pack(case_data)


    print("➡️ About to call LLM...", flush=True)
    llm_text = call_llm_with_context_pack(llm_pack)
    print("✅ LLM returned. Length:", len(llm_text), flush=True)
    print("\n=== LLM RESPONSE ===\n", llm_text, flush=True)


    # Return a clean object for UI rendering
    return {
        "input_id": case_id,
        "case_summary": llm_pack["case_summary"],
        "stage": llm_pack["stage"],
        "llm_response": llm_text,
        # Optional debug fields if you want them in UI:
        # "stage_card": llm_pack["stage_card"],
        # "raw_case_data": case_data,
    }

explain_case("364915353569")