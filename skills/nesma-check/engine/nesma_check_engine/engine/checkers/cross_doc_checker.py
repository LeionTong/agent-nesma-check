"""cross_doc_checker：跨文档层级对应检查（071-074）。

拆分表列值 vs docx 章节标题的层级约束匹配 + 修改类型↔功能类别比对。
"""
from __future__ import annotations
from ...models.rule import Rule
from ...models.document import Document
from ...utils.location import LocationAnchor
from .base import BaseChecker, register
from .cross_doc_matcher import (
    normalize, match_by_level, match_exists, match_by_level_degraded,
    find_section_normalized, parse_function_type, MODIFY_TYPE_MAP,
)


_DOCX_TYPES = ("srs", "test_report", "technical_specification")


@register("builtin:cross_doc")
class CrossDocChecker(BaseChecker):
    def run(self, rule: Rule, document: Document | list[Document]) -> list:
        docs = document if isinstance(document, list) else [document]
        fb = next((d for d in docs if d.doc_type == "function_breakdown"), None)
        docx = next((d for d in docs if d.doc_type in _DOCX_TYPES), None)
        if fb is None:
            return [self._skipped(rule, "缺少文档类型: function_breakdown")]
        if docx is None:
            return [self._skipped(rule, f"缺少文档类型: {rule.document_types}")]
        sheet = self._find_sheet(fb, "estimate")
        if sheet is None:
            return [self._skipped(rule, "拆分表未找到 estimate sheet")]
        params = rule.checker_params
        mappings = params.get("mappings", [])
        modify_type_col = params.get("modify_type_col")
        section_path = params.get("section_path")
        subtree = find_section_normalized(docx.section_tree, section_path)
        is_degraded = docx.section_tree is None
        results = []
        for ri, row in enumerate(sheet.data_rows):
            row_results = self._check_row(rule, row, ri, sheet, fb, docx,
                                          mappings, modify_type_col, subtree,
                                          is_degraded)
            results.extend(row_results)
        if not results:
            results.append(self._pass(rule, "所有层级对应检查通过"))
        return results

    def _check_row(self, rule, row, ri, sheet, fb, docx, mappings,
                   modify_type_col, subtree, is_degraded):
        row_num = sheet.header_row + 1 + ri
        unmatched = []
        matched_node = None
        for m in mappings:
            col_name = m["col"]
            ci = sheet.columns.get(col_name)
            if ci is None:
                return [self._skipped(rule, f"拆分表缺少列: {col_name}")]
            col_val = self._cell(row, ci)
            if not col_val:
                continue
            if m.get("mode") == "exists":
                if is_degraded:
                    hit = match_exists(None, docx.paragraphs, col_val)
                else:
                    hit = match_exists(subtree, None, col_val)
            else:
                exp_lvl = m["expected_level"]
                tol = m.get("level_tolerance", 1)
                if is_degraded:
                    hit = match_by_level_degraded(docx.paragraphs, col_val, exp_lvl, tol)
                else:
                    hit = match_by_level(subtree, col_val, exp_lvl, tol)
            if not hit:
                unmatched.append((col_name, col_val))
            elif col_name == "功能点计数项名称" and not is_degraded and m.get("mode") != "exists":
                matched_node = self._find_matched_node(subtree, col_val,
                    m["expected_level"], m.get("level_tolerance", 1))
        if unmatched:
            loc = LocationAnchor(doc_type=fb.doc_type, sheet=sheet.name,
                                 row=row_num, col=unmatched[0][0])
            evidence = "; ".join(f"{c}=\"{v}\"" for c, v in unmatched)
            return [self._fail(rule, [loc], evidence,
                               f"层级对应不匹配: {evidence}")]
        if modify_type_col:
            mt_ci = sheet.columns.get(modify_type_col)
            if mt_ci is not None:
                mt = self._cell(row, mt_ci)
                ft = self._parse_ft(docx, matched_node, is_degraded)
                if ft is None:
                    return [self._skipped(rule,
                        f"行{row_num} 无法解析功能类型（无√选中项或无法定位段落）")]
                expected_ft = MODIFY_TYPE_MAP.get(mt)
                if expected_ft and expected_ft != ft:
                    loc = LocationAnchor(doc_type=fb.doc_type, sheet=sheet.name,
                                         row=row_num, col=modify_type_col)
                    return [self._fail(rule, [loc],
                        f"拆分表=\"{mt}\" ↔ SRS功能类型=\"{ft}\"",
                        f"修改类型不匹配: 拆分表={mt}({expected_ft}) ≠ SRS={ft}")]
        return []

    def _cell(self, row: list, ci: int) -> str:
        if ci >= len(row): return ""
        v = row[ci]
        return str(v).strip() if v is not None else ""

    def _find_matched_node(self, tree, value, exp_lvl, tol):
        """找功能点计数项名称命中的节点（用于定位功能类型段落区间）。"""
        if tree is None: return None
        norm_val = normalize(value)
        return self._search_node(tree, norm_val, exp_lvl - tol, exp_lvl + tol)

    def _search_node(self, node, norm_val, lo, hi):
        if node.level != 0 and lo <= node.level <= hi:
            if normalize(node.title) == norm_val:
                return node
        for child in node.children:
            found = self._search_node(child, norm_val, lo, hi)
            if found: return found
        return None

    def _parse_ft(self, docx, matched_node, is_degraded):
        if matched_node is not None:
            start, end = matched_node.paragraphs_in()
            return parse_function_type(docx.paragraphs, start, end)
        if is_degraded:
            return parse_function_type(docx.paragraphs, 0, len(docx.paragraphs))
        return None
