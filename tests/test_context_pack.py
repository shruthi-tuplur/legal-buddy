from main import build_llm_context_pack

def test_context_pack_contains_required_fields():
    case = {
        "case_id": "123",
        "arraignment_date": "2023-01-01"
    }

    pack = build_llm_context_pack(case)

    assert "stage" in pack
    assert "case_summary" in pack
    assert isinstance(pack["case_summary"], dict)
