"""unique_checker 测试（093/095）。"""
from nesma_check_engine.engine.checkers.unique_checker import UniqueChecker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document, Sheet

def _rule(col):
    return Rule(id="R093", item_name="", layer="programmatic",
                document_types=["function_breakdown"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B",
                checker_key="unique", checker_params={"sheet_role":"estimate","col":col})

def _doc(values, col="功能点计数项名称"):
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns={col:0}, data_rows=[[v] for v in values], meta_rows={})
    return Document(file_path="t.xlsx", doc_type="function_breakdown", sheets=[sheet], paragraphs=[], tables=[])

def test_unique_pass():
    assert UniqueChecker().run(_rule("功能点计数项名称"), _doc(["A","B","C"]))[0].verdict == "pass"

def test_unique_fail_dup():
    r = UniqueChecker().run(_rule("功能点计数项名称"), _doc(["A","B","A"]))[0]
    assert r.verdict == "fail" and "A" in r.evidence

def test_unique_case_insensitive():
    assert UniqueChecker().run(_rule("功能点计数项名称"), _doc(["功能A"," 功能a "]))[0].verdict == "fail"

def test_unique_reason_mentions_sp4():
    r = UniqueChecker().run(_rule("功能点计数项名称"), _doc(["A","A"]))[0]
    assert "SP-4" in r.reason or "相似度" in r.reason
