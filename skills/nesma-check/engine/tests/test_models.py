"""数据模型测试。"""
import json
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import (
    Document, Sheet, Paragraph, Table, SectionNode)
from nesma_check_engine.utils.location import LocationAnchor
from nesma_check_engine.models.check_result import CheckResult

def test_rule_applies_to():
    rule = Rule(id="R001", item_name="测试", layer="programmatic",
                document_types=["function_breakdown"], scope=["engineering","new_demand"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B")
    assert rule.applies_to("function_breakdown", "engineering") is True
    assert rule.applies_to("srs", "engineering") is False

def test_location_anchor_xlsx():
    loc = LocationAnchor(doc_type="function_breakdown", sheet="规模估算", row=6, col="类别")
    assert loc.to_str() == "[规模估算] 行6; 列[类别]"

def test_location_anchor_docx():
    loc = LocationAnchor(doc_type="srs", section="3.2 功能描述", para_idx=12)
    assert loc.to_str() == "§3.2 功能描述 #P12"

def test_sheet_to_dict_roundtrip():
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns={"编号":0,"类别":7}, data_rows=[["1","ILF"]], meta_rows={"C2":448})
    sheet2 = Sheet.from_dict(sheet.to_dict())
    assert sheet2.name == sheet.name
    assert sheet2.columns == sheet.columns

def test_section_node_find():
    root = SectionNode(title="root", level=0, start_para=0, end_para=100, children=[
        SectionNode(title="3", level=1, start_para=5, end_para=50, children=[
            SectionNode(title="3.2 功能描述", level=2, start_para=10, end_para=30, children=[])])])
    found = root.find("3/3.2 功能描述")
    assert found is not None
    assert found.start_para == 10

def test_section_node_no_headings():
    assert SectionNode(title="x", level=1, start_para=0, end_para=1, children=[])

def test_document_to_dict_roundtrip():
    doc = Document(file_path="t.xlsx", doc_type="function_breakdown",
                   sheets=[Sheet(name="s1", semantic_role="estimate", header_row=1,
                                 columns={"a":0}, data_rows=[], meta_rows={})],
                   paragraphs=[], tables=[], section_tree=None)
    doc2 = Document.from_dict(doc.to_dict())
    assert doc2.doc_type == doc.doc_type
    assert doc2.sheets[0].name == "s1"

def test_check_result_to_dict():
    r = CheckResult(rule_id="R001", verdict="fail", location="[规模估算] 行6",
                    evidence="值='ILF1'", reason="非法类别", severity="error", confidence=1.0)
    d = r.to_dict()
    assert d["verdict"] == "fail"
    assert json.dumps(d, ensure_ascii=False)
