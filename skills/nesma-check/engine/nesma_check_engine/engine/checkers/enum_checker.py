"""enum_checker（080/081/087）：列值枚举校验。"""
from __future__ import annotations
from ...models.rule import Rule
from ...models.document import Document
from ...utils.location import LocationAnchor
from .base import BaseChecker, register

@register("enum")
class EnumChecker(BaseChecker):
    def run(self, rule: Rule, document: Document | list[Document]) -> list:
        if isinstance(document, list): document = document[0]
        p = rule.checker_params
        sheet = self._find_sheet(document, p["sheet_role"])
        if sheet is None:
            return [self._skipped(rule, f"未找到 sheet_role={p['sheet_role']}")]
        col = p["col"]
        ci = sheet.columns.get(col)
        if ci is None:
            return [self._skipped(rule, f"列 '{col}' 不存在")]
        allowed = p["values"]
        ci_flag = p.get("ci", False)
        allowed_norm = {v.lower() for v in allowed} if ci_flag else set(allowed)
        bad = []
        for ri, row in enumerate(sheet.data_rows):
            if ci >= len(row): continue
            v = row[ci]
            if v is None or (isinstance(v, str) and not v.strip()): continue
            v_str = str(v).strip()
            v_norm = v_str.lower() if ci_flag else v_str
            if v_norm not in allowed_norm:
                bad.append((v_str, sheet.header_row + 1 + ri, sheet.name))
        if not bad:
            return [self._pass(rule)]
        locs = [LocationAnchor(doc_type=document.doc_type, sheet=b[2], row=b[1], col=col) for b in bad]
        evidence = "; ".join(f"行{b[1]} 值='{b[0]}'" for b in bad)
        return [self._fail(rule, locs, evidence,
                           f"列 '{col}' 存在非法枚举值（允许: {','.join(allowed)}）: {evidence}")]
