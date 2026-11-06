"""文档解析入口：按扩展名分派 reader。"""
from __future__ import annotations
from pathlib import Path
from ..models.document import Document
from .xlsx_reader import XlsxReader
from .docx_reader import DocxReader

class DocParser:
    def __init__(self):
        self.xlsx_reader = XlsxReader()
        self.docx_reader = DocxReader()

    def parse(self, path: str | Path) -> Document:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        suffix = path.suffix.lower()
        if suffix == ".xlsx": return self.xlsx_reader.read(path)
        if suffix == ".docx": return self.docx_reader.read(path)
        raise ValueError(f"不支持的格式: {suffix}")
