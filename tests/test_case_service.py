from case_service import explain_case


def test_explain_case_happy_path(monkeypatch):
    monkeypatch.setattr(
        "case_service.fetch_case_by_id",
        lambda cid: {"case_id": cid}
    )
    monkeypatch.setattr(
        "case_service.call_llm_with_context_pack",
        lambda pack: "LLM response"
    )

    result = explain_case("123")

    assert result["input_id"] == "123"
    assert result["llm_response"] == "LLM response"
