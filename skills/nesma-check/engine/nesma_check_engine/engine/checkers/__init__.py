"""检查器库。导入即注册到 REGISTRY。"""
from .nonnull_checker import NonnullChecker
from .enum_checker import EnumChecker
from .unique_checker import UniqueChecker
from .submission_checker import SubmissionChecker
from .numeric_relation_checker import NumericRelationChecker
from .sc_format_082_checker import ScFormat082Checker
from .cross_doc_checker import CrossDocChecker
