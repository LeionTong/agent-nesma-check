"""sheet 定位器与章节树构建测试。"""
from nesma_check_engine.utils.sheet_locator import (
    classify_sheet, locate_header_row, EXPECTED_COLS)
from nesma_check_engine.utils.section_locator import build_section_tree
from nesma_check_engine.models.document import Paragraph, SectionNode

def test_classify_sheet():
    assert classify_sheet("规模估算") == "estimate"
    assert classify_sheet("开发费用估算") == "cost"
    assert classify_sheet("开发费用附件") == "cost"
    assert classify_sheet("项目特征") == "project_feature"
    assert classify_sheet("其他") == "other"

def test_expected_cols_estimate():
    cols = EXPECTED_COLS["estimate"]
    for c in ["类别","重用程度","修改类型","US","功能点计数项名称","功能项描述"]:
        assert c in cols

def test_locate_header_row_finds_best_match():
    rows = [["元数据"]*14]*4 + [["编号","子系统","一级模块","二级模块","三级模块",
        "四级模块","功能项描述","功能点计数项名称","类别","UFP","重用程度","修改类型","US","备注"]]
    assert locate_header_row(rows, EXPECTED_COLS["estimate"]) == 5

def test_locate_header_row_not_found():
    assert locate_header_row([["无","关","内","容"]], EXPECTED_COLS["estimate"]) == -1

def test_build_section_tree_with_headings():
    paras = [
        Paragraph(idx=0, style="Normal", text="前言"),
        Paragraph(idx=1, style="Heading 1", text="1 概述"),
        Paragraph(idx=2, style="Normal", text="概述内容"),
        Paragraph(idx=3, style="Heading 2", text="1.1 背景"),
        Paragraph(idx=4, style="Normal", text="背景内容"),
        Paragraph(idx=5, style="Heading 1", text="2 需求"),
        Paragraph(idx=6, style="Normal", text="需求内容")]
    tree = build_section_tree(paras)
    assert tree is not None
    assert tree.title == "root"
    assert len(tree.children) == 2
    assert tree.children[0].title == "1 概述"
    assert tree.children[0].start_para == 1
    assert tree.children[0].end_para == 5
    assert tree.children[0].children[0].title == "1.1 背景"
    assert tree.children[1].title == "2 需求"
    assert tree.children[1].start_para == 5
    assert tree.children[1].end_para == 7

def test_build_section_tree_no_headings():
    paras = [Paragraph(idx=0, style="Normal", text="无标题"), Paragraph(idx=1, style="Normal", text="内容")]
    assert build_section_tree(paras) is None
