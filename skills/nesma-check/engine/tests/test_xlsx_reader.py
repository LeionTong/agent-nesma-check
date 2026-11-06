"""xlsx reader 集成测试（基于真实拆分表）。"""
from pathlib import Path
import pytest
from nesma_check_engine.services.xlsx_reader import XlsxReader
from nesma_check_engine.models.document import Document

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE = FIXTURES / "NESMA评估表-合并表格.xlsx"
pytestmark = pytest.mark.skipif(not SAMPLE.exists(), reason="fixture 缺失")

def test_returns_document():
    doc = XlsxReader().read(SAMPLE)
    assert isinstance(doc, Document)
    assert doc.doc_type == "function_breakdown"
    assert len(doc.sheets) > 0

def test_finds_estimate_sheet():
    doc = XlsxReader().read(SAMPLE)
    est = next((s for s in doc.sheets if s.semantic_role == "estimate"), None)
    assert est is not None and est.name == "规模估算"

def test_header_row_not_first():
    """真实拆分表表头在第5行。"""
    doc = XlsxReader().read(SAMPLE)
    est = next(s for s in doc.sheets if s.semantic_role == "estimate")
    assert est.header_row == 5

def test_columns_by_name():
    doc = XlsxReader().read(SAMPLE)
    est = next(s for s in doc.sheets if s.semantic_role == "estimate")
    for c in ["类别","重用程度","修改类型","US"]:
        assert c in est.columns

def test_data_rows_not_empty():
    doc = XlsxReader().read(SAMPLE)
    est = next(s for s in doc.sheets if s.semantic_role == "estimate")
    assert len(est.data_rows) > 0

def test_cost_sheet_meta_rows():
    """开发费用估算 sheet 元数据按坐标存。"""
    doc = XlsxReader().read(SAMPLE)
    cost = next((s for s in doc.sheets if s.semantic_role == "cost"), None)
    assert cost is not None and isinstance(cost.meta_rows, dict)

def test_call_count_once(monkeypatch):
    """每个文件只 load 一次（issue 2.1）。"""
    count = 0
    import openpyxl
    orig = openpyxl.load_workbook
    def counting(*a, **kw):
        nonlocal count; count += 1
        return orig(*a, **kw)
    monkeypatch.setattr(openpyxl, "load_workbook", counting)
    XlsxReader().read(SAMPLE)
    assert count == 1
