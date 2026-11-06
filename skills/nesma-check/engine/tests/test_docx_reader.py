"""docx reader 集成测试。"""
from pathlib import Path
import pytest
from nesma_check_engine.services.docx_reader import DocxReader
from nesma_check_engine.models.document import Document, SectionNode

FIXTURES = Path(__file__).parent / "fixtures"
SRS = FIXTURES / "sample_srs.docx"
pytestmark = pytest.mark.skipif(not SRS.exists(), reason="fixture 缺失")

def test_returns_document():
    doc = DocxReader().read(SRS)
    assert isinstance(doc, Document)
    assert doc.doc_type in ("srs","test_report","technical_specification","unknown")

def test_paragraphs_not_empty():
    doc = DocxReader().read(SRS)
    assert len(doc.paragraphs) > 0
    assert all(hasattr(p, "style") for p in doc.paragraphs)

def test_section_tree_built_or_none():
    doc = DocxReader().read(SRS)
    if doc.section_tree is not None:
        assert isinstance(doc.section_tree, SectionNode)
        assert doc.section_tree.title == "root"
        assert len(doc.section_tree.children) > 0

def test_get_section():
    doc = DocxReader().read(SRS)
    if doc.section_tree and doc.section_tree.children:
        paras = doc.get_section(doc.section_tree.children[0].title)
        assert isinstance(paras, list)

def test_call_count_once(monkeypatch):
    import nesma_check_engine.services.docx_reader as mod
    count = 0
    orig = mod.DocxDocument
    def counting(*a, **kw):
        nonlocal count; count += 1
        return orig(*a, **kw)
    monkeypatch.setattr(mod, "DocxDocument", counting)
    DocxReader().read(SRS)
    assert count == 1

def test_recognize_srs():
    """文件名含'需求说明书'识别为 srs。"""
    doc = DocxReader().read(SRS)
    assert doc.doc_type == "srs"
