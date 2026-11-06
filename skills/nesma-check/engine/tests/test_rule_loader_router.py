"""规则加载与路由测试。"""
from pathlib import Path
from nesma_check_engine.engine.rule_loader import RuleLoader
from nesma_check_engine.engine.rule_router import RuleRouter

CHECKLIST = Path(__file__).parents[2] / "checklist"

def test_loads_all_in_range():
    """规则数用范围断言（155±5，避免硬编码过期）。"""
    n = len(RuleLoader().load_all(CHECKLIST))
    assert 150 <= n <= 160, f"规则数 {n} 超出预期范围"

def test_assigns_org_and_group():
    rules = RuleLoader().load_all(CHECKLIST)
    assert any(r.org_id == "ORG_B" for r in rules)
    assert any(r.group.startswith("Base") for r in rules)

def test_resolves_checker_key():
    rules = RuleLoader().load_all(CHECKLIST)
    prog = [r for r in rules if r.layer == "programmatic" and r.org_id == "ORG_B"
            and "function_breakdown" in r.document_types]
    for r in prog:
        assert r.checker_key is not None or r.needs_semantic, f"{r.id} 未分派"

def test_091_096_needs_semantic():
    rules = RuleLoader().load_all(CHECKLIST)
    assert next(r for r in rules if r.id == "Orgs-ORG_B-Format-091").needs_semantic
    assert next(r for r in rules if r.id == "Orgs-ORG_B-Format-096").needs_semantic

def test_067_070_skipped():
    """067-070 模板合规性：模板不固定，标 needs_semantic=True（skipped）。"""
    rules = RuleLoader().load_all(CHECKLIST)
    for rid in ["Orgs-ORG_B-Format-067","Orgs-ORG_B-Format-068",
                "Orgs-ORG_B-Format-069","Orgs-ORG_B-Format-070"]:
        r = next(r for r in rules if r.id == rid)
        assert r.needs_semantic and r.checker_key is None, f"{rid} 应标 skipped"

def test_097_sheet_role_cost():
    r = next(r for r in RuleLoader().load_all(CHECKLIST) if r.id == "Orgs-ORG_B-Format-097")
    assert r.checker_key == "numeric_relation"
    assert r.checker_params["sheet_role"] == "cost"

def test_router_filter_by_org():
    rules = RuleRouter().filter(RuleLoader().load_all(CHECKLIST), org="ORG_B")
    assert all(r.org_id == "ORG_B" or r.group.startswith("Base") for r in rules)
    assert not any(r.org_id == "ORG_A" for r in rules)

def test_router_filter_by_project_type():
    rules = RuleRouter().filter(RuleLoader().load_all(CHECKLIST), org="ORG_B", project_type="engineering")
    for r in rules: assert "engineering" in r.scope

def test_router_filter_by_doc_type():
    rules = RuleRouter().filter(RuleLoader().load_all(CHECKLIST), org="ORG_B",
                                doc_type="function_breakdown", layer="programmatic")
    for r in rules:
        assert "function_breakdown" in r.document_types
        assert r.layer == "programmatic"

def test_base_always_included():
    rules = RuleRouter().filter(RuleLoader().load_all(CHECKLIST), org="ORG_B")
    assert any(r.group.startswith("Base") for r in rules)

def test_dispatch_has_071_074():
    from nesma_check_engine.engine.rule_loader import DISPATCH
    for rid in ["Orgs-ORG_B-Cross-071", "Orgs-ORG_B-Cross-072",
                "Orgs-ORG_B-Cross-073", "Orgs-ORG_B-Cross-074"]:
        assert rid in DISPATCH, f"{rid} 不在 DISPATCH 表"
        assert DISPATCH[rid][0] == "builtin:cross_doc", f"{rid} 未分派到 builtin:cross_doc"

def test_dispatch_075_skipped():
    from nesma_check_engine.engine.rule_loader import DISPATCH
    entry = DISPATCH.get("Orgs-ORG_B-Cross-075")
    assert entry is not None
    assert entry[0] is None
    assert len(entry) == 3 and entry[2] is True  # needs_semantic=True

def test_071_params_has_mappings():
    from nesma_check_engine.engine.rule_loader import DISPATCH
    params = DISPATCH["Orgs-ORG_B-Cross-071"][1]
    assert "mappings" in params
    assert len(params["mappings"]) == 3
    assert params["modify_type_col"] == "修改类型"

def test_075_loads_as_skipped():
    from nesma_check_engine.engine.rule_loader import RuleLoader
    from pathlib import Path
    checklist = Path(__file__).parents[2] / "checklist"
    rules = RuleLoader().load_all(checklist)
    r075 = next(r for r in rules if r.id == "Orgs-ORG_B-Cross-075")
    assert r075.needs_semantic is True
    assert r075.checker_key is None
