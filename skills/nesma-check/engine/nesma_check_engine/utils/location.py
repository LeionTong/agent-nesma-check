"""位置锚点格式化。Excel: [{sheet}] 行{n}; 列[{col}] / Word: §{section} #P{para}"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class LocationAnchor:
    doc_type: str
    sheet: str | None = None
    section: str | None = None
    row: int | None = None
    col: str | None = None
    para_idx: int | None = None

    def to_str(self) -> str:
        if self.sheet is not None or self.doc_type == "function_breakdown":
            sheet_part = f"[{self.sheet}]" if self.sheet else ""
            row_part = f"行{self.row}" if self.row is not None else ""
            col_part = f"列[{self.col}]" if self.col is not None else ""
            head = " ".join(p for p in [sheet_part, row_part] if p)
            tail = "; ".join(p for p in [head, col_part] if p)
            return tail
        else:
            parts = []
            if self.section: parts.append(f"§{self.section}")
            if self.para_idx is not None: parts.append(f"#P{self.para_idx}")
            return " ".join(parts) if parts else ""
