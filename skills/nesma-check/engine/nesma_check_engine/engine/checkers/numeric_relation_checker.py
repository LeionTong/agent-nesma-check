"""numeric_relation_checker（097）：从 meta_rows 按坐标取值，受限 eval 求值。

表达式来自硬编码 DISPATCH 表（非用户输入），eval 限制 __builtins__ 为空，安全。
sheet 未找到或坐标无值 → skipped + reason（不 fail）。
"""
from __future__ import annotations
import re
from ...models.rule import Rule
from ...models.document import Document, Sheet
from ...utils.location import LocationAnchor
from .base import BaseChecker, register

_COORD_RE = re.compile(r"\b([A-Z]+\d+)\b")

@register("numeric_relation")
class NumericRelationChecker(BaseChecker):
    def run(self, rule: Rule, document: Document | list[Document]) -> list:
        if isinstance(document, list): document = document[0]
        p = rule.checker_params
        sheet = self._find_sheet(document, p["sheet_role"])
        if sheet is None:
            return [self._skipped(rule, f"未找到 sheet_role={p['sheet_role']}")]
        expr: str = p["expr"]
        coords = _COORD_RE.findall(expr)
        values = {}
        missing = []
        for coord in coords:
            raw = sheet.meta_rows.get(coord)
            if raw is None:
                missing.append(coord)
                continue
            try:
                values[coord] = float(raw)
            except (ValueError, TypeError):
                return [self._fail(rule, [], f"{coord}={raw!r}",
                                   f"单元格 {coord} 无法解析为数值: {raw!r}")]
        if missing:
            return [self._skipped(rule, f"坐标无值: {', '.join(missing)}")]
        local_ns = dict(values)
        result = eval(expr, {"__builtins__": {}}, local_ns)
        if result:
            return [self._pass(rule, f"{expr} = True ({self._fmt(values)})")]
        loc = LocationAnchor(doc_type=document.doc_type, sheet=sheet.name)
        evidence = f"{expr} = False ({self._fmt(values)})"
        return [self._fail(rule, [loc], evidence,
                           f"数值关系不满足: {expr}（实际值: {self._fmt(values)}）")]

    @staticmethod
    def _fmt(values: dict) -> str:
        return ", ".join(f"{k}={v}" for k, v in sorted(values.items()))
