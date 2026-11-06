"""sc_format_082_checker：修改/删除功能重用程度检查。

当修改类型 ∈ {修改,删除} 且 重用程度 != 高：
- 功能项描述/备注 含明确比例信号 → pass(放行)
- 无明确比例信号 → skipped(转语义层，不猜测、不默认放行)
"""
from __future__ import annotations
import re
from ...models.rule import Rule
from ...models.document import Document
from ...utils.location import LocationAnchor
from .base import BaseChecker, register

_SIGNAL_RE = re.compile(
    r"(变更|新增|修改).{0,10}(超过|占比|比例|>|≥|大于).{0,4}50\s*%"
    r"|超过\s*50\s*%"
    r"|50\s*%\s*以上"
    r"|[>≥]\s*50\s*%"
)

@register("builtin:sc_format_082")
class ScFormat082Checker(BaseChecker):
    def run(self, rule: Rule, document: Document | list[Document]) -> list:
        if isinstance(document, list): document = document[0]
        sheet = self._find_sheet(document, "estimate")
        if sheet is None:
            return [self._skipped(rule, "未找到 sheet_role=estimate")]
        ci_modify = sheet.columns.get("修改类型")
        ci_reuse = sheet.columns.get("重用程度")
        ci_desc = sheet.columns.get("功能项描述")
        ci_remark = sheet.columns.get("备注")
        if ci_modify is None or ci_reuse is None:
            return [self._skipped(rule, "缺少 修改类型/重用程度 列")]
        results = []
        for ri, row in enumerate(sheet.data_rows):
            modify = self._cell(row, ci_modify)
            reuse = self._cell(row, ci_reuse)
            if modify not in ("修改", "删除"):
                continue
            if reuse == "高":
                continue
            desc = self._cell(row, ci_desc) if ci_desc is not None else ""
            remark = self._cell(row, ci_remark) if ci_remark is not None else ""
            text = f"{desc} {remark}"
            loc = LocationAnchor(doc_type=document.doc_type, sheet=sheet.name,
                                 row=sheet.header_row + 1 + ri, col="重用程度")
            if _SIGNAL_RE.search(text):
                results.append(self._pass(rule,
                    f"行{sheet.header_row+1+ri} 含明确比例信号: {text.strip()}"))
            else:
                results.append(self._skipped(rule,
                    f"行{sheet.header_row+1+ri} 修改类型={modify} 重用程度={reuse}"
                    f" 无明确比例信号，需语义层判断是否有充分理由"))
        if not results:
            results.append(self._pass(rule, "无修改/删除且重用程度非高的行"))
        return results

    @staticmethod
    def _cell(row: list, ci: int) -> str:
        if ci >= len(row): return ""
        v = row[ci]
        return str(v).strip() if v is not None else ""
