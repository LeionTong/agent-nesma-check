"""nonnull_checker（079）：必填列非空。"""
from __future__ import annotations
from ...models.rule import Rule
from ...models.document import Document
from ...models.check_result import CheckResult
from ...utils.location import LocationAnchor
from .base import BaseChecker, register

def _is_empty(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())

@register("nonnull")
class NonnullChecker(BaseChecker):
    def run(self, rule: Rule, document: Document | list[Document]) -> list[CheckResult]:
        if isinstance(document, list): document = document[0]
        sheet = self._find_sheet(document, rule.checker_params["sheet_role"])
        if sheet is None:
            return [self._skipped(rule, f"未找到 sheet_role={rule.checker_params['sheet_role']}")]
        cols = rule.checker_params["cols_to_check"]
        misses = []
        for col in cols:
            ci = sheet.columns.get(col)
            if ci is None:
                misses.append((col, None, None))
                continue
            for ri, row in enumerate(sheet.data_rows):
                if ci < len(row) and _is_empty(row[ci]):
                    misses.append((col, sheet.header_row + 1 + ri, sheet.name))
        if not misses:
            return [self._pass(rule)]
        locs = [LocationAnchor(doc_type=document.doc_type, sheet=m[2], row=m[1], col=m[0])
                for m in misses if m[1] is not None]
        evidence = "; ".join(f"{m[0]} 行{m[1]} 为空" for m in misses if m[1] is not None)
        for m in misses:
            if m[1] is None: evidence += f"; 列 '{m[0]}' 不存在"
        return [self._fail(rule, locs, evidence, f"必填列存在空值: {evidence}")]
