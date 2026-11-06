"""编排主流程：加载→路由→提取→检查→聚合→校验。"""
from __future__ import annotations
from pathlib import Path
from ..models.rule import Rule
from ..models.document import Document
from ..models.check_result import CheckResult
from ..utils.logger import get_logger
from .rule_loader import RuleLoader
from .rule_router import RuleRouter
from .checkers.base import REGISTRY
from . import checkers  # noqa: F401 — 触发注册

_logger = get_logger("main")

def aggregate_summary(results: list[CheckResult], total_rules: int, executed: int) -> dict:
    return {
        "total_rules": total_rules,
        "executed": executed,
        "pass": sum(1 for r in results if r.verdict == "pass"),
        "fail": sum(1 for r in results if r.verdict == "fail"),
        "skipped_semantic": sum(1 for r in results if r.verdict == "skipped"),
        "errors": sum(1 for r in results if "检查器内部错误" in r.reason),
    }

def validate_summary(summary: dict, results: list[CheckResult]) -> bool:
    actual = aggregate_summary(results, summary["total_rules"], summary["executed"])
    for k in ("pass","fail","skipped_semantic","errors"):
        if summary.get(k) != actual.get(k):
            _logger.error("summary 校验失败: %s=%s 实际=%s", k, summary.get(k), actual.get(k))
            return False
    return True

def run_check(documents: list[Document], checklist_dir: Path,
              org: str = "ORG_B", project_type: str = "engineering",
              return_summary: bool = False) -> list[CheckResult] | dict:
    rules = RuleLoader().load_all(checklist_dir)
    rules = RuleRouter().filter(rules, org=org, project_type=project_type,
                                layer="programmatic")
    total_rules = len(rules)
    results: list[CheckResult] = []
    executed = 0
    for rule in rules:
        if rule.needs_semantic:
            results.append(CheckResult(rule_id=rule.id, verdict="skipped", location="",
                evidence="", reason="规则无可编程精确阈值，下沉语义层(SP-4)",
                severity=rule.severity, confidence=1.0))
            continue
        executed += 1
        try:
            checker_cls = REGISTRY.get(rule.checker_key)
            if checker_cls is None:
                results.append(CheckResult(rule_id=rule.id, verdict="fail", location="",
                    evidence="", reason=f"检查器内部错误: 未注册 checker_key={rule.checker_key}",
                    severity=rule.severity, confidence=0.0))
                continue
            checker = checker_cls()
            matched = [d for d in documents if d.doc_type in rule.document_types]
            distinct_types = set(d.doc_type for d in matched)
            if len(distinct_types) >= 2:
                docs_for_rule = matched
            elif matched:
                docs_for_rule = matched[0]
            else:
                docs_for_rule = None
            if docs_for_rule is None:
                results.append(CheckResult(rule_id=rule.id, verdict="skipped", location="",
                    evidence="", reason=f"无匹配文档类型: {rule.document_types}",
                    severity=rule.severity, confidence=1.0))
                continue
            rule_results = checker.run(rule, docs_for_rule)
            results.extend(rule_results)
        except Exception as e:
            _logger.error("规则 %s 执行异常: %s", rule.id, e)
            results.append(CheckResult(rule_id=rule.id, verdict="fail", location="",
                evidence="", reason=f"检查器内部错误: {e}",
                severity=rule.severity, confidence=0.0))
    if not return_summary:
        return results
    summary = aggregate_summary(results, total_rules, executed)
    if not validate_summary(summary, results):
        _logger.error("summary 自校验失败，终止")
        raise RuntimeError("summary 自校验失败")
    return {"results": results, "summary": summary, "documents": documents,
            "total_rules": total_rules}
