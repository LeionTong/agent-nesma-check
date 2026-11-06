"""规则加载器：YAML加载+校验+检查器分派。直接吃现有格式，不改 checklist。"""
from __future__ import annotations
from pathlib import Path
import yaml
from ..models.rule import Rule
from ..utils.logger import get_logger

_logger = get_logger("rule_loader")

DISPATCH: dict[str, tuple] = {
    "Orgs-ORG_B-Format-063": ("submission", {"require": ["srs"]}),
    "Orgs-ORG_B-Format-064": ("submission", {"require": ["function_breakdown"]}),
    "Orgs-ORG_B-Format-065": ("submission", {"require": ["test_report"]}),
    "Orgs-ORG_B-Format-066": ("submission", {"require": ["technical_specification"]}),
    "Orgs-ORG_B-Format-067": (None, {}, True),
    "Orgs-ORG_B-Format-068": (None, {}, True),
    "Orgs-ORG_B-Format-069": (None, {}, True),
    "Orgs-ORG_B-Format-070": (None, {}, True),
    "Orgs-ORG_B-Format-079": ("nonnull", {"sheet_role": "estimate",
        "cols_to_check": ["编号","子系统","一级模块","二级模块","功能项描述",
                          "功能点计数项名称","类别","UFP","重用程度","修改类型"]}),
    "Orgs-ORG_B-Format-080": ("enum", {"sheet_role": "estimate", "col": "类别",
        "values": ["ILF","ELF","EIF","EI","EO","EQ"], "ci": True}),
    "Orgs-ORG_B-Format-081": ("enum", {"sheet_role": "estimate", "col": "重用程度",
        "values": ["低","中","高"]}),
    "Orgs-ORG_B-Format-087": ("enum", {"sheet_role": "estimate", "col": "修改类型",
        "values": ["新增","修改","删除"]}),
    "Orgs-ORG_B-Format-093": ("unique", {"sheet_role": "estimate", "col": "功能点计数项名称"}),
    "Orgs-ORG_B-Format-095": ("unique", {"sheet_role": "estimate", "col": "功能项描述"}),
    "Orgs-ORG_B-Format-097": ("numeric_relation", {"sheet_role": "cost", "expr": "C20 - C27 <= C22"}),
    "Orgs-ORG_B-Format-082": ("builtin:sc_format_082", {}),
    "Orgs-ORG_B-Format-091": (None, {}, True),
    "Orgs-ORG_B-Format-096": (None, {}, True),
    # SP-2 跨文档规则 071-075
    "Orgs-ORG_B-Cross-071": ("builtin:cross_doc", {
        "section_path": None,
        "mappings": [
            {"col": "一级模块", "expected_level": 3, "level_tolerance": 1},
            {"col": "二级模块", "expected_level": 4, "level_tolerance": 1},
            {"col": "功能点计数项名称", "expected_level": 6, "level_tolerance": 2},
        ],
        "modify_type_col": "修改类型",
        "function_type_field": "功能类型",
    }),
    "Orgs-ORG_B-Cross-072": ("builtin:cross_doc", {
        "section_path": None,
        "mappings": [
            {"col": "新需求名称", "expected_level": 1, "level_tolerance": 0},
            {"col": "一级模块", "expected_level": 4, "level_tolerance": 1},
            {"col": "二级模块", "expected_level": 5, "level_tolerance": 1},
            {"col": "功能点计数项名称", "expected_level": 6, "level_tolerance": 2},
        ],
        "modify_type_col": "修改类型",
        "function_type_field": "功能类型",
    }),
    "Orgs-ORG_B-Cross-073": ("builtin:cross_doc", {
        "section_path": "测试结果",
        "mappings": [
            {"col": "一级模块", "expected_level": 3, "level_tolerance": 1},
            {"col": "二级模块", "expected_level": 4, "level_tolerance": 1},
            {"col": "功能点计数项名称", "mode": "exists"},
        ],
    }),
    "Orgs-ORG_B-Cross-074": ("builtin:cross_doc", {
        "section_path": None,
        "mappings": [
            {"col": "新需求名称", "expected_level": 1, "level_tolerance": 0},
            {"col": "功能点计数项名称", "expected_level": 2, "level_tolerance": 1},
        ],
    }),
    "Orgs-ORG_B-Cross-075": (None, {}, True),  # 无技术规范书模板，skipped
}

KNOWN_DOC_TYPES = {"srs","function_breakdown","test_report","technical_specification","spds","demand_review_form","ppt"}
KNOWN_SEVERITIES = {"error","warning","info"}
KNOWN_LAYERS = {"programmatic","semantic"}

class RuleLoadError(Exception): pass

class RuleLoader:
    def load_all(self, checklist_dir: Path) -> list[Rule]:
        checklist_dir = Path(checklist_dir)
        if not checklist_dir.is_dir():
            raise RuleLoadError(f"checklist 目录不存在: {checklist_dir}")
        rules = []
        for f in sorted(checklist_dir.glob("*.yaml")):
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            group = data.get("group", "")
            org_id = data.get("org_id", "")
            for raw in data.get("rules", []):
                rules.append(self._build(raw, group, org_id))
        self._validate(rules)
        _logger.info("加载 %d 条规则", len(rules))
        return rules

    def _build(self, raw: dict, group: str, org_id: str) -> Rule:
        rule = Rule(id=raw["id"], item_name=raw.get("item_name",""), layer=raw["layer"],
                    document_types=raw.get("document_types",[]), scope=raw.get("scope",[]),
                    severity=raw.get("severity","error"), description=raw.get("description",""),
                    pass_criteria=raw.get("pass_criteria",""), fail_criteria=raw.get("fail_criteria",""),
                    references=raw.get("references",[]), org_id=org_id, group=group)
        rule.checker_key, rule.checker_params, rule.needs_semantic = self._resolve(rule)
        return rule

    def _resolve(self, rule: Rule) -> tuple[str | None, dict, bool]:
        entry = DISPATCH.get(rule.id)
        if entry is None:
            return (None, {}, True) if rule.layer == "programmatic" else (None, {}, False)
        return entry if len(entry) == 3 else (entry[0], entry[1], False)

    def _validate(self, rules: list[Rule]):
        for r in rules:
            if not r.id: raise RuleLoadError("规则缺少 id")
            if r.layer not in KNOWN_LAYERS: raise RuleLoadError(f"{r.id}: layer 非法")
            for dt in r.document_types:
                if dt not in KNOWN_DOC_TYPES: raise RuleLoadError(f"{r.id}: doc_type 非法 '{dt}'")
            if r.severity not in KNOWN_SEVERITIES: raise RuleLoadError(f"{r.id}: severity 非法")
            if r.layer == "programmatic" and r.checker_key is None and not r.needs_semantic:
                raise RuleLoadError(f"{r.id}: 程序化规则未分派且未标记 needs_semantic")
