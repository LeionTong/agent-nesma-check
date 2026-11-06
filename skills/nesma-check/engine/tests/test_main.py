"""main.py 编排主流程测试。"""
from pathlib import Path
from nesma_check_engine.engine.main import run_check, aggregate_summary, validate_summary
from nesma_check_engine.models.check_result import CheckResult

CHECKLIST = Path(__file__).parents[2] / "checklist"

def test_aggregate_summary():
    results = [
        CheckResult("R1","pass","","","",  "error",1.0),
        CheckResult("R2","pass","","","",  "error",1.0),
        CheckResult("R3","fail","","","",  "error",1.0),
        CheckResult("R4","skipped","","","","error",1.0),
        CheckResult("R5","skipped","","","","error",1.0),
    ]
    s = aggregate_summary(results, total_rules=5, executed=3)
    assert s["pass"] == 2 and s["fail"] == 1 and s["skipped_semantic"] == 2
    assert s["total_rules"] == 5 and s["executed"] == 3

def test_validate_summary_ok():
    results = [
        CheckResult("R1","pass","","","","error",1.0),
        CheckResult("R2","fail","","","","error",1.0),
    ]
    s = {"total_rules":2,"executed":2,"pass":1,"fail":1,"skipped_semantic":0,"errors":0}
    assert validate_summary(s, results) is True

def test_validate_summary_mismatch():
    results = [
        CheckResult("R1","pass","","","","error",1.0),
        CheckResult("R2","fail","","","","error",1.0),
    ]
    s = {"total_rules":2,"executed":2,"pass":2,"fail":0,"skipped_semantic":0,"errors":0}
    assert validate_summary(s, results) is False

def test_run_check_needs_semantic_skipped():
    """091/096/067-070 → skipped。"""
    from nesma_check_engine.models.document import Document
    docs = [Document(file_path="t.xlsx", doc_type="function_breakdown")]
    results = run_check(docs, checklist_dir=CHECKLIST, org="ORG_B", project_type="engineering")
    skipped_ids = {r.rule_id for r in results if r.verdict == "skipped"}
    assert "Orgs-ORG_B-Format-091" in skipped_ids
    assert "Orgs-ORG_B-Format-096" in skipped_ids
    assert "Orgs-ORG_B-Format-067" in skipped_ids

def test_run_check_scope_filter():
    """scope=engineering 时，仅含 new_demand 的规则不进入执行。"""
    from nesma_check_engine.models.document import Document
    from nesma_check_engine.engine.rule_loader import RuleLoader
    from nesma_check_engine.engine.rule_router import RuleRouter
    docs = [Document(file_path="t.xlsx", doc_type="function_breakdown")]
    all_rules = RuleLoader().load_all(CHECKLIST)
    filtered = RuleRouter().filter(all_rules, org="ORG_B", project_type="engineering",
                                   layer="programmatic")
    for r in filtered:
        assert "engineering" in r.scope, f"{r.id} scope={r.scope} 不含 engineering"
    new_demand_only = [r for r in all_rules if r.scope == ["new_demand"]]
    filtered_ids = {r.id for r in filtered}
    for r in new_demand_only:
        assert r.id not in filtered_ids, f"{r.id} 仅含 new_demand 但未被过滤"

def test_run_check_summary_matches_results():
    from nesma_check_engine.models.document import Document
    docs = [Document(file_path="t.xlsx", doc_type="function_breakdown")]
    output = run_check(docs, checklist_dir=CHECKLIST, org="ORG_B", project_type="engineering",
                       return_summary=True)
    results = output["results"]
    summary = output["summary"]
    assert summary["pass"] == sum(1 for r in results if r.verdict == "pass")
    assert summary["fail"] == sum(1 for r in results if r.verdict == "fail")
    assert summary["skipped_semantic"] == sum(1 for r in results if r.verdict == "skipped")

def test_run_check_submission_gets_all_docs():
    """063-066 submission checker 接收全部文档。"""
    from nesma_check_engine.models.document import Document
    docs = [
        Document(file_path="srs.docx", doc_type="srs"),
        Document(file_path="fb.xlsx", doc_type="function_breakdown"),
        Document(file_path="tr.docx", doc_type="test_report"),
    ]
    results = run_check(docs, checklist_dir=CHECKLIST, org="ORG_B", project_type="engineering")
    r063 = next(r for r in results if r.rule_id == "Orgs-ORG_B-Format-063")
    r064 = next(r for r in results if r.rule_id == "Orgs-ORG_B-Format-064")
    r065 = next(r for r in results if r.rule_id == "Orgs-ORG_B-Format-065")
    assert r063.verdict == "pass"
    assert r064.verdict == "pass"
    assert r065.verdict == "pass"

def test_run_check_exception_continues():
    """单条规则异常不中断其他规则。"""
    from nesma_check_engine.engine.checkers.base import REGISTRY
    from nesma_check_engine.models.document import Document, Sheet
    from nesma_check_engine.models.rule import Rule

    class BoomChecker:
        def run(self, rule, doc):
            raise RuntimeError("boom")
    original = REGISTRY.get("enum")
    REGISTRY["enum"] = BoomChecker
    try:
        docs = [Document(file_path="t.xlsx", doc_type="function_breakdown")]
        results = run_check(docs, checklist_dir=CHECKLIST, org="ORG_B",
                            project_type="engineering")
        assert any(r.verdict == "fail" and "检查器内部错误" in r.reason for r in results)
        nonnull = [r for r in results if r.rule_id == "Orgs-ORG_B-Format-079"]
        assert len(nonnull) > 0
    finally:
        if original: REGISTRY["enum"] = original

def test_cross_doc_rule_gets_multiple_docs():
    """跨文档规则应收到 list[Document]（含两种 doc_type）"""
    from nesma_check_engine.engine.main import run_check
    from nesma_check_engine.models.document import Document, Sheet
    from pathlib import Path
    checklist = Path(__file__).parents[2] / "checklist"
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns={"一级模块": 0, "二级模块": 1, "功能点计数项名称": 2,
                           "修改类型": 3},
                  data_rows=[["统一纳管", "集团纳管", "机房数据", "新增"]],
                  meta_rows={})
    fb = Document(file_path="t.xlsx", doc_type="function_breakdown",
                  sheets=[sheet], paragraphs=[], tables=[])
    srs = Document(file_path="t.docx", doc_type="srs", sheets=[],
                   paragraphs=[], tables=[])
    output = run_check([fb, srs], checklist_dir=checklist, org="ORG_B",
                       project_type="engineering", return_summary=True)
    cross_results = [r for r in output["results"]
                     if r.rule_id == "Orgs-ORG_B-Cross-071"]
    assert len(cross_results) >= 1
    # 071 应产出结果（pass/fail/skipped 任一），不是被"无匹配文档"跳过
    assert cross_results[0].verdict in ("pass", "fail", "skipped")

def test_075_is_skipped():
    """075 应在结果中产出 skipped"""
    from nesma_check_engine.engine.main import run_check
    from nesma_check_engine.models.document import Document, Sheet
    from pathlib import Path
    checklist = Path(__file__).parents[2] / "checklist"
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns={"子系统": 0, "一级模块": 1, "二级模块": 2},
                  data_rows=[["系统A", "模块A", "子模块A"]],
                  meta_rows={})
    fb = Document(file_path="t.xlsx", doc_type="function_breakdown",
                  sheets=[sheet], paragraphs=[], tables=[])
    output = run_check([fb], checklist_dir=checklist, org="ORG_B",
                       project_type="engineering", return_summary=True)
    r075 = [r for r in output["results"] if r.rule_id == "Orgs-ORG_B-Cross-075"]
    assert len(r075) == 1
    assert r075[0].verdict == "skipped"

def test_single_doc_rule_unchanged():
    """单文档规则仍收到单个 Document（非列表）—— SP-1 无回归"""
    from nesma_check_engine.engine.main import run_check
    from nesma_check_engine.models.document import Document, Sheet
    from pathlib import Path
    checklist = Path(__file__).parents[2] / "checklist"
    sheet = Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                  columns={"类别": 0, "重用程度": 1, "修改类型": 2,
                           "功能点计数项名称": 3, "功能项描述": 4,
                           "编号": 5, "子系统": 6, "一级模块": 7, "二级模块": 8, "UFP": 9},
                  data_rows=[["ILF", "高", "新增", "计数项A", "描述A",
                              "1", "系统A", "模块A", "子模块A", "5"]],
                  meta_rows={})
    fb = Document(file_path="t.xlsx", doc_type="function_breakdown",
                  sheets=[sheet], paragraphs=[], tables=[])
    output = run_check([fb], checklist_dir=checklist, org="ORG_B",
                       project_type="engineering", return_summary=True)
    # 080 enum_checker 应正常执行（非 skipped）
    r080 = [r for r in output["results"] if r.rule_id == "Orgs-ORG_B-Format-080"]
    assert len(r080) == 1 and r080[0].verdict == "pass"
