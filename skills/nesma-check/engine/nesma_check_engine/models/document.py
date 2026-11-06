"""Document 数据模型。"""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Sheet:
    name: str
    semantic_role: str
    header_row: int
    columns: dict[str, int]
    data_rows: list[list]
    meta_rows: dict[str, object]
    def to_dict(self) -> dict:
        return {"name": self.name, "semantic_role": self.semantic_role,
                "header_row": self.header_row, "columns": self.columns,
                "data_rows": self.data_rows, "meta_rows": self.meta_rows}
    @classmethod
    def from_dict(cls, d: dict) -> "Sheet":
        return cls(name=d["name"], semantic_role=d["semantic_role"],
                   header_row=d["header_row"], columns=d["columns"],
                   data_rows=d["data_rows"], meta_rows=d["meta_rows"])

@dataclass
class Paragraph:
    idx: int
    style: str
    text: str
    def to_dict(self) -> dict:
        return {"idx": self.idx, "style": self.style, "text": self.text}
    @classmethod
    def from_dict(cls, d: dict) -> "Paragraph":
        return cls(idx=d["idx"], style=d["style"], text=d["text"])

@dataclass
class Table:
    idx: int
    rows: list[list[str]]
    def to_dict(self) -> dict:
        return {"idx": self.idx, "rows": self.rows}
    @classmethod
    def from_dict(cls, d: dict) -> "Table":
        return cls(idx=d["idx"], rows=d["rows"])

@dataclass
class SectionNode:
    title: str
    level: int
    start_para: int
    end_para: int
    children: list["SectionNode"] = field(default_factory=list)
    def find(self, title_path: str) -> "SectionNode | None":
        parts = title_path.split("/", 1)
        head, rest = parts[0], parts[1] if len(parts) > 1 else None
        for child in self.children:
            if child.title == head:
                return child if rest is None else child.find(rest)
        return None
    def paragraphs_in(self) -> tuple[int, int]:
        return (self.start_para, self.end_para)
    def to_dict(self) -> dict:
        return {"title": self.title, "level": self.level,
                "start_para": self.start_para, "end_para": self.end_para,
                "children": [c.to_dict() for c in self.children]}
    @classmethod
    def from_dict(cls, d: dict) -> "SectionNode":
        return cls(title=d["title"], level=d["level"],
                   start_para=d["start_para"], end_para=d["end_para"],
                   children=[cls.from_dict(c) for c in d.get("children", [])])

@dataclass
class Document:
    file_path: str
    doc_type: str
    sheets: list[Sheet] = field(default_factory=list)
    paragraphs: list[Paragraph] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    section_tree: SectionNode | None = None
    parse_error: str | None = None
    @property
    def parsed(self) -> bool:
        return self.parse_error is None
    def get_section(self, title_path: str) -> list[Paragraph]:
        if self.section_tree is None:
            return self.paragraphs
        node = self.section_tree.find(title_path)
        if node is None:
            return []
        start, end = node.paragraphs_in()
        return self.paragraphs[start:end]
    def with_error(self, error_msg: str) -> "Document":
        self.parse_error = error_msg
        return self
    def to_dict(self) -> dict:
        return {"file_path": self.file_path, "doc_type": self.doc_type,
                "parsed": self.parsed, "error_msg": self.parse_error,
                "sheets": [s.to_dict() for s in self.sheets],
                "paragraphs": [p.to_dict() for p in self.paragraphs],
                "tables": [t.to_dict() for t in self.tables],
                "section_tree": self.section_tree.to_dict() if self.section_tree else None}
    @classmethod
    def from_dict(cls, d: dict) -> "Document":
        return cls(file_path=d["file_path"], doc_type=d["doc_type"],
                   sheets=[Sheet.from_dict(s) for s in d.get("sheets", [])],
                   paragraphs=[Paragraph.from_dict(p) for p in d.get("paragraphs", [])],
                   tables=[Table.from_dict(t) for t in d.get("tables", [])],
                   section_tree=SectionNode.from_dict(d["section_tree"]) if d.get("section_tree") else None,
                   parse_error=d.get("error_msg"))
