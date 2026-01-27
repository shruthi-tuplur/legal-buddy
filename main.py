#!/usr/bin/env python3
"""
Cook County Case Analyzer
Counts open cases and fetches random cases
"""

import requests
import random
from datetime import datetime

print("LOADED main.py")




# API endpoints
INTAKE_URL = "https://datacatalog.cookcountyil.gov/resource/3k7z-hchi.json"
INITIATION_URL = "https://datacatalog.cookcountyil.gov/resource/7mck-ehwz.json"
DISPOSITION_URL = "https://datacatalog.cookcountyil.gov/resource/apwk-dzx8.json"
SENTENCING_URL = "https://datacatalog.cookcountyil.gov/resource/tg8v-tm6u.json"

def count_open_cases():
    """Count how many cases are open."""
    print("\n" + "="*70)
    print("COUNTING OPEN CASES")
    print("="*70 + "\n")
    
    print("Step 1: Counting total initiated cases...")
    params = {"$query": "SELECT COUNT(*) AS count"}
    
    try:
        response = requests.get(INITIATION_URL, params=params, timeout=30)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            initiated_total = int(list(data[0].values())[0])
        else:
            print("  ❌ Could not get initiation count")
            return None
        print(f"  ✓ Total initiated cases: {initiated_total:,}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None
    
    print("\nStep 2: Counting total dispositions...")
    try:
        response = requests.get(DISPOSITION_URL, params=params, timeout=30)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            disposition_total = int(list(data[0].values())[0])
        else:
            print("  ❌ Could not get disposition count")
            return None
        print(f"  ✓ Total dispositions: {disposition_total:,}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None
    
    open_cases = initiated_total - disposition_total
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\nTotal initiated cases:  {initiated_total:>10,}")
    print(f"Total dispositions:     {disposition_total:>10,}")
    print(f"                        {'-'*11}")
    print(f"Estimated open cases:   {open_cases:>10,}")
    print(f"\nPercentage open:        {(open_cases/initiated_total*100):>9.1f}%")
    print("\n" + "="*70 + "\n")
    
    return {
        "initiated": initiated_total,
        "disposed": disposition_total,
        "open": open_cases,
        "open_percentage": (open_cases/initiated_total*100)
    }

def fetch_random_open_case():
    """Fetch a random OPEN case (one that has no disposition)."""
    print("Finding random OPEN cases...")
    
    max_attempts = 5  # Try up to 5 times to find an open case
    
    for attempt in range(1, max_attempts + 1):
        print(f"  Attempt {attempt}/{max_attempts}...")
        
        # Fetch a batch of cases
        params = {
            "$limit": 50,
            "$offset": random.randint(0, 100000)
        }
        
        response = requests.get(INITIATION_URL, params=params, timeout=30)
        cases = response.json()
        
        if not cases:
            continue
        
        # Check each case to see if it's open (no disposition)
        for case in cases:
            case_participant_id = case.get('case_participant_id')
            
            if not case_participant_id:
                continue
            
            # Check if this case has a disposition
            disp_params = {"case_participant_id": case_participant_id, "$limit": 1}
            disp_response = requests.get(DISPOSITION_URL, params=disp_params, timeout=30)
            disposition = disp_response.json()
            
            # If no disposition found, this case is OPEN!
            if not disposition:
                print(f"✓ Found an open case!\n")
                return case
    
    print("❌ Could not find an open case after several attempts")
    return None

def format_date(date_string):
    """Make dates readable."""
    if not date_string:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_string

def format_money(amount):
    """Make money readable."""
    if not amount:
        return "N/A"
    try:
        return f"${float(amount):,.0f}"
    except:
        return amount

def print_case(case):
    """Print the case nicely."""
    print("="*70)
    print("COOK COUNTY INTAKE CASE")
    print("="*70)
    
    print(f"\n📋 CASE INFO:")
    print(f"  Case ID:              {case.get('case_id', 'N/A')}")
    print(f"  Participant ID:       {case.get('case_participant_id', 'N/A')}")
    
    print(f"\n⚖️  CHARGE:")
    print(f"  Title:                {case.get('charge_offense_title', 'N/A')}")
    print(f"  Category:             {case.get('offense_category', 'N/A')}")
    print(f"  Class:                {case.get('class', 'N/A')}")
    
    print(f"\n👤 DEFENDANT:")
    print(f"  Age:                  {case.get('age_at_incident', 'N/A')} years old")
    print(f"  Race:                 {case.get('race', 'N/A')}")
    print(f"  Gender:               {case.get('gender', 'N/A')}")
    
    print(f"\n📅 DATES:")
    print(f"  Incident:             {format_date(case.get('incident_begin_date'))}")
    print(f"  Arrest:               {format_date(case.get('arrest_date'))}")
    print(f"  Arraignment:          {format_date(case.get('arraignment_date'))}")
    
    print(f"\n💰 BOND:")
    print(f"  Type:                 {case.get('bond_type_initial', 'N/A')}")
    print(f"  Amount:               {format_money(case.get('bond_amount_initial'))}")
    
    print(f"\n📍 LOCATION:")
    print(f"  City:                 {case.get('incident_city', 'N/A')}")
    print(f"  Police:               {case.get('law_enforcement_agency', 'N/A')}")
    
    print(f"\n✅ REVIEW:")
    print(f"  Result:               {case.get('felony_review_result', 'N/A')}")
    
    print(f"\n{'='*70}\n")

def fetch_case_by_id(search_id):
    """Fetch a case by ID, trying both case_id and case_participant_id."""
    print(f"\n{'='*70}")
    print(f"FETCHING CASE: {search_id}")
    print(f"{'='*70}\n")
    
    case_data = {}
    
    # 1. Intake
    print("Step 1: Checking Intake dataset...")
    try:
        params = {"case_participant_id": search_id}
        response = requests.get(INTAKE_URL, params=params, timeout=30)
        intake = response.json()
        
        if not intake:
            params = {"case_id": search_id}
            response = requests.get(INTAKE_URL, params=params, timeout=30)
            intake = response.json()
        
        if intake:
            case_data['intake'] = intake[0]
            print(f"  ✓ Found in Intake")
        else:
            print(f"  ✗ Not found in Intake")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 2. Initiation
    print("Step 2: Checking Initiation dataset...")
    try:
        params = {"case_participant_id": search_id}
        response = requests.get(INITIATION_URL, params=params, timeout=30)
        initiation = response.json()
        
        if not initiation:
            params = {"case_id": search_id}
            response = requests.get(INITIATION_URL, params=params, timeout=30)
            initiation = response.json()
        
        if initiation:
            case_data['initiation'] = initiation[0]
            print(f"  ✓ Found in Initiation")
        else:
            print(f"  ✗ Not found in Initiation")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 3. Disposition
    print("Step 3: Checking Disposition dataset...")
    try:
        params = {"case_participant_id": search_id}
        response = requests.get(DISPOSITION_URL, params=params, timeout=30)
        disposition = response.json()
        
        if not disposition:
            params = {"case_id": search_id}
            response = requests.get(DISPOSITION_URL, params=params, timeout=30)
            disposition = response.json()
        
        if disposition:
            case_data['disposition'] = disposition[0]
            print(f"  ✓ Found in Disposition (CLOSED)")
        else:
            print(f"  ✗ Not found in Disposition (OPEN)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # 4. Sentencing
    print("Step 4: Checking Sentencing dataset...")
    try:
        params = {"case_participant_id": search_id}
        response = requests.get(SENTENCING_URL, params=params, timeout=30)
        sentencing = response.json()
        
        if not sentencing:
            params = {"case_id": search_id}
            response = requests.get(SENTENCING_URL, params=params, timeout=30)
            sentencing = response.json()
        
        if sentencing:
            case_data['sentencing'] = sentencing[0]
            print(f"  ✓ Found in Sentencing")
        else:
            print(f"  ✗ Not found in Sentencing")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    
    if not case_data:
        print(f"❌ Case {search_id} not found in any dataset.\n")
        return None
    
    return case_data


def fetch_latest_case():
    """Fetch the most recent case from the dataset."""
    print("Fetching most recent case...")
    
    # Fetch the latest case by ordering by case_id descending
    params = {
        "$limit": 1,
        "$order": "case_id DESC"
    }
    
    try:
        response = requests.get(INITIATION_URL, params=params, timeout=30)
        records = response.json()
        
        if records:
            case = records[0]
            print(f"✓ Got the latest case!\n")
            
            # Show when it was filed
            if case.get('arraignment_date'):
                print(f"  This case was arraigned on: {format_date(case.get('arraignment_date'))}")
            
            return case
        else:
            print("❌ No records found")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

import json
from datetime import datetime

# Stage cards as structured objects (NOT printed directly by Python)
STAGE_CARDS = {
    "PRE_ARRAIGNMENT": {
        "title": "Pre-Arraignment",
        "where_you_are": "Case has been filed and charges are formal. Arraignment is scheduled but has not yet occurred.",
        "what_this_means": [
            "The case has been formally filed in court",
            "A case number has been assigned",
            "Bond has been set",
            "First court appearance (arraignment) is upcoming"
        ],
        "what_usually_happens_next": [
            "Arraignment occurs (judge reads charges, defendant enters plea)",
            "Bond status is confirmed or modified",
            "Pre-trial conference dates are scheduled",
            "Discovery process begins after arraignment"
        ],
        "what_not_yet": [
            "Arraignment has not occurred",
            "No plea has been entered",
            "Discovery has not begun",
            "No trial date set"
        ],
        "data_limits": "Public dataset includes arraignment date but may not show all bond modifications or upcoming hearing dates."
    },
    
    "POST_ARRAIGNMENT_EARLY_PRETRIAL": {
        "title": "Early Pre-Trial",
        "where_you_are": "Arraignment has occurred. Case is in early pre-trial phase.",
        "what_this_means": [
            "Defendant has been arraigned and entered a plea",
            "Discovery process is beginning or underway",
            "Pre-trial conferences are scheduled",
            "Case is in negotiation and evidence review phase"
        ],
        "what_usually_happens_next": [
            "Pre-trial conferences occur regularly",
            "Discovery materials are exchanged",
            "Defense may file motions",
            "Plea negotiations typically begin",
            "Case progresses toward resolution or trial"
        ],
        "what_not_yet": [
            "Plea negotiations are early or just beginning",
            "No trial date set yet",
            "Case has not reached resolution"
        ],
        "data_limits": "Public dataset shows case is open but does not include upcoming court dates, plea offers, or motion activity."
    },
    
    # Updated STAGE_CARDS entry for POST_ARRAIGNMENT_PRETRIAL only
    
    # Updated STAGE_CARDS entry for POST_ARRAIGNMENT_PRETRIAL
"POST_ARRAIGNMENT_PRETRIAL": {
    "title": "Pretrial (post-arraignment)",
    "where_you_are": "Case is post-arraignment. This is the pretrial phase where cases typically move through discovery, scheduling, and case discussions and scheduling.",
    "what_this_means": [
        "Arraignment has occurred",
        "Case is in the pretrial phase of the court process",
        "This phase typically involves discovery (evidence sharing) and court scheduling",
        "Pretrial conferences are commonly used for status updates and next steps"
    ],
    "what_usually_happens_next": [
        "Pretrial conferences are often scheduled periodically to track progress",
        "Discovery materials may be exchanged between parties",
        "Defense may file motions related to evidence or procedure",
        "Some cases resolve during pretrial; others continue toward trial scheduling",
        "This phase can include multiple steps over time, depending on the case"
    ],
    "what_not_yet": [
        "Final resolution has not occurred",
        "No disposition recorded",
        "Case outcome has not been determined"
    ],
    "data_limits": "Public dataset shows case is open but does not include upcoming court dates, motion filings, or negotiation status.",
    "common_questions": [
        "What is the pretrial phase?",
        "What are pretrial conferences?",
        "What is discovery?",
        "How long does pretrial typically last?",
        "What happens during this phase in general?"
    ]

    
},
    
    "PENDING_OR_UNKNOWN": {
    "title": "Stage Unclear",
    "where_you_are": "Charges are listed in this dataset but key event dates are not available.",
    "what_this_means": [
        "Case number and participant ID are assigned",
        "Charges are entered into the system",
        "Arraignment date is not shown in this public dataset",
        "Exact procedural stage cannot be determined from available fields"
    ],
    "what_usually_happens_next": [
        "A court event date (like arraignment) may appear later in the record depending on dataset coverage",
        "If an arraignment date becomes available, the stage inference can update",
        "Other hearing types may occur but not be visible in this dataset",
        "A disposition field may appear later if the dataset includes closure information"
    ],
    "what_not_yet": [
        "Exact stage cannot be confirmed from data",
        "Upcoming court dates are not visible",
        "Disposition has not been recorded"
    ],
    "data_limits": "Arraignment date and felony review outcome are missing. Public datasets can omit fields due to publication practices, data entry timing, or coverage gaps."
},
    
    "CASE_CLOSED": {
        "title": "Case Closed",
        "where_you_are": "Case has been resolved. Disposition is recorded.",
        "what_this_means": [
            "Case is no longer open or pending",
            "Resolution has been reached (plea, trial verdict, or dismissal)",
            "Sentencing has occurred or is scheduled",
            "Pre-trial activity has concluded"
        ],
        "what_usually_happens_next": [
            "If convicted, sentence terms are carried out",
            "If dismissed or acquitted, case is concluded",
            "Appeals are possible but are separate proceedings"
        ],
        "what_not_yet": [
            "Case is concluded",
            "No further pre-trial proceedings"
        ],
        "data_limits": "Disposition is recorded. Sentencing details may or may not appear in this public dataset."
    }
}

def format_date(date_string):
    """Make dates readable."""
    if not date_string or date_string == 'N/A':
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_string

def format_money(amount):
    """Make money readable."""
    if not amount or amount == 'N/A':
        return "N/A"
    try:
        return f"${float(amount):,.0f}"
    except:
        return amount

def infer_stage(case_data):
    """
    Infer the case stage from available data.
    Returns: (stage_id, stage_label, confidence, reasons)
    """
    has_intake = 'intake' in case_data
    has_initiation = 'initiation' in case_data
    has_disposition = 'disposition' in case_data
    has_sentencing = 'sentencing' in case_data
    
    reasons = []
    
    # Check for closed case
    if has_sentencing:
        return ("CASE_CLOSED", "Sentencing Complete", "high", 
                ["Sentencing record present", "Case fully resolved"])
    
    if has_disposition:
        return ("CASE_CLOSED", "Case Closed - Disposition Recorded", "high",
                ["Disposition record present", "Case resolved"])
    
    # Check for open case with initiation
    if has_initiation:
        init = case_data['initiation']
        arraignment_date = init.get('arraignment_date')
        
        if arraignment_date and arraignment_date != 'N/A':
            try:
                arraignment_dt = datetime.fromisoformat(arraignment_date.replace('Z', '+00:00'))
                days_since = (datetime.now(arraignment_dt.tzinfo) - arraignment_dt).days
                
                if days_since < 0:
                    return ("PRE_ARRAIGNMENT", "Pre-Arraignment", "high",
                            [f"Arraignment scheduled for {format_date(arraignment_date)}",
                             "Arraignment has not occurred yet"])
                elif days_since < 30:
                    conf = "high" if days_since <= 180 else "medium"
                    return ("POST_ARRAIGNMENT_EARLY_PRETRIAL", "Early Pre-Trial", conf,
                            ["Arraignment date is present in the dataset",
                            "No disposition is recorded in this dataset"])
                else:
                    # For older cases without recent event data, use medium confidence
                    conf = "high" if days_since <= 180 else "medium"
                    return ("POST_ARRAIGNMENT_PRETRIAL", "Pretrial (post-arraignment)", conf,
                            ["Arraignment date is present in the dataset",
             "No disposition is recorded in this dataset"])
            except:
                reasons.append("Arraignment date present but unparseable")
        else:
            reasons.append("Arraignment date not present in dataset")
            reasons.append("Charges are listed in the record, but key event dates are missing so the stage is unclear")
        
        return ("PENDING_OR_UNKNOWN", "Stage Unclear", "medium", reasons)
    
    # Only intake data
    if has_intake:
        return ("PENDING_OR_UNKNOWN", "Intake Stage Only", "low",
                ["Only intake data present", "Case may not be formally filed"])
    
    return ("PENDING_OR_UNKNOWN", "Unknown", "low", ["Insufficient data"])


def build_llm_context_pack(case_data):
    """
    Build machine-readable payload for LLM consumption.
    Returns dict with case summary, stage inference, stage card, and safety flags.
    """
    has_intake = 'intake' in case_data
    has_initiation = 'initiation' in case_data
    has_disposition = 'disposition' in case_data
    has_sentencing = 'sentencing' in case_data
    
    # Get primary data source
    if has_initiation:
        primary = case_data['initiation']
    elif has_intake:
        primary = case_data['intake']
    else:
        primary = {}
    
    # Build case summary
    missing_fields = []
    
    # Case IDs
    case_id = primary.get('case_id', 'N/A')
    participant_id = primary.get('case_participant_id', 'N/A')
    
    # Charge info
    charge_title = primary.get('charge_offense_title', 'N/A')
    offense_category = primary.get('offense_category', 'N/A')
    charge_class = primary.get('class', 'N/A')
    statute = f"{primary.get('chapter', '')}/{primary.get('act', '')}/{primary.get('section', '')}"
    
    # Timeline
    incident_date = primary.get('incident_begin_date', 'N/A')
    arrest_date = primary.get('arrest_date', 'N/A')
    received_date = primary.get('received_date', 'N/A')
    felony_review_date = primary.get('felony_review_date', 'N/A')
    felony_review_result = primary.get('felony_review_result', 'N/A')
    arraignment_date = primary.get('arraignment_date', 'N/A')
    
    days_since_arraignment = None
    if arraignment_date and arraignment_date != 'N/A':
        try:
            arr_dt = datetime.fromisoformat(arraignment_date.replace('Z', '+00:00'))
            days_since_arraignment = (datetime.now(arr_dt.tzinfo) - arr_dt).days
            if days_since_arraignment < 0:
                days_since_arraignment = None
        except:
            pass
    
    # Bond info
    bond_type = primary.get('bond_type_current', 'N/A')
    bond_amount = primary.get('bond_amount_current', 'N/A')
    bond_date = primary.get('bond_date_current', 'N/A')
    
    bond_explanation = None
    if bond_type and bond_type != 'N/A':
        if 'D Bond' in bond_type or 'D-Bond' in bond_type:
            bond_explanation = "D-Bond = 10% deposit bond. Defendant pays 10% of bond amount to be released."
        elif 'I Bond' in bond_type or 'I-Bond' in bond_type:
            bond_explanation = "I-Bond = Individual Recognizance. Released on promise to appear."
        elif 'No Bail' in bond_type:
            bond_explanation = "No Bail = Held without bond, cannot be released."
    
    # Track missing fields
    if arraignment_date == 'N/A':
        missing_fields.append("arraignment_date")
    if felony_review_result == 'N/A':
        missing_fields.append("felony_review_result")
    if bond_type == 'N/A':
        missing_fields.append("bond_type")
    if bond_amount == 'N/A':
        missing_fields.append("bond_amount")
    
    # Disposition info (if closed)
    disposition_info = None
    if has_disposition:
        disp = case_data['disposition']
        disposition_info = {
            "disposition_type": disp.get('charge_disposition', 'N/A'),
            "disposition_date": format_date(disp.get('disposition_date')),
            "explanation": None
        }
        
        disp_type = disp.get('charge_disposition', '')
        if 'Plea' in disp_type and 'Guilty' in disp_type:
            disposition_info['explanation'] = "Defendant pleaded guilty (plea deal, no trial)."
        elif 'Finding' in disp_type and 'Guilty' in disp_type:
            disposition_info['explanation'] = "Defendant found guilty at trial."
        elif 'Finding' in disp_type and 'Not Guilty' in disp_type:
            disposition_info['explanation'] = "Defendant found not guilty (acquitted)."
        elif 'Nolle Prosequi' in disp_type or 'Nol Pros' in disp_type:
            disposition_info['explanation'] = "State's Attorney dropped charges (dismissed)."
    
    # Sentencing info (if present)
    sentencing_info = None
    if has_sentencing:
        sent = case_data['sentencing']
        sentencing_info = {
            "sentence_type": sent.get('sentence_type', 'N/A'),
            "commitment_term": sent.get('commitment_term', 'N/A'),
            "commitment_unit": sent.get('commitment_unit', 'N/A'),
            "sentence_date": format_date(sent.get('sentence_date')),
            "explanation": None
        }
        
        sent_type = sent.get('sentence_type', '')
        if 'Prison' in sent_type:
            sentencing_info['explanation'] = "Prison = Illinois Department of Corrections (state prison)."
        elif 'Jail' in sent_type:
            sentencing_info['explanation'] = "Jail = County jail (typically less than 1 year)."
        elif 'Probation' in sent_type:
            sentencing_info['explanation'] = "Probation = Supervised release with conditions."
        elif 'Conditional Discharge' in sent_type:
            sentencing_info['explanation'] = "Conditional Discharge = Released with conditions, no probation officer."
    
    # Infer stage
    stage_id, stage_label, confidence, reasons = infer_stage(case_data)
    
    # Build payload
    payload = {
        "case_summary": {
            "case_id": case_id,
            "participant_id": participant_id,
            "charge": {
                "offense_category": offense_category,
                "charge_title": charge_title,
                "class": charge_class,
                "statute": statute
            },
            "timeline": {
                "incident_date": format_date(incident_date),
                "arrest_date": format_date(arrest_date),
                "received_date": format_date(received_date),
                "felony_review_date": format_date(felony_review_date),
                "felony_review_result": felony_review_result,
                "arraignment_date": format_date(arraignment_date),
                "days_since_arraignment": days_since_arraignment
            },
            "bond": {
                "bond_type": bond_type,
                "bond_amount": format_money(bond_amount),
                "bond_date": format_date(bond_date),
                "bond_explanation": bond_explanation
            },
            "disposition": disposition_info,
            "sentencing": sentencing_info,
            "missing_fields": missing_fields
        },
        "stage": {
            "stage_id": stage_id,
            "stage_label": stage_label,
            "confidence": confidence,
            "reasons": reasons
        },
        "stage_card": STAGE_CARDS.get(stage_id, STAGE_CARDS["PENDING_OR_UNKNOWN"]),
        "safety": {
            "no_legal_advice": True,
            "do_not_speculate": True,
            "no_outcome_predictions": True
        }
    }
    
    return payload

def print_case_analysis_for_user(case_data):
    """
    Print factual case analysis section only.
    Does NOT print narrative explanations (those are for LLM to generate).
    """
    has_intake = 'intake' in case_data
    has_initiation = 'initiation' in case_data
    has_disposition = 'disposition' in case_data
    has_sentencing = 'sentencing' in case_data
    
    print("\n" + "="*70)
    print("CASE ANALYSIS FOR USER")
    print("="*70 + "\n")
    
    # Infer stage
    stage_id, stage_label, confidence, reasons = infer_stage(case_data)
    
    print("CURRENT CASE STAGE:")
    print(f"  {stage_label}")
    if has_disposition or has_sentencing:
        print("  This case has been resolved.")
    elif stage_id == "PENDING_OR_UNKNOWN":
        print("  The case appears active, but this dataset does not include enough event history to confirm the exact stage.")
    else:
        print("  This case is open and has not been resolved.")
    print()
    
    # CASE IDENTIFIERS
    print("CASE IDENTIFIERS:")
    if has_intake:
        print(f"  Case ID:              {case_data['intake'].get('case_id', 'N/A')}")
        print(f"  Participant ID:       {case_data['intake'].get('case_participant_id', 'N/A')}")
    elif has_initiation:
        print(f"  Case ID:              {case_data['initiation'].get('case_id', 'N/A')}")
        print(f"  Participant ID:       {case_data['initiation'].get('case_participant_id', 'N/A')}")
    print()
    
    # CHARGE INFORMATION
    print("CHARGE INFORMATION:")
    if has_initiation:
        init = case_data['initiation']
        # Try multiple fields to find charge title
        charge_title = (init.get('charge_offense_title') or 
                    init.get('primary_charge_flag') or 
                    init.get('charge_title', 'N/A'))
        print(f"  Charge Title:         {charge_title}")
        print(f"  Offense Category:     {init.get('offense_category', 'N/A')}")
        print(f"  Class:                {init.get('class', 'N/A')} (Felony)")
        print(f"  Statute:              {init.get('chapter', '')}/{init.get('act', '')}/{init.get('section', '')}")
    
    print()
    
    
    # TIMELINE
    print("TIMELINE OF EVENTS:")
    if has_intake:
        intake = case_data['intake']
        print(f"  Incident Date:        {format_date(intake.get('incident_begin_date'))}")
        print(f"  Arrest Date:          {format_date(intake.get('arrest_date'))}")
        print(f"  Received by SA:       {format_date(intake.get('received_date'))}")
        print(f"  Felony Review Date:   {format_date(intake.get('felony_review_date'))}")
        
        review_result = intake.get('felony_review_result', 'N/A')
        print(f"  Felony Review Result: {review_result}")
        
        if review_result == 'Rejected':
            print("\n  NOTE: Case was REJECTED at felony review.")
            print("  This means the State's Attorney declined to prosecute.")
        elif review_result == 'Approved':
            print("\n  NOTE: Case was APPROVED at felony review.")
            print("  This means the State's Attorney decided to prosecute.")
    
    if has_initiation:
        init = case_data['initiation']
        arraignment_date = init.get('arraignment_date')
        print(f"  Arraignment Date:     {format_date(arraignment_date)}")
        
    
    if has_disposition:
        disp = case_data['disposition']
        print(f"  Disposition Date:     {format_date(disp.get('disposition_date'))}")
        
        if has_initiation:
            init = case_data['initiation']
            if init.get('arraignment_date') and disp.get('disposition_date'):
                try:
                    arr_dt = datetime.fromisoformat(init.get('arraignment_date').replace('Z', '+00:00'))
                    disp_dt = datetime.fromisoformat(disp.get('disposition_date').replace('Z', '+00:00'))
                    case_length = (disp_dt - arr_dt).days
                    #print(f"  Total Case Length:    {case_length} days from arraignment to disposition")
                except:
                    pass
    
    if has_sentencing:
        sent = case_data['sentencing']
        print(f"  Sentencing Date:      {format_date(sent.get('sentence_date'))}")
    
    print()
    
    # BOND INFORMATION (if open)
    if has_initiation and not has_disposition:
        print("BOND INFORMATION:")
        init = case_data['initiation']
        bond_type = init.get('bond_type_current', 'N/A')
        bond_amount = init.get('bond_amount_current', 'N/A')
        bond_date = init.get('bond_date_current', 'N/A')
        
        print(f"  Bond Type:            {bond_type}")
        print(f"  Bond Amount:          {format_money(bond_amount)}")
        print(f"  Bond Date:            {format_date(bond_date)}")
        
        if bond_type and bond_type != 'N/A':
            if 'D Bond' in bond_type or 'D-Bond' in bond_type:
                print("\n  BOND EXPLANATION:")
                print("  D-Bond = 10% deposit bond. Defendant pays 10% of bond amount to be released.")
            elif 'I Bond' in bond_type or 'I-Bond' in bond_type:
                print("\n  BOND EXPLANATION:")
                print("  I-Bond = Individual Recognizance. Released on promise to appear.")
            elif 'No Bail' in bond_type:
                print("\n  BOND EXPLANATION:")
                print("  No Bail = Held without bond, cannot be released.")
        print()
    
    # DISPOSITION (if closed)
    if has_disposition:
        print("DISPOSITION (HOW CASE WAS RESOLVED):")
        disp = case_data['disposition']
        print(f"  Disposition Type:     {disp.get('charge_disposition', 'N/A')}")
        print(f"  Disposition Date:     {format_date(disp.get('disposition_date'))}")
        
        disp_type = disp.get('charge_disposition', '')
        if 'Plea' in disp_type and 'Guilty' in disp_type:
            print("\n  DISPOSITION EXPLANATION:")
            print("  Defendant pleaded guilty (plea deal, no trial).")
        elif 'Finding' in disp_type and 'Guilty' in disp_type:
            print("\n  DISPOSITION EXPLANATION:")
            print("  Defendant found guilty at trial.")
        elif 'Finding' in disp_type and 'Not Guilty' in disp_type:
            print("\n  DISPOSITION EXPLANATION:")
            print("  Defendant found not guilty (acquitted).")
        elif 'Nolle Prosequi' in disp_type or 'Nol Pros' in disp_type:
            print("\n  DISPOSITION EXPLANATION:")
            print("  State's Attorney dropped charges (dismissed).")
        print()
    
    # SENTENCING (if present)
    if has_sentencing:
        print("SENTENCING INFORMATION:")
        sent = case_data['sentencing']
        print(f"  Sentence Type:        {sent.get('sentence_type', 'N/A')}")
        print(f"  Commitment Term:      {sent.get('commitment_term', 'N/A')} {sent.get('commitment_unit', '')}")
        
        sent_type = sent.get('sentence_type', '')
        if 'Prison' in sent_type:
            print("\n  SENTENCE EXPLANATION:")
            print("  Prison = Illinois Department of Corrections (state prison).")
        elif 'Jail' in sent_type:
            print("\n  SENTENCE EXPLANATION:")
            print("  Jail = County jail (typically less than 1 year).")
        elif 'Probation' in sent_type:
            print("\n  SENTENCE EXPLANATION:")
            print("  Probation = Supervised release with conditions.")
        elif 'Conditional Discharge' in sent_type:
            print("\n  SENTENCE EXPLANATION:")
            print("  Conditional Discharge = Released with conditions, no probation officer.")
        print()
    
    # STAGE INFERENCE
    print("="*70)
    print(f"STAGE INFERENCE: {stage_id} ({stage_label}) [confidence={confidence}]")
    print("="*70)
    print("\nREASONS:")
    for reason in reasons:
        print(f"  • {reason}")
    print("\n" + "="*70 + "\n")




def cli_lookup_case():
    from llm_client_openai import call_llm_with_context_pack
    llm_response = call_llm_with_context_pack(llm_pack)

    """Interactive case lookup."""
    print("\n" + "="*70)
    print("CASE LOOKUP")
    print("="*70 + "\n")
    
    case_id = input("Enter case ID or participant ID: ").strip()
    
    if not case_id:
        print("❌ No ID entered\n")
        return
    
    case_data = fetch_case_by_id(case_id)
    
    if case_data:
    # 1) Print factual analysis
        print_case_analysis_for_user(case_data)

        # 2) Build context pack
        llm_pack = build_llm_context_pack(case_data)

        # Optional debug
        # print("\nLLM_CONTEXT_PACK_JSON:")
        # print(json.dumps(llm_pack, indent=2, ensure_ascii=False))

        # 3) Call the LLM to generate the calming explanation
        print("\n=== LLM RESPONSE ===\n")
        llm_response = call_llm_with_context_pack(llm_pack)
        print("TYPE:", type(llm_response))
        print("RAW:", repr(llm_response))
        print("\n=== LLM RESPONSE ===\n", llm_response)



# Main program
if __name__ == "__main__":
    print("\n" + "="*70)
    print("COOK COUNTY CASE ANALYZER")
    print("="*70)
    
    print("\nWhat would you like to do?")
    print("  1. Count open cases")
    print("  2. Fetch random OPEN case")
    print("  3. Look up specific case by ID")
    print("  4. Fetch latest case")  # NEW OPTION
    
    choice = input("\nChoice (1-4): ").strip()
    
    if choice == "1":
        results = count_open_cases()
    
    elif choice == "2":
        case = fetch_random_open_case()
        if case:
            print_case(case)
    
    elif choice == "3":
        cli_lookup_case()
    
    elif choice == "4":  # NEW
        case = fetch_latest_case()
        if case:
            print_case(case)
    
    else:
        print("Invalid choice")
    
    print("\n✓ Done!\n")

    import json

#with open("llm_context_pack.json", "w", encoding="utf-8") as f:
    #json.dump(payload, f, indent=2, ensure_ascii=False)
