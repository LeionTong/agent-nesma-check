"""数据提取脚本测试（中间 JSON 往返）。"""
import json
from pathlib import Path
from nesma_check_engine.extract import extract
from nesma_check_engine.models.document import Document

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLE = FIXTURES / "NESMA评估表-合并表格.xlsx"
pytestmark = __import__("pytest").mark.skipif(not SAMPLE.exists(), reason="fixture 缺失")

def test_returns_documents_list():
    docs = extract([SAMPLE])
    assert len(docs) == 1 and docs[0].doc_type == "function_breakdown"

def test_parse_error_recorded():
    docs = extract([Path("不存在.xlsx")])
    assert docs[0].parsed is False and docs[0].parse_error is not None

def test_json_roundtrip():
    docs = extract([SAMPLE])
    serialized = json.dumps([d.to_dict() for d in docs], ensure_ascii=False, default=str)
    restored = [Document.from_dict(d) for d in json.loads(serialized)]
    assert restored[0].doc_type == docs[0].doc_type
    assert restored[0].sheets[0].name == docs[0].sheets[0].name
    assert restored[0].sheets[0].header_row == docs[0].sheets[0].header_row

def test_writes_intermediate_json(tmp_path):
    out = tmp_path / "inter.json"
    extract([SAMPLE], output=out)
    assert out.exists()
    assert json.loads(out.read_text(encoding="utf-8"))[0]["doc_type"] == "function_breakdown"

def test_multiple_files():
    docs = extract([SAMPLE, Path("不存在.docx")])
    assert len(docs) == 2 and docs[0].parsed and not docs[1].parsed
