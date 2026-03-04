from main import infer_stage


# happy path: open case with arraignment date, no disposition
def test_infer_stage_happy_path():
    case_data = {
        "initiation": {
            "arraignment_date": "2024-01-01"
        }
    }

    stage_id, label, confidence, reasons = infer_stage(case_data)

    assert stage_id in ["POST_ARRAIGNMENT_EARLY_PRETRIAL", "POST_ARRAIGNMENT_PRETRIAL"]
    assert "Pre-Trial" in label or "Pretrial" in label
    assert confidence in ["high", "medium"]


# closed case via disposition
def test_infer_stage_closed_case_disposition():
    case_data = {
        "disposition": {
            "charge_disposition": "Plea Guilty"
        }
    }

    stage_id, label, confidence, reasons = infer_stage(case_data)

    assert stage_id == "CASE_CLOSED"
    assert confidence == "high"


# closed case via sentencing
def test_infer_stage_closed_case_sentencing():
    case_data = {
        "sentencing": {
            "sentence_type": "Prison"
        }
    }

    stage_id, label, confidence, reasons = infer_stage(case_data)

    assert stage_id == "CASE_CLOSED"
    assert confidence == "high"


# insufficient data
def test_infer_stage_unclear_when_insufficient_data():
    case_data = {}

    stage_id, label, confidence, reasons = infer_stage(case_data)

    assert stage_id == "PENDING_OR_UNKNOWN"
    assert confidence == "low"
    assert reasons


# initiation present but no arraignment date
def test_infer_stage_pending_when_no_arraignment():
    case_data = {
        "initiation": {}
    }

    stage_id, label, confidence, reasons = infer_stage(case_data)

    assert stage_id == "PENDING_OR_UNKNOWN"
    assert confidence in ["medium", "low"]
    assert reasons