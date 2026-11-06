"""numeric_relation_checker 测试（097）。"""
from nesma_check_engine.engine.checkers.numeric_relation_checker import NumericRelationChecker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document, Sheet

def _rule(expr="C20 - C27 <= C22"):
    return Rule(id="R097", item_name="", layer="programmatic",
                document_types=["function_breakdown"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B",
                checker_key="numeric_relation",
                checker_params={"sheet_role":"cost","expr":expr})

def _doc(meta):
    sheet = Sheet(name="开发费用估算", semantic_role="cost", header_row=-1,
                  columns={}, data_rows=[], meta_rows=meta)
    return Document(file_path="t.xlsx", doc_type="function_breakdown",
                    sheets=[sheet], paragraphs=[], tables=[])

def test_numeric_pass():
    r = NumericRelationChecker().run(_rule(), _doc({"C20":100.0,"C27":10.0,"C22":95.0}))[0]
    assert r.verdict == "pass"

def test_numeric_fail():
    r = NumericRelationChecker().run(_rule(), _doc({"C20":100.0,"C27":10.0,"C22":85.0}))[0]
    assert r.verdict == "fail"
    assert "C20" in r.evidence and "C27" in r.evidence and "C22" in r.evidence

def test_numeric_skipped_no_sheet():
    doc = Document(file_path="t.xlsx", doc_type="function_breakdown",
                   sheets=[], paragraphs=[], tables=[])
    r = NumericRelationChecker().run(_rule(), doc)[0]
    assert r.verdict == "skipped" and "cost" in r.reason

def test_numeric_skipped_missing_coord():
    r = NumericRelationChecker().run(_rule(), _doc({"C20":100.0,"C27":10.0}))[0]
    assert r.verdict == "skipped" and "C22" in r.reason

def test_numeric_fail_non_number():
    r = NumericRelationChecker().run(_rule(), _doc({"C20":"abc","C27":10.0,"C22":95.0}))[0]
    assert r.verdict == "fail" and "无法解析" in r.reason

def test_numeric_int_values():
    r = NumericRelationChecker().run(_rule(), _doc({"C20":100,"C27":10,"C22":95}))[0]
    assert r.verdict == "pass"
