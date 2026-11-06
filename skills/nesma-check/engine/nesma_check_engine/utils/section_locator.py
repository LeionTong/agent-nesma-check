"""docx 章节树构建与查询。扫描 Heading 段落按层级嵌套。"""
from __future__ import annotations
from ..models.document import Paragraph, SectionNode

def build_section_tree(paragraphs: list[Paragraph]) -> SectionNode | None:
    headings = [(p.idx, _heading_level(p.style), p.text)
                for p in paragraphs if p.style.startswith("Heading")]
    if not headings:
        return None
    root = SectionNode(title="root", level=0, start_para=0,
                       end_para=len(paragraphs), children=[])
    stack: list[SectionNode] = [root]
    for i, (para_idx, level, title) in enumerate(headings):
        next_idx = headings[i + 1][0] if i + 1 < len(headings) else len(paragraphs)
        node = SectionNode(title=title, level=level, start_para=para_idx,
                           end_para=next_idx, children=[])
        while len(stack) > 1 and stack[-1].level >= level:
            stack.pop()
        stack[-1].children.append(node)
        stack.append(node)
    _fix_end_paras(root)
    return root

def _fix_end_paras(node: SectionNode) -> int:
    """回填: 父节点 end_para = max(自身 end_para, 最末子节点 end_para)。"""
    if node.children:
        max_child_end = max(_fix_end_paras(c) for c in node.children)
        node.end_para = max(node.end_para, max_child_end)
    return node.end_para

def _heading_level(style: str) -> int:
    parts = style.split()
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1])
    return 1
