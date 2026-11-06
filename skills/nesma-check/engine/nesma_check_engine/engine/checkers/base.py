"""BaseChecker 契约 + 注册装饰器。"""
from __future__ import annotations
from abc import ABC, abstractmethod
from ...models.rule import Rule
from ...models.document import Document, Sheet
from ...models.check_result import CheckResult
from ...utils.location import LocationAnchor

class BaseChecker(ABC):
    @abstractmethod
    def run(self, rule: Rule, document: Document | list[Document]) -> list[CheckResult]: ...

    def _find_sheet(self, document: Document, sheet_role: str) -> Sheet | None:
        for s in document.sheets:
            if s.semantic_role == sheet_role: return s
        return None

    def _pass(self, rule: Rule, reason: str = "") -> CheckResult:
        return CheckResult(rule_id=rule.id, verdict="pass", location="", evidence="",
                           reason=reason, severity=rule.severity, confidence=1.0)

    def _fail(self, rule: Rule, locations: list[LocationAnchor], evidence: str, reason: str) -> CheckResult:
        loc = "; ".join(l.to_str() for l in locations) if locations else ""
        return CheckResult(rule_id=rule.id, verdict="fail", location=loc,
                           evidence=evidence, reason=reason, severity=rule.severity, confidence=1.0)

    def _skipped(self, rule: Rule, reason: str) -> CheckResult:
        return CheckResult(rule_id=rule.id, verdict="skipped", location="", evidence="",
                           reason=reason, severity=rule.severity, confidence=1.0)

REGISTRY: dict[str, type[BaseChecker]] = {}

def register(key: str):
    def decorator(cls):
        REGISTRY[key] = cls
        return cls
    return decorator
