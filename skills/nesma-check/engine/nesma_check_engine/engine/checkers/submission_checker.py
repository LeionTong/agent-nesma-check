"""submission_checker（063-066）：提交完备性，检查文档集是否含所有 require 的 doc_type。"""
from __future__ import annotations
from ...models.rule import Rule
from ...models.document import Document
from .base import BaseChecker, register

@register("submission")
class SubmissionChecker(BaseChecker):
    def run(self, rule: Rule, document: Document | list[Document]) -> list:
        docs = document if isinstance(document, list) else [document]
        require: list[str] = rule.checker_params["require"]
        present = {d.doc_type for d in docs if d.parsed}
        missing = [t for t in require if t not in present]
        if not missing:
            return [self._pass(rule, f"已提交: {', '.join(require)}")]
        evidence = f"缺少: {', '.join(missing)}"
        return [self._fail(rule, [], evidence,
                           f"提交完备性检查未通过——缺少文档类型: {', '.join(missing)}")]
