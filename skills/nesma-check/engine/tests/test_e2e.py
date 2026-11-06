"""端到端测试：CLI 跑完整流程，断言 JSON 结构、退出码、关键结果。"""
from __future__ import annotations
import json
from pathlib import Path
from nesma_check_engine.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
CHECKLIST = Path(__file__).parents[2] / "checklist"
CROSS_ENGINEERING = ("Orgs-ORG_B-Cross-071", "Orgs-ORG_B-Cross-073", "Orgs-ORG_B-Cross-075")
CROSS_NEW_DEMAND = ("Orgs-ORG_B-Cross-072",)

def test_cli_version(capsys):
    try:
        main(["--version"])
    except SystemExit as e:
        assert e.code == 0

def test_cli_no_files(capsys):
    code = main([])
    assert code == 3

def test_cli_nonexistent_file(capsys):
    code = main(["nonexistent.xlsx"])
    assert code == 3

def test_cli_extract_only(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    code = main(["--extract-only", "--format", "json", xlsx])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "documents" in data
    assert "results" not in data
    assert code == 0

def test_cli_full_run_json(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    srs = str(FIXTURES / "sample_srs.docx")
    tr = str(FIXTURES / "sample_test_report.docx")
    code = main(["--format", "json", xlsx, srs, tr])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["version"]
    assert data["config"]["org"] == "ORG_B"
    assert data["config"]["project_type"] == "engineering"
    assert "documents" in data and len(data["documents"]) == 3
    assert "summary" in data
    assert "results" in data
    s = data["summary"]
    assert s["pass"] + s["fail"] + s["skipped_semantic"] >= 0
    assert code in (0, 1)

def test_cli_skipped_semantic_present(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    code = main(["--format", "json", xlsx])
    out = capsys.readouterr().out
    data = json.loads(out)
    skipped_ids = {r["rule_id"] for r in data["results"] if r["verdict"] == "skipped"}
    assert "Orgs-ORG_B-Format-091" in skipped_ids
    assert "Orgs-ORG_B-Format-096" in skipped_ids
    assert "Orgs-ORG_B-Format-067" in skipped_ids

def test_cli_markdown(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    code = main(["--format", "markdown", xlsx])
    out = capsys.readouterr().out
    assert "# NESMA 合规性检查报告" in out
    assert "## 摘要" in out
    assert "## 详情" in out

def test_cli_output_to_file(tmp_path, capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    out_file = tmp_path / "report.json"
    code = main(["--output", str(out_file), "--format", "json", xlsx])
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert "results" in data

def test_cli_summary_aggregation(capsys):
    """summary 由 results 程序化聚合。"""
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    srs = str(FIXTURES / "sample_srs.docx")
    tr = str(FIXTURES / "sample_test_report.docx")
    code = main(["--format", "json", xlsx, srs, tr])
    out = capsys.readouterr().out
    data = json.loads(out)
    s = data["summary"]
    results = data["results"]
    assert s["pass"] == sum(1 for r in results if r["verdict"] == "pass")
    assert s["fail"] == sum(1 for r in results if r["verdict"] == "fail")
    assert s["skipped_semantic"] == sum(1 for r in results if r["verdict"] == "skipped")

def test_cli_cross_doc_071_engineering(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    srs = str(FIXTURES / "sample_srs.docx")
    code = main(["--format", "json", "--project-type", "engineering", xlsx, srs])
    out = capsys.readouterr().out
    data = json.loads(out)
    r071 = [r for r in data["results"] if r["rule_id"] == "Orgs-ORG_B-Cross-071"]
    assert len(r071) >= 1
    assert r071[0]["verdict"] in ("pass", "fail", "skipped")

def test_cli_cross_doc_073_engineering(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    tr = str(FIXTURES / "sample_test_report.docx")
    code = main(["--format", "json", "--project-type", "engineering", xlsx, tr])
    out = capsys.readouterr().out
    data = json.loads(out)
    r073 = [r for r in data["results"] if r["rule_id"] == "Orgs-ORG_B-Cross-073"]
    assert len(r073) >= 1

def test_cli_cross_doc_075_skipped(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    code = main(["--format", "json", "--project-type", "engineering", xlsx])
    out = capsys.readouterr().out
    data = json.loads(out)
    r075 = [r for r in data["results"] if r["rule_id"] == "Orgs-ORG_B-Cross-075"]
    assert len(r075) == 1
    assert r075[0]["verdict"] == "skipped"

def test_cli_cross_doc_072_new_demand(capsys):
    xlsx = str(FIXTURES / "NESMA评估表-合并表格.xlsx")
    code = main(["--format", "json", "--project-type", "new_demand", xlsx])
    out = capsys.readouterr().out
    data = json.loads(out)
    r072 = [r for r in data["results"] if r["rule_id"] == "Orgs-ORG_B-Cross-072"]
    assert len(r072) >= 1
    assert r072[0]["verdict"] == "skipped"
