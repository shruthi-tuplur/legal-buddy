from main import build_llm_context_pack
import pytest

def test_context_pack_contains_required_fields():
    case = {
        "case_id": "123",
        "arraignment_date": "2023-01-01"
    }

    pack = build_llm_context_pack(case)

    assert "stage" in pack
    assert "case_summary" in pack
    assert isinstance(pack["case_summary"], dict)

# Verifying that build_llm_context_pack correctly wires infer_stage output into the payload
def test_build_llm_context_pack_happy_path(monkeypatch):

    case_data = {
            "initiation": {
                "case_id": "123"
            }
        }
    
    # monkeypatching infer stage to return fake data
    monkeypatch.setattr(
        "main.infer_stage",
        lambda data: ("id", "label", "confidence", "reasons")
    )

    pack = build_llm_context_pack(case_data)

    assert pack["stage"]["stage_label"] == "label"
    assert pack["case_summary"]["case_id"] == "123"


# Testing result if build_llm_context_pack receives empty input
def test_build_llm_context_pack_empty_input(monkeypatch):

    case_data = {}

    # monkeypatching infer stage to return fake data
    monkeypatch.setattr(
        "main.infer_stage",
        lambda data: ("id", "label", "confidence", "reasons")
    )

    pack = build_llm_context_pack(case_data)

    assert pack["case_summary"]["case_id"] == "N/A"

    # Testing result if internal failure occurs via infer_stage, e.g. function does not return expected data 
    def test_build_llm_context_pack_internal_failure(monkeypatch):
        case_data = {
            "initiation": {
                "case_id": "123"
            }
        }

        # monkeypatching infer_stage to return incomplete fake data
        monkeypatch.setattr(
            "main.infer_stage",
            lambda data: ("id", "label", "confidence")
        )

        

        # asserting that with internal failure, function returns ValueError
        with pytest.raises(ValueError):
            build_llm_context_pack(case_data)


