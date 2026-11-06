"""path_resolver 测试：输出路径解析。"""
from pathlib import Path
from nesma_check_engine.services.path_resolver import resolve

def test_explicit_file_path(tmp_path):
    out = tmp_path / "report.md"
    result = resolve(str(out), tmp_path / "input.xlsx")
    assert result == out

def test_explicit_dir_path_with_slash(tmp_path):
    out_dir = tmp_path / "reports"
    result = resolve(str(out_dir) + "/", tmp_path / "input.xlsx")
    assert result.parent == out_dir
    assert result.name.startswith("NESMA合规性检查报告-")
    assert result.name.endswith(".md")

def test_explicit_dir_path_no_extension(tmp_path):
    out_dir = tmp_path / "reports"
    result = resolve(str(out_dir), tmp_path / "input.xlsx")
    assert result.parent == out_dir
    assert result.suffix == ".md"

def test_omitted_single_file_input(tmp_path):
    input_file = tmp_path / "input.xlsx"
    result = resolve(None, input_file)
    assert result.parent == tmp_path
    assert result.name.startswith("NESMA合规性检查报告-")

def test_omitted_multi_file_input(tmp_path):
    """多文件输入取首个文件所在目录"""
    f1 = tmp_path / "sub1" / "f1.xlsx"
    f1.parent.mkdir()
    f2 = tmp_path / "sub2" / "f2.xlsx"
    f2.parent.mkdir()
    result = resolve(None, f1)
    assert result.parent == f1.parent

def test_omitted_relative_path(tmp_path, monkeypatch):
    """相对路径不强制转绝对"""
    monkeypatch.chdir(tmp_path)
    result = resolve(None, Path("./docs/input.xlsx"))
    assert "docs" in str(result.parent)

def test_dir_not_exist_created(tmp_path):
    out_dir = tmp_path / "a" / "b" / "c"
    resolve(str(out_dir) + "/", tmp_path / "input.xlsx")
    assert out_dir.exists()

def test_auto_filename_format(tmp_path):
    """自动文件名格式: NESMA合规性检查报告-YYYYMMDD-HHmm.md"""
    result = resolve(None, tmp_path / "input.xlsx")
    import re
    assert re.match(r"NESMA合规性检查报告-\d{8}-\d{4}\.md", result.name)

def test_explicit_file_path_creates_parent(tmp_path):
    """显式文件路径的父目录不存在时创建"""
    out = tmp_path / "a" / "b" / "report.md"
    result = resolve(str(out), tmp_path / "input.xlsx")
    assert out.parent.exists()

def test_omitted_creates_input_parent_dir(tmp_path):
    """省略 output 时输入目录不存在也要创建（边界场景）"""
    input_file = tmp_path / "newdir" / "input.xlsx"
    result = resolve(None, input_file)
    assert result.parent.exists()
