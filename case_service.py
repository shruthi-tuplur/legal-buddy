# service.py
from typing import Any, Dict
from main import fetch_case_by_id, build_llm_context_pack, infer_stage
from llm_client_openai import call_llm_with_context_pack

import os
import subprocess
import time
import requests

import subprocess, time, requests



# --------------------------------------------------------------------------------------------------------------------------------------------
# main service function - the core service function that runs the full Legal Buddy pipeline 

def explain_case(case_id: str) -> Dict[str, Any]:
    """
    Core pipeline for both CLI and UI.
    Returns JSON-serializable output (no prints).
    """

    case_id = (case_id or "").strip()   # input validation to make sure a case ID was provided
    if not case_id:
        raise ValueError("No case ID provided")
    

    case_data = fetch_case_by_id(case_id)   # fetches case data from public datasets using fetch_case_by_id
    if not case_data:
        raise ValueError(f"Case '{case_id}' not found in any dataset")

    # builds structured context pack including things like case summary, charge, timeline, stage inference, stage explanation card, etc
    # this is what gets sent to the model
    llm_pack = build_llm_context_pack(case_data)    

    llm_text = call_llm_with_context_pack(llm_pack)     # calls the LLM with context pack as input to generate plain-language case explanation 
    

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

explain_case("364915353569") # test call