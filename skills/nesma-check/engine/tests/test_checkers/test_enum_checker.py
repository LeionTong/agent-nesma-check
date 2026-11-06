"""enum_checker 测试（080/081/087）。"""
from nesma_check_engine.engine.checkers.enum_checker import EnumChecker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document, Sheet

def _rule(col, values, ci=True):
    return Rule(id="R080", item_name="", layer="programmatic",
                document_types=["function_breakdown"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B",
                checker_key="enum", checker_params={"sheet_role":"estimate","col":col,"values":values,"ci":ci})

def _doc(rows, col="类别"):
    idx = 8
    data = []
    for val in rows:
        row = [None]*15; row[idx] = val; data.append(row)
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns={col: idx}, data_rows=data, meta_rows={})
    return Document(file_path="t.xlsx", doc_type="function_breakdown", sheets=[sheet], paragraphs=[], tables=[])

def test_enum_pass_all_valid():
    assert EnumChecker().run(_rule("类别",["ILF","EIF","EI","EO","EQ"]), _doc(["ILF","EIF","EI","EO","EQ"]))[0].verdict == "pass"

def test_enum_fail_invalid():
    r = EnumChecker().run(_rule("类别",["ILF","EIF"]), _doc(["ILF","ILF1"]))[0]
    assert r.verdict == "fail" and "ILF1" in r.evidence

def test_enum_case_insensitive():
    assert EnumChecker().run(_rule("类别",["ILF","EIF","EI","EO","EQ"],ci=True), _doc(["Eo","ei"]))[0].verdict == "pass"

def test_enum_elf_eif_both():
    assert EnumChecker().run(_rule("类别",["ILF","ELF","EIF","EI","EO","EQ"]), _doc(["ELF","EIF"]))[0].verdict == "pass"

def test_enum_skip_empty():
    assert EnumChecker().run(_rule("类别",["ILF","EIF"]), _doc(["ILF","","EIF"]))[0].verdict == "pass"
