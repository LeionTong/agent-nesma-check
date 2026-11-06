"""跨文档匹配核心：归一化、层级约束匹配、存在性匹配、功能类型解析、降级模式。"""
from __future__ import annotations
import re
import unicodedata
from ...models.document import SectionNode, Paragraph

_MULTI_NUM_PREFIX_RE = re.compile(r"^(\d+[\.\、])+\s*")
_SYMBOL_RE = re.compile(r"[√□※]")

def normalize(text: str) -> str:
    """归一化文本：去空白、去编号前缀、全角转半角、去符号、小写。"""
    if not text:
        return ""
    s = text.strip()
    s = _MULTI_NUM_PREFIX_RE.sub("", s)
    s = _SYMBOL_RE.sub("", s)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", "", s)
    return s.lower()


def match_by_level(tree: SectionNode, value: str, expected_level: int,
                   tolerance: int = 1) -> bool:
    if not value or tree is None:
        return False
    norm_val = normalize(value)
    if not norm_val:
        return False
    lo = expected_level - tolerance
    hi = expected_level + tolerance
    return _search_by_level(tree, norm_val, lo, hi)


def _search_by_level(node: SectionNode, norm_val: str, lo: int, hi: int) -> bool:
    if node.level != 0 and lo <= node.level <= hi:
        if normalize(node.title) == norm_val:
            return True
    for child in node.children:
        if _search_by_level(child, norm_val, lo, hi):
            return True
    return False


def match_exists(tree: SectionNode | None, paragraphs: list[Paragraph] | None,
                 value: str) -> bool:
    """存在性匹配：有章节树时遍历所有标题，无树时遍历段落文本（子串匹配）。"""
    if not value:
        return False
    norm_val = normalize(value)
    if not norm_val:
        return False
    if tree is not None:
        return _search_exists_tree(tree, norm_val)
    if paragraphs is not None:
        return any(norm_val in normalize(p.text) for p in paragraphs)
    return False


def _search_exists_tree(node: SectionNode, norm_val: str) -> bool:
    if node.level != 0 and norm_val in normalize(node.title):
        return True
    for child in node.children:
        if _search_exists_tree(child, norm_val):
            return True
    return False


_FUNC_TYPE_RE = re.compile(r"功能类型[：:]\s*.*?√\s*(新增|完善|下线)")

MODIFY_TYPE_MAP = {"新增": "新增", "修改": "完善", "删除": "下线"}

def parse_function_type(paragraphs: list[Paragraph], start: int, end: int) -> str | None:
    """在段落区间 [start, end) 内解析功能类型 √ 选中项。"""
    for p in paragraphs:
        if start <= p.idx < end:
            m = _FUNC_TYPE_RE.search(p.text)
            if m:
                return m.group(1)
    return None


def find_section_normalized(tree: SectionNode | None, path: str | None) -> SectionNode | None:
    """归一化查找章节路径。path=None 时返回整棵树（root）。"""
    if tree is None:
        return None
    if path is None:
        return tree
    norm_path = normalize(path)
    if not norm_path:
        return tree
    return _find_in_children(tree, norm_path)


def _find_in_children(node: SectionNode, norm_path: str) -> SectionNode | None:
    for child in node.children:
        if normalize(child.title) == norm_path:
            return child
        found = _find_in_children(child, norm_path)
        if found:
            return found
    return None


_NUMBERED_PREFIX_RE = re.compile(r"^(\d+[\.\、])+")

def _count_segments(text: str) -> int:
    """从编号文本推断层级：4.1.1. → 3。无编号返回 0。"""
    m = _NUMBERED_PREFIX_RE.match(text.strip())
    if not m:
        return 0
    return m.group(0).rstrip(".、").count(".") + m.group(0).rstrip(".、").count("、") + 1


def match_by_level_degraded(paragraphs: list[Paragraph], value: str,
                            expected_level: int, tolerance: int = 1) -> bool:
    """降级模式：无章节树时从段落编号推断层级再匹配。"""
    if not value or not paragraphs:
        return False
    norm_val = normalize(value)
    if not norm_val:
        return False
    lo = expected_level - tolerance
    hi = expected_level + tolerance
    for p in paragraphs:
        level = _count_segments(p.text)
        if level == 0:
            continue
        if lo <= level <= hi and normalize(p.text) == norm_val:
            return True
    return False
