"""规则路由器：org/project_type/doc_type/layer 过滤。"""
from __future__ import annotations
from ..models.rule import Rule

class RuleRouter:
    def filter(self, rules: list[Rule], org: str | None = None,
               project_type: str | None = None, doc_type: str | None = None,
               layer: str | None = None) -> list[Rule]:
        result = []
        for r in rules:
            if org and r.org_id != org and not r.group.startswith("Base"): continue
            if project_type and project_type not in r.scope: continue
            if doc_type and doc_type not in r.document_types: continue
            if layer and r.layer != layer: continue
            result.append(r)
        return result
