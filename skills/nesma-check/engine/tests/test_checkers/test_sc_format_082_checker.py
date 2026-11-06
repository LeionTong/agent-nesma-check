"""sc_format_082_checker 测试：修改/删除功能重用程度检查。

逻辑：
- 修改类型 ∈ {修改,删除} 且 重用程度 != 高：
  - 功能项描述/备注 含明确比例信号(如"变更字段超过50%") → pass(放行)
  - 无明确比例信号 → skipped(转语义层，不猜测)
- 其他情况 → pass
"""
from nesma_check_engine.engine.checkers.sc_format_082_checker import ScFormat082Checker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document, Sheet

def _rule():
    return Rule(id="R082", item_name="", layer="programmatic",
                document_types=["function_breakdown"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B",
                checker_key="builtin:sc_format_082", checker_params={})

def _doc(rows):
    columns = {"功能项描述":0,"类别":1,"重用程度":2,"修改类型":3,"备注":4}
    data = []
    for desc, reuse, modify, remark in rows:
        data.append([desc, "EI", reuse, modify, remark])
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns=columns, data_rows=data, meta_rows={})
    return Document(file_path="t.xlsx", doc_type="function_breakdown",
                    sheets=[sheet], paragraphs=[], tables=[])

def test_pass_new_high():
    r = ScFormat082Checker().run(_rule(), _doc([("功能A","高","新增","")]))[0]
    assert r.verdict == "pass"

def test_pass_modify_high():
    r = ScFormat082Checker().run(_rule(), _doc([("功能A","高","修改","")]))[0]
    assert r.verdict == "pass"

def test_pass_delete_high():
    r = ScFormat082Checker().run(_rule(), _doc([("功能A","高","删除","")]))[0]
    assert r.verdict == "pass"

def test_skipped_modify_low_no_signal():
    r = ScFormat082Checker().run(_rule(), _doc([("功能A","低","修改","")]))[0]
    assert r.verdict == "skipped" and "语义" in r.reason

def test_skipped_delete_medium_no_signal():
    r = ScFormat082Checker().run(_rule(), _doc([("功能A","中","删除","")]))[0]
    assert r.verdict == "skipped"

def test_pass_modify_low_with_signal_in_desc():
    r = ScFormat082Checker().run(_rule(),
        _doc([("功能A，变更字段超过50%","低","修改","")]))[0]
    assert r.verdict == "pass"

def test_pass_modify_low_with_signal_in_remark():
    r = ScFormat082Checker().run(_rule(),
        _doc([("功能A","低","修改","新增字段占比>50%")]))[0]
    assert r.verdict == "pass"

def test_pass_delete_medium_with_signal_50pct_above():
    r = ScFormat082Checker().run(_rule(),
        _doc([("功能A","中","删除","变更比例50%以上")]))[0]
    assert r.verdict == "pass"

def test_mixed_rows():
    results = ScFormat082Checker().run(_rule(),
        _doc([("功能A","高","新增",""),
              ("功能B","低","修改",""),
              ("功能C","低","修改","变更字段超过50%")]))
    assert len(results) == 2
    assert results[0].verdict == "skipped"
    assert results[1].verdict == "pass"

def test_skipped_no_sheet():
    doc = Document(file_path="t.xlsx", doc_type="function_breakdown",
                   sheets=[], paragraphs=[], tables=[])
    r = ScFormat082Checker().run(_rule(), doc)[0]
    assert r.verdict == "skipped" and "estimate" in r.reason
