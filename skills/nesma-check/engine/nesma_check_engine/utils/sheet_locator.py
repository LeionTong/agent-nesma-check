"""sheet 名→语义角色映射 + 表头行检测。"""
from __future__ import annotations

SHEET_NAME_ROLES: dict[str, str] = {
    "规模估算": "estimate",
    "开发费用估算": "cost",
    "开发费用附件": "cost",
    "项目特征": "project_feature",
    "模板使用说明&基础参数": "instruction",
}

EXPECTED_COLS: dict[str, set[str]] = {
    "estimate": {"编号","子系统","一级模块","二级模块","三级模块","四级模块",
                 "功能项描述","功能点计数项名称","类别","UFP",
                 "重用程度","修改类型","US","备注","QSC"},
    "cost": set(), "project_feature": set(), "instruction": set(), "other": set(),
}

def classify_sheet(sheet_name: str) -> str:
    return SHEET_NAME_ROLES.get(sheet_name, "other")

def locate_header_row(rows: list[list], expected_cols: set[str], max_scan: int = 10) -> int:
    """在前 max_scan 行找与期望列名集合重合度最高的行。返回 1-based 行号；找不到返回 -1。"""
    if not expected_cols:
        return -1
    best_row, best_overlap = -1, 0
    for i, row in enumerate(rows[:max_scan], start=1):
        row_cells = {str(c).strip() for c in row if c is not None}
        overlap = len(row_cells & expected_cols)
        if overlap > best_overlap:
            best_overlap, best_row = overlap, i
    if best_overlap >= len(expected_cols) / 2:
        return best_row
    return -1
