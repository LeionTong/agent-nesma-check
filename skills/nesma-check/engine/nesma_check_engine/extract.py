"""一次性提取文档→中间 JSON（每个文件只读一次，issue 2.1）。"""
from __future__ import annotations
import json
from pathlib import Path
from .models.document import Document
from .services.doc_parser import DocParser
from .utils.logger import get_logger

_logger = get_logger("extract")

def extract(files: list[Path], output: Path | None = None) -> list[Document]:
    parser = DocParser()
    documents = []
    for f in files:
        try:
            doc = parser.parse(f)
            documents.append(doc)
            _logger.info("提取完成: %s (%s)", f.name, doc.doc_type)
        except Exception as e:
            _logger.error("提取失败: %s (%s)", f, e)
            documents.append(Document(file_path=str(f), doc_type="").with_error(str(e)))
    if output is not None:
        data = [d.to_dict() for d in documents]
        output.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
    return documents
