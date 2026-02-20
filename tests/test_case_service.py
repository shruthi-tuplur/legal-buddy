from case_service import explain_case
import pytest


def test_explain_case_happy_path(monkeypatch):
    
    # monkeypatching function that fetches case by id
    monkeypatch.setattr(
        "case_service.fetch_case_by_id",
        lambda cid: {"case_id": cid}
    )

    monkeypatch.setattr(
        "case_service.build_llm_context_pack",
         lambda data: {
             "case_summary": "case summary",
             "stage": "current stage"
         }   
    )

    # monkeypatching function that feeds in context pack to llm and gets llm response
    monkeypatch.setattr(
        "case_service.call_llm_with_context_pack",
        lambda pack: "LLM response"
    )

    result = explain_case("123")

    assert result["input_id"] == "123"
    assert result["llm_response"] == "LLM response"
    assert result["case_summary"] == "case summary"
    assert result["stage"] == "current stage"


def test_explain_case_no_case_id():
    with pytest.raises(ValueError, match = "No case ID provided"):
        explain_case("")


def test_explain_case_whitespace_case_id():
    with pytest.raises(ValueError, match = "No case ID provided"):
        explain_case("      ")


def test_explain_case_case_not_found(monkeypatch):
    # first replacing the real fetch function with a fake that always returns None
    monkeypatch.setattr("case_service.fetch_case_by_id", lambda cid: None)

    # now testing to make sure that any time "if not case data = True", ValueError is raised
    with pytest.raises(ValueError, match = "not found"):
        explain_case("123")


def test_explain_case_context_pack_none(monkeypatch):

    # monkeypatching function that fetches case by id
    monkeypatch.setattr(
        "case_service.fetch_case_by_id",
        lambda cid: {"case_id": cid}
    )

    # monkeypatching function that builds llm context pack to make it return None
    monkeypatch.setattr(
        "case_service.build_llm_context_pack",
        lambda data: None
    )

    # asserting that explain_case raises TypeError in this case
    with pytest.raises(TypeError):
        explain_case("123")


def test_explain_case_llm_raises_exception(monkeypatch):

    # monkeypatching function that fetches case by id
    monkeypatch.setattr(
        "case_service.fetch_case_by_id",
        lambda cid: {"case_id": cid}
    )

    # monkeypatching function that builds llm context pack
    monkeypatch.setattr(
        "case_service.build_llm_context_pack",
         lambda data: {
             "case_summary": "case summary",
             "stage": "current stage"
         }   
    )

    def fake_llm(pack):
        raise Exception("LLM down")

    # monkeypatching function that calls llm with context pack
    monkeypatch.setattr(
        "case_service.call_llm_with_context_pack",
        fake_llm
    )

    # asserting that explain_case raises Exception in this case
    with pytest.raises(Exception):
        explain_case("123")