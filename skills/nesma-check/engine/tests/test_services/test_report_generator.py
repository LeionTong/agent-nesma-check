"""report_generator 测试：三级报告渲染。"""
from nesma_check_engine.services.report_generator import _project_info, _document_info

def _sample_output():
    return {
        "version": "0.2.0",
        "config": {"org": "ORG_B", "project_type": "engineering"},
        "documents": [
            {"file_path": "srs.docx", "doc_type": "srs", "parsed": True, "error_msg": None},
            {"file_path": "fb.xlsx", "doc_type": "function_breakdown", "parsed": True, "error_msg": None},
        ],
        "summary": {"total_rules": 25, "executed": 18, "pass": 15, "fail": 2, "skipped_semantic": 8, "errors": 0},
        "results": [],
        "rules": [],
    }

def test_project_info_has_org_and_type():
    out = _sample_output()
    md = _project_info(out)
    assert "ORG_B" in md
    assert "engineering" in md
    assert "项目信息" in md

def test_project_info_has_version():
    out = _sample_output()
    md = _project_info(out)
    assert "0.2.0" in md

def test_document_info_lists_all_docs():
    out = _sample_output()
    md = _document_info(out)
    assert "srs.docx" in md
    assert "fb.xlsx" in md
    assert "已读取" in md or "✅" in md

def test_document_info_shows_unparsed():
    out = _sample_output()
    out["documents"] = [{"file_path": "bad.docx", "doc_type": "srs", "parsed": False, "error_msg": "格式错误"}]
    md = _document_info(out)
    assert "未读取" in md or "❌" in md
    assert "格式错误" in md
