"""nonnull_checker 测试（079）。"""
from nesma_check_engine.engine.checkers.nonnull_checker import NonnullChecker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document, Sheet

def _rule():
    return Rule(id="R079", item_name="", layer="programmatic",
                document_types=["function_breakdown"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B",
                checker_key="nonnull", checker_params={"sheet_role":"estimate",
                "cols_to_check":["编号","类别","重用程度"]})

def _doc(rows_dict):
    columns = {c:i for i,c in enumerate(rows_dict)}
    n = max(len(v) for v in rows_dict.values())
    data = []
    for r in range(n):
        row = [None]*len(columns)
        for col, vals in rows_dict.items():
            if r < len(vals): row[columns[col]] = vals[r]
        data.append(row)
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns=columns, data_rows=data, meta_rows={})
    return Document(file_path="t.xlsx", doc_type="function_breakdown", sheets=[sheet], paragraphs=[], tables=[])

def test_nonnull_pass():
    r = NonnullChecker().run(_rule(), _doc({"编号":["1","2"],"类别":["ILF","EIF"],"重用程度":["高","低"]}))
    assert r[0].verdict == "pass"

def test_nonnull_fail_empty():
    r = NonnullChecker().run(_rule(), _doc({"编号":["1","2"],"类别":["ILF",None],"重用程度":["高","低"]}))
    assert r[0].verdict == "fail" and "类别" in r[0].evidence

def test_nonnull_whitespace_is_empty():
    r = NonnullChecker().run(_rule(), _doc({"编号":["1","  "],"类别":["ILF","EIF"],"重用程度":["高","低"]}))
    assert r[0].verdict == "fail"
