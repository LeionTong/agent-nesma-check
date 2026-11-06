"""docx 读取（python-docx）。保留段落style+建章节树+类型识别。"""
from __future__ import annotations
from pathlib import Path
from docx import Document as DocxDocument
from ..models.document import Document, Paragraph, Table
from ..utils.section_locator import build_section_tree

SRS_KW = ("需求说明书", "需求规格说明书")
TEST_KW = ("测试报告", "验收测试")
TECH_KW = ("技术规范书", "技术规范")

class DocxReader:
    def read(self, path: str | Path) -> Document:
        path = Path(path)
        d = DocxDocument(str(path))
        paragraphs = [Paragraph(idx=i, style=p.style.name, text=p.text)
                      for i, p in enumerate(d.paragraphs)]
        tables = [Table(idx=i, rows=[[c.text for c in row.cells] for row in t.rows])
                  for i, t in enumerate(d.tables)]
        section_tree = build_section_tree(paragraphs)
        doc_type = self._recognize(path, paragraphs)
        return Document(file_path=str(path), doc_type=doc_type, sheets=[],
                        paragraphs=paragraphs, tables=tables, section_tree=section_tree)

    def _recognize(self, path: Path, paragraphs: list[Paragraph]) -> str:
        name = path.name
        head_text = " ".join(p.text for p in paragraphs[:10] if p.text)
        for kw in SRS_KW:
            if kw in name or kw in head_text: return "srs"
        for kw in TEST_KW:
            if kw in name or kw in head_text: return "test_report"
        for kw in TECH_KW:
            if kw in name or kw in head_text: return "technical_specification"
        return "unknown"
