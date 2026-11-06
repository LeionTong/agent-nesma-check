"""xlsx 读取（openpyxl）。表头行检测+列名定位+元数据按坐标存。"""
from __future__ import annotations
from pathlib import Path
import openpyxl
from ..models.document import Document, Sheet
from ..utils.sheet_locator import classify_sheet, locate_header_row, EXPECTED_COLS

class XlsxReader:
    def read(self, path: str | Path) -> Document:
        path = Path(path)
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        sheets = [self._parse_sheet(ws) for ws in wb.worksheets]
        wb.close()
        return Document(file_path=str(path), doc_type="function_breakdown",
                        sheets=sheets, paragraphs=[], tables=[], section_tree=None)

    def _parse_sheet(self, ws) -> Sheet:
        name = ws.title
        role = classify_sheet(name)
        rows_detect = [list(r) for r in ws.iter_rows(min_row=1, max_row=10, values_only=True)]
        expected = EXPECTED_COLS.get(role, set())
        header_row = locate_header_row(rows_detect, expected) if expected else -1

        if header_row == -1:
            all_rows = list(ws.iter_rows(values_only=True))
            meta = {}
            for ri, row in enumerate(all_rows, start=1):
                for ci, cell in enumerate(row, start=1):
                    if cell is not None:
                        meta[f"{openpyxl.utils.get_column_letter(ci)}{ri}"] = cell
            return Sheet(name=name, semantic_role=role, header_row=-1,
                         columns={}, data_rows=[], meta_rows=meta)

        header_vals = rows_detect[header_row - 1]
        columns = {str(v).strip(): i for i, v in enumerate(header_vals) if v is not None and str(v).strip()}
        data_rows = [list(r) for r in ws.iter_rows(min_row=header_row + 1, values_only=True)
                     if any(c is not None and str(c).strip() for c in r)]
        meta = {}
        for ri, row in enumerate(rows_detect[:header_row - 1], start=1):
            for ci, cell in enumerate(row, start=1):
                if cell is not None:
                    meta[f"{openpyxl.utils.get_column_letter(ci)}{ri}"] = cell
        return Sheet(name=name, semantic_role=role, header_row=header_row,
                     columns=columns, data_rows=data_rows, meta_rows=meta)
