from main import infer_stage


def test_infer_stage_unclear_when_insufficient_data():
    case = {}
    stage_id, label, confidence, reasons = infer_stage(case)

    assert stage_id == "PENDING_OR_UNKNOWN"
    assert confidence == "low"
    assert reasons


def test_infer_stage_still_unclear_with_only_arraignment():
    case = {"arraignment_date": "2023-01-10"}
    stage_id, _, _, _ = infer_stage(case)

    assert stage_id == "PENDING_OR_UNKNOWN"


def test_infer_stage_still_unclear_with_only_sentencing():
    case = {"sentencing_date": "2024-05-01"}
    stage_id, _, _, _ = infer_stage(case)

    assert stage_id == "PENDING_OR_UNKNOWN"
