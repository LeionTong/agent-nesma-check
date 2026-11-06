"""Rule 数据模型。"""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Rule:
    id: str
    item_name: str
    layer: str
    document_types: list[str]
    scope: list[str]
    severity: str
    description: str
    pass_criteria: str
    fail_criteria: str
    references: list[str]
    org_id: str
    group: str
    checker_key: str | None = None
    checker_params: dict = field(default_factory=dict)
    needs_semantic: bool = False

    def applies_to(self, doc_type: str, project_type: str) -> bool:
        return doc_type in self.document_types and project_type in self.scope
