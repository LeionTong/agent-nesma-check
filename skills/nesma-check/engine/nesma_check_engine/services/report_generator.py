"""报告生成器：三级 Markdown 报告渲染 + 格式验证。"""
from __future__ import annotations

_DOC_TYPE_NAMES = {
    "srs": "需求说明书",
    "function_breakdown": "功能清单拆分表",
    "test_report": "测试报告",
    "technical_specification": "技术规范书",
    "spds": "系统概详要设计说明书",
    "demand_review_form": "需求评审表",
    "ppt": "汇报PPT",
}


def _project_info(output: dict) -> str:
    cfg = output.get("config", {})
    lines = ["## 一、项目信息", "",
             "| 项目 | 值 |", "|------|-----|",
             f"| 项目类型 | {cfg.get('project_type', '')} |",
             f"| 所属组织 | {cfg.get('org', '')} |",
             f"| 规则版本 | v{output.get('version', '')} |"]
    return "\n".join(lines)


def _document_info(output: dict) -> str:
    lines = ["## 二、检查范围-文档信息", "",
             "| 文档类型 | 文件名 | 状态 |", "|----------|--------|------|"]
    for d in output.get("documents", []):
        type_name = _DOC_TYPE_NAMES.get(d.get("doc_type", ""), d.get("doc_type", ""))
        fname = d.get("file_path", "")
        if d.get("parsed"):
            status = "✅已读取"
        else:
            err = d.get("error_msg", "")
            status = f"❌未读取({err})" if err else "❌未读取"
        lines.append(f"| {type_name} ({d.get('doc_type', '')}) | {fname} | {status} |")
    return "\n".join(lines)
