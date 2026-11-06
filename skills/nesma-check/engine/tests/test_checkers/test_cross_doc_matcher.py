"""cross_doc_matcher 测试：跨文档匹配核心逻辑。"""
from nesma_check_engine.engine.checkers.cross_doc_matcher import normalize
from nesma_check_engine.models.document import SectionNode

def test_normalize_strips_whitespace():
    assert normalize("  统一纳管  ") == "统一纳管"

def test_normalize_removes_number_prefix_dot():
    assert normalize("4.1. 统一纳管") == "统一纳管"

def test_normalize_removes_number_prefix_chinese():
    assert normalize("1、统一纳管") == "统一纳管"

def test_normalize_removes_multi_level_prefix():
    assert normalize("4.1.1.1.1. 小区标准地址数据") == "小区标准地址数据"

def test_normalize_fullwidth_to_halfwidth():
    assert normalize("统一纳管（）") == "统一纳管()"

def test_normalize_removes_symbols():
    assert normalize("√新增") == "新增"
    assert normalize("□完善") == "完善"

def test_normalize_lowercases():
    assert normalize("ILF") == "ilf"

def test_normalize_collapses_inner_spaces():
    assert normalize("统一  纳管") == "统一纳管"

def test_normalize_empty():
    assert normalize("") == ""
    assert normalize("   ") == ""


def _make_tree():
    l6 = SectionNode(title="机房配置数据", level=6, start_para=10, end_para=15, children=[])
    l4 = SectionNode(title="集团统一纳管", level=4, start_para=5, end_para=20, children=[l6])
    l3 = SectionNode(title="统一纳管", level=3, start_para=3, end_para=25, children=[l4])
    l1 = SectionNode(title="功能需求", level=1, start_para=0, end_para=30, children=[l3])
    root = SectionNode(title="root", level=0, start_para=0, end_para=30, children=[l1])
    return root


def test_match_by_level_exact_hit():
    from nesma_check_engine.engine.checkers.cross_doc_matcher import match_by_level
    tree = _make_tree()
    assert match_by_level(tree, "统一纳管", expected_level=3, tolerance=1) is True


def test_match_by_level_normalized_hit():
    from nesma_check_engine.engine.checkers.cross_doc_matcher import match_by_level
    tree = _make_tree()
    assert match_by_level(tree, "4.1. 统一纳管", expected_level=3, tolerance=1) is True


def test_match_by_level_tolerance_hit():
    from nesma_check_engine.engine.checkers.cross_doc_matcher import match_by_level
    tree = _make_tree()
    assert match_by_level(tree, "集团统一纳管", expected_level=3, tolerance=1) is True


def test_match_by_level_out_of_tolerance():
    from nesma_check_engine.engine.checkers.cross_doc_matcher import match_by_level
    tree = _make_tree()
    assert match_by_level(tree, "功能需求", expected_level=3, tolerance=1) is False


def test_match_by_level_no_match():
    from nesma_check_engine.engine.checkers.cross_doc_matcher import match_by_level
    tree = _make_tree()
    assert match_by_level(tree, "不存在的模块", expected_level=3, tolerance=1) is False


def test_match_by_level_l6_hit():
    from nesma_check_engine.engine.checkers.cross_doc_matcher import match_by_level
    tree = _make_tree()
    assert match_by_level(tree, "机房配置数据", expected_level=6, tolerance=2) is True


from nesma_check_engine.engine.checkers.cross_doc_matcher import match_exists

def test_match_exists_in_tree_exact():
    tree = _make_tree()
    assert match_exists(tree, None, "机房配置数据") is True

def test_match_exists_in_tree_substring():
    """功能点计数项名称是标题子串 → 命中"""
    tree = _make_tree()
    assert match_exists(tree, None, "机房配置") is True

def test_match_exists_no_tree_uses_paragraphs():
    """无章节树时退化为段落文本子串匹配"""
    from nesma_check_engine.models.document import Paragraph
    paras = [Paragraph(idx=0, style="Normal", text="4.1.1.1.1. 小区标准地址数据"),
             Paragraph(idx=1, style="Normal", text="功能类型：√新增")]
    assert match_exists(None, paras, "小区标准地址数据") is True

def test_match_exists_no_match():
    tree = _make_tree()
    assert match_exists(tree, None, "完全不存在的名称") is False

def test_match_exists_empty_value():
    tree = _make_tree()
    assert match_exists(tree, None, "") is False


from nesma_check_engine.engine.checkers.cross_doc_matcher import parse_function_type, MODIFY_TYPE_MAP
from nesma_check_engine.models.document import Paragraph

def test_parse_function_type_xinzeng():
    paras = [Paragraph(idx=0, style="Normal", text="用户：营业员"),
             Paragraph(idx=1, style="Normal", text="功能类型：√新增；□完善；□下线")]
    assert parse_function_type(paras, 0, 5) == "新增"

def test_parse_function_type_wanshan():
    paras = [Paragraph(idx=0, style="Normal", text="用户：终端用户"),
             Paragraph(idx=1, style="Normal", text="功能类型：□新增；√完善；□下线")]
    assert parse_function_type(paras, 0, 5) == "完善"

def test_parse_function_type_xiaxian():
    paras = [Paragraph(idx=0, style="Normal", text="功能类型：□新增；□完善；√下线")]
    assert parse_function_type(paras, 0, 5) == "下线"

def test_parse_function_type_no_check():
    paras = [Paragraph(idx=0, style="Normal", text="功能类型：□新增；□完善；□下线")]
    assert parse_function_type(paras, 0, 5) is None

def test_parse_function_type_no_field():
    paras = [Paragraph(idx=0, style="Normal", text="这是一段普通描述")]
    assert parse_function_type(paras, 0, 5) is None

def test_parse_function_type_range_limit():
    """功能类型段落不在区间内 → None"""
    paras = [Paragraph(idx=0, style="Normal", text="功能类型：√新增"),
             Paragraph(idx=10, style="Normal", text="功能类型：√完善")]
    assert parse_function_type(paras, 0, 3) == "新增"
    assert parse_function_type(paras, 5, 15) == "完善"

def test_modify_type_map():
    assert MODIFY_TYPE_MAP["新增"] == "新增"
    assert MODIFY_TYPE_MAP["修改"] == "完善"
    assert MODIFY_TYPE_MAP["删除"] == "下线"


from nesma_check_engine.engine.checkers.cross_doc_matcher import (
    find_section_normalized, match_by_level_degraded
)
from nesma_check_engine.models.document import Paragraph

def test_find_section_normalized_exact():
    tree = _make_tree()
    node = find_section_normalized(tree, "功能需求")
    assert node is not None and node.title == "功能需求"

def test_find_section_normalized_with_prefix():
    """带编号前缀的路径也能匹配"""
    tree = _make_tree()
    node = find_section_normalized(tree, "4. 功能需求")
    assert node is not None and "功能需求" in node.title

def test_find_section_normalized_no_match():
    tree = _make_tree()
    assert find_section_normalized(tree, "不存在的章节") is None

def test_find_section_normalized_none_path():
    assert find_section_normalized(_make_tree(), None) is not None  # 返回 root

def test_match_by_level_degraded_numbered():
    """降级模式：Normal 段落带编号 4.1.1. → 推断 L3"""
    paras = [Paragraph(idx=0, style="Normal", text="4.1. 智能搜索引擎"),
             Paragraph(idx=1, style="Normal", text="4.1.1. 小区信息模糊查询"),
             Paragraph(idx=2, style="Normal", text="4.1.1.1.1. 小区标准地址数据")]
    assert match_by_level_degraded(paras, "智能搜索引擎", expected_level=3, tolerance=1) is True
    assert match_by_level_degraded(paras, "小区标准地址数据", expected_level=5, tolerance=2) is True

def test_match_by_level_degraded_no_number():
    """降级模式：无编号段落归入未知池，做存在性匹配"""
    paras = [Paragraph(idx=0, style="Normal", text="统一纳管模块描述")]
    assert match_by_level_degraded(paras, "统一纳管", expected_level=3, tolerance=1) is False

def test_match_by_level_degraded_empty():
    assert match_by_level_degraded([], "x", 3, 1) is False
