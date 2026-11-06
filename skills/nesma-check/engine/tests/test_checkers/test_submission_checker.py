"""submission_checker 测试（063-066）。"""
from nesma_check_engine.engine.checkers.submission_checker import SubmissionChecker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document

def _rule(require):
    return Rule(id="R063", item_name="", layer="programmatic",
                document_types=["srs"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B",
                checker_key="submission", checker_params={"require": require})

def _doc(doc_type):
    return Document(file_path=f"t.{doc_type}", doc_type=doc_type)

def test_submission_pass_all_present():
    rule = _rule(["srs","function_breakdown","test_report"])
    docs = [_doc("srs"), _doc("function_breakdown"), _doc("test_report")]
    assert SubmissionChecker().run(rule, docs)[0].verdict == "pass"

def test_submission_fail_missing():
    rule = _rule(["srs","function_breakdown","test_report"])
    docs = [_doc("srs"), _doc("function_breakdown")]
    r = SubmissionChecker().run(rule, docs)[0]
    assert r.verdict == "fail" and "test_report" in r.evidence

def test_submission_fail_multiple_missing():
    rule = _rule(["srs","function_breakdown","test_report","technical_specification"])
    docs = [_doc("srs")]
    r = SubmissionChecker().run(rule, docs)[0]
    assert r.verdict == "fail"
    assert "function_breakdown" in r.evidence
    assert "test_report" in r.evidence
    assert "technical_specification" in r.evidence

def test_submission_single_require():
    rule = _rule(["srs"])
    docs = [_doc("srs")]
    assert SubmissionChecker().run(rule, docs)[0].verdict == "pass"

def test_submission_empty_docs():
    rule = _rule(["srs"])
    r = SubmissionChecker().run(rule, [])[0]
    assert r.verdict == "fail" and "srs" in r.evidence
