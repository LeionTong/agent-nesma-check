"""cross_doc_checker 测试：跨文档一致性检查器。"""
from nesma_check_engine.engine.checkers.cross_doc_checker import CrossDocChecker
from nesma_check_engine.models.rule import Rule
from nesma_check_engine.models.document import Document, Sheet, SectionNode, Paragraph


def _rule_071():
    return Rule(id="Orgs-ORG_B-Cross-071", item_name="", layer="programmatic",
                document_types=["srs", "function_breakdown"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B-Cross",
                checker_key="builtin:cross_doc",
                checker_params={
                    "section_path": None,
                    "mappings": [
                        {"col": "一级模块", "expected_level": 3, "level_tolerance": 1},
                        {"col": "二级模块", "expected_level": 4, "level_tolerance": 1},
                        {"col": "功能点计数项名称", "expected_level": 6, "level_tolerance": 2},
                    ],
                    "modify_type_col": "修改类型",
                    "function_type_field": "功能类型",
                })


def _sheet(rows_data):
    columns = {"编号": 0, "一级模块": 1, "二级模块": 2, "功能点计数项名称": 3, "修改类型": 4}
    return Sheet(name="规模估算", semantic_role="estimate", header_row=5,
                 columns=columns, data_rows=rows_data, meta_rows={})


def _fb_doc(rows_data):
    return Document(file_path="t.xlsx", doc_type="function_breakdown",
                    sheets=[_sheet(rows_data)], paragraphs=[], tables=[])


def _srs_doc(tree=None, paragraphs=None):
    return Document(file_path="t.docx", doc_type="srs", sheets=[],
                    paragraphs=paragraphs or [], tables=[], section_tree=tree)


def test_skipped_missing_fb():
    """缺拆分表 -> skipped"""
    rule = _rule_071()
    docs = [_srs_doc()]
    r = CrossDocChecker().run(rule, docs)[0]
    assert r.verdict == "skipped" and "function_breakdown" in r.reason


def test_skipped_missing_docx():
    """缺 SRS -> skipped"""
    rule = _rule_071()
    docs = [_fb_doc([["1", "统一纳管", "集团纳管", "机房数据", "新增"]])]
    r = CrossDocChecker().run(rule, docs)[0]
    assert r.verdict == "skipped" and "srs" in r.reason


def test_skipped_no_estimate_sheet():
    """拆分表无 estimate sheet -> skipped"""
    rule = _rule_071()
    fb = Document(file_path="t.xlsx", doc_type="function_breakdown",
                  sheets=[], paragraphs=[], tables=[])
    docs = [fb, _srs_doc()]
    r = CrossDocChecker().run(rule, docs)[0]
    assert r.verdict == "skipped" and "estimate" in r.reason


def _make_srs_tree():
    """SRS 章节树: L1(功能需求) > L3(统一纳管) > L4(集团纳管) > L6(机房配置数据)"""
    l6 = SectionNode(title="机房配置数据", level=6, start_para=10, end_para=14, children=[])
    l4 = SectionNode(title="集团统一纳管", level=4, start_para=5, end_para=20, children=[l6])
    l3 = SectionNode(title="统一纳管", level=3, start_para=3, end_para=25, children=[l4])
    l1 = SectionNode(title="功能需求", level=1, start_para=0, end_para=30, children=[l3])
    return SectionNode(title="root", level=0, start_para=0, end_para=30, children=[l1])


def _srs_with_func_type(tree, func_type="新增"):
    """带功能类型段落的 SRS"""
    paras = [Paragraph(idx=10, style="Normal", text="机房配置数据"),
             Paragraph(idx=11, style="Normal", text=f"功能类型：√{func_type}；□完善；□下线")]
    return _srs_doc(tree=tree, paragraphs=paras)


def test_071_all_match_pass():
    """071 全匹配 → pass"""
    rule = _rule_071()
    tree = _make_srs_tree()
    fb = _fb_doc([["1", "统一纳管", "集团统一纳管", "机房配置数据", "新增"]])
    srs = _srs_with_func_type(tree, "新增")
    r = CrossDocChecker().run(rule, [fb, srs])[0]
    assert r.verdict == "pass"


def test_071_level_mismatch_fail():
    """071 一级模块在 SRS 无对应标题 → fail"""
    rule = _rule_071()
    tree = _make_srs_tree()
    fb = _fb_doc([["1", "不存在的模块", "集团统一纳管", "机房配置数据", "新增"]])
    srs = _srs_with_func_type(tree, "新增")
    r = CrossDocChecker().run(rule, [fb, srs])[0]
    assert r.verdict == "fail"
    assert "一级模块" in r.reason


def test_071_modify_type_mismatch_fail():
    """071 修改类型=新增 vs 功能类型=完善 → fail"""
    rule = _rule_071()
    tree = _make_srs_tree()
    fb = _fb_doc([["1", "统一纳管", "集团统一纳管", "机房配置数据", "新增"]])
    srs = _srs_with_func_type(tree, "完善")
    r = CrossDocChecker().run(rule, [fb, srs])[0]
    assert r.verdict == "fail"
    assert "修改类型" in r.reason


def test_071_modify_type_no_check_skipped():
    """071 功能类型无 √ 选中项 → 该行 skipped"""
    rule = _rule_071()
    tree = _make_srs_tree()
    fb = _fb_doc([["1", "统一纳管", "集团统一纳管", "机房配置数据", "新增"]])
    paras = [Paragraph(idx=10, style="Normal", text="机房配置数据"),
             Paragraph(idx=11, style="Normal", text="功能类型：□新增；□完善；□下线")]
    srs = _srs_doc(tree=tree, paragraphs=paras)
    results = CrossDocChecker().run(rule, [fb, srs])
    skipped = [r for r in results if r.verdict == "skipped"]
    assert len(skipped) == 1
    assert "功能类型" in skipped[0].reason or "无法定位" in skipped[0].reason


def test_071_location_has_row_and_section():
    """fail 结果的 location 含拆分表行号"""
    rule = _rule_071()
    tree = _make_srs_tree()
    fb = _fb_doc([["1", "不存在", "集团统一纳管", "机房配置数据", "新增"]])
    srs = _srs_with_func_type(tree, "新增")
    r = CrossDocChecker().run(rule, [fb, srs])[0]
    assert r.verdict == "fail"
    assert "行6" in r.location  # header_row=5, 第一条数据行=6


def _rule_073():
    return Rule(id="Orgs-ORG_B-Cross-073", item_name="", layer="programmatic",
                document_types=["function_breakdown", "test_report"], scope=["engineering"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B-Cross",
                checker_key="builtin:cross_doc",
                checker_params={
                    "section_path": "测试结果",
                    "mappings": [
                        {"col": "一级模块", "expected_level": 3, "level_tolerance": 1},
                        {"col": "二级模块", "expected_level": 4, "level_tolerance": 1},
                        {"col": "功能点计数项名称", "mode": "exists"},
                    ],
                })


def _rule_074():
    return Rule(id="Orgs-ORG_B-Cross-074", item_name="", layer="programmatic",
                document_types=["function_breakdown", "test_report"], scope=["new_demand"],
                severity="error", description="", pass_criteria="", fail_criteria="",
                references=[], org_id="ORG_B", group="Orgs-ORG_B-Cross",
                checker_key="builtin:cross_doc",
                checker_params={
                    "section_path": None,
                    "mappings": [
                        {"col": "新需求名称", "expected_level": 1, "level_tolerance": 0},
                        {"col": "功能点计数项名称", "expected_level": 2, "level_tolerance": 1},
                    ],
                })


def _tr_doc(tree=None, paragraphs=None):
    return Document(file_path="tr.docx", doc_type="test_report", sheets=[],
                    paragraphs=paragraphs or [], tables=[], section_tree=tree)


def _fb_doc_new(rows_data):
    """074 用的拆分表（新需求列名不同）"""
    columns = {"新需求名称": 0, "功能点计数项名称": 1}
    return Document(file_path="t.xlsx", doc_type="function_breakdown",
                    sheets=[Sheet(name="规模估算", semantic_role="estimate",
                                  header_row=5, columns=columns,
                                  data_rows=rows_data, meta_rows={})],
                    paragraphs=[], tables=[])


def test_073_exists_pass():
    """073 功能点计数项名称存在性匹配 → pass"""
    rule = _rule_073()
    l6 = SectionNode(title="机房配置数据", level=6, start_para=10, end_para=14, children=[])
    l4 = SectionNode(title="集团统一纳管", level=4, start_para=5, end_para=20, children=[l6])
    l3 = SectionNode(title="统一纳管", level=3, start_para=3, end_para=25, children=[l4])
    l1 = SectionNode(title="测试结果", level=1, start_para=0, end_para=30, children=[l3])
    tree = SectionNode(title="root", level=0, start_para=0, end_para=30, children=[l1])
    fb = _fb_doc([["1", "统一纳管", "集团统一纳管", "机房配置数据", "新增"]])
    tr = _tr_doc(tree=tree)
    r = CrossDocChecker().run(rule, [fb, tr])[0]
    assert r.verdict == "pass"


def test_073_count_name_not_found_fail():
    """073 功能点计数项名称在测试报告找不到 → fail"""
    rule = _rule_073()
    l3 = SectionNode(title="统一纳管", level=3, start_para=3, end_para=25, children=[])
    l1 = SectionNode(title="测试结果", level=1, start_para=0, end_para=30, children=[l3])
    tree = SectionNode(title="root", level=0, start_para=0, end_para=30, children=[l1])
    fb = _fb_doc([["1", "统一纳管", "集团统一纳管", "不存在的计数项", "新增"]])
    tr = _tr_doc(tree=tree)
    r = CrossDocChecker().run(rule, [fb, tr])[0]
    assert r.verdict == "fail"
    assert "功能点计数项名称" in r.reason


def test_074_new_demand_pass():
    """074 新需求测试报告匹配 → pass"""
    rule = _rule_074()
    l2 = SectionNode(title="移动云平台账号基础资费信息查询", level=2, start_para=5, end_para=10, children=[])
    l1 = SectionNode(title="关于线下基础口令需求", level=1, start_para=0, end_para=15, children=[l2])
    tree = SectionNode(title="root", level=0, start_para=0, end_para=15, children=[l1])
    fb = _fb_doc_new([["关于线下基础口令需求", "移动云平台账号基础资费信息查询"]])
    tr = _tr_doc(tree=tree)
    r = CrossDocChecker().run(rule, [fb, tr])[0]
    assert r.verdict == "pass"


def test_074_new_demand_l1_mismatch_fail():
    """074 新需求名称不匹配 → fail"""
    rule = _rule_074()
    l1 = SectionNode(title="其他需求", level=1, start_para=0, end_para=10, children=[])
    tree = SectionNode(title="root", level=0, start_para=0, end_para=10, children=[l1])
    fb = _fb_doc_new([["关于线下基础口令需求", "某功能"]])
    tr = _tr_doc(tree=tree)
    r = CrossDocChecker().run(rule, [fb, tr])[0]
    assert r.verdict == "fail"
    assert "新需求名称" in r.reason


def test_071_degraded_mode_pass():
    """降级模式：SRS 无 Heading（section_tree=None），用编号段落匹配 → pass"""
    rule = _rule_071()
    paras = [
        Paragraph(idx=0, style="Normal", text="4. 功能需求"),
        Paragraph(idx=1, style="Normal", text="4.1. 统一纳管"),
        Paragraph(idx=2, style="Normal", text="4.1.1. 集团统一纳管"),
        Paragraph(idx=3, style="Normal", text="4.1.1.1.1. 机房配置数据"),
        Paragraph(idx=4, style="Normal", text="功能类型：√新增；□完善；□下线"),
    ]
    fb = _fb_doc([["1", "统一纳管", "集团统一纳管", "机房配置数据", "新增"]])
    srs = _srs_doc(tree=None, paragraphs=paras)
    results = CrossDocChecker().run(rule, [fb, srs])
    passes = [r for r in results if r.verdict == "pass"]
    assert len(passes) >= 1


def test_071_degraded_mode_fail():
    """降级模式：编号段落中找不到对应层级 → fail"""
    rule = _rule_071()
    paras = [
        Paragraph(idx=0, style="Normal", text="4.1. 统一纳管"),
        Paragraph(idx=1, style="Normal", text="功能类型：√新增"),
    ]
    fb = _fb_doc([["1", "不存在的模块", "集团统一纳管", "机房配置数据", "新增"]])
    srs = _srs_doc(tree=None, paragraphs=paras)
    r = CrossDocChecker().run(rule, [fb, srs])[0]
    assert r.verdict == "fail"
