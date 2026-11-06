"""unique_checker（093/095）：列值唯一性。重复项提示 SP-4 语义相似度复核。"""
from __future__ import annotations
from collections import defaultdict
from ...models.rule import Rule
from ...models.document import Document
from ...utils.location import LocationAnchor
from .base import BaseChecker, register

@register("unique")
class UniqueChecker(BaseChecker):
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
        groups = defaultdict(list)
        for ri, row in enumerate(sheet.data_rows):
            if ci >= len(row): continue
            v = row[ci]
            if v is None or (isinstance(v, str) and not v.strip()): continue
            key = str(v).strip().lower()
            groups[key].append((str(v).strip(), sheet.header_row + 1 + ri, sheet.name))
        dups = {k: v for k, v in groups.items() if len(v) > 1}
        if not dups:
            return [self._pass(rule)]
        locs = []
        evidence_parts = []
        for key, entries in dups.items():
            for val, row_num, sheet_name in entries:
                locs.append(LocationAnchor(doc_type=document.doc_type, sheet=sheet_name,
                                           row=row_num, col=col))
                evidence_parts.append(f"'{val}' 行{row_num}")
        evidence = "; ".join(evidence_parts)
        reason = f"列 '{col}' 存在重复值: {evidence}（疑似相似功能项，需 SP-4 语义相似度复核）"
        return [self._fail(rule, locs, evidence, reason)]
