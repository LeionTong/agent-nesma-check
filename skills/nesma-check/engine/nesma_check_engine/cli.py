"""CLI 入口。

nesma-check-engine [--org ORG_B] [--project-type engineering]
                   [--output path] [--format json|markdown]
                   [--checklist-dir dir] [--extract-only] [--quiet]
                   <files...>
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .extract import extract
from .engine.main import run_check, aggregate_summary, validate_summary

DEFAULT_CHECKLIST = Path(__file__).parent.parent.parent / "checklist"

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nesma-check-engine",
        description="NESMA 交付物检查代理 - 程序化检查脚本底座")
    p.add_argument("files", nargs="*", help="待检查文件路径")
    p.add_argument("--org", default="ORG_B", help="组织 (默认 ORG_B)")
    p.add_argument("--project-type", default="engineering",
                   choices=["engineering","new_demand"], help="项目类型")
    p.add_argument("--output", default=None, help="报告输出路径")
    p.add_argument("--format", default="json", choices=["json","markdown"])
    p.add_argument("--checklist-dir", default=str(DEFAULT_CHECKLIST),
                   help="规则目录")
    p.add_argument("--extract-only", action="store_true",
                   help="仅提取数据产出中间 JSON")
    p.add_argument("--quiet", action="store_true", help="抑制详情")
    p.add_argument("--version", action="version",
                   version=f"nesma-check-engine {__version__}")
    return p

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.files:
        print("错误: 请提供至少一个文件路径", file=sys.stderr)
        return 3
    file_paths = []
    for f in args.files:
        p = Path(f)
        if p.is_dir():
            file_paths.extend(sorted(p.rglob("*.xlsx")) + sorted(p.rglob("*.docx")))
        elif p.exists():
            file_paths.append(p)
        else:
            print(f"错误: 文件不存在: {f}", file=sys.stderr)
            return 3
    if not file_paths:
        print("错误: 未找到有效文件", file=sys.stderr)
        return 3
    checklist_dir = Path(args.checklist_dir)
    if not checklist_dir.is_dir():
        print(f"错误: checklist 目录不存在: {checklist_dir}", file=sys.stderr)
        return 3
    documents = extract(file_paths)
    if args.extract_only:
        output_data = {
            "version": __version__,
            "run_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "documents": [d.to_dict() for d in documents],
        }
        return _output(output_data, args, exit_code=0)
    output = run_check(documents, checklist_dir=checklist_dir,
                       org=args.org, project_type=args.project_type,
                       return_summary=True)
    results = output["results"]
    summary = output["summary"]
    has_fail = summary["fail"] > 0
    has_errors = summary["errors"] > 0
    exit_code = 1 if has_fail else (2 if has_errors else 0)
    output_data = {
        "version": __version__,
        "run_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "config": {"org": args.org, "project_type": args.project_type},
        "documents": [{"file_path": d.file_path, "doc_type": d.doc_type,
                        "parsed": d.parsed, "error_msg": d.parse_error}
                       for d in documents],
        "summary": summary,
        "results": [r.to_dict() for r in results],
    }
    return _output(output_data, args, exit_code)

def _output(data: dict, args, exit_code: int) -> int:
    if args.format == "json":
        text = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    else:
        text = _to_markdown(data)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"报告已写入: {args.output}", file=sys.stderr)
    else:
        print(text)
    if not args.quiet and "summary" in data:
        s = data["summary"]
        print(f"摘要: 执行={s.get('executed',0)} 通过={s['pass']} "
              f"不通过={s['fail']} 下沉={s['skipped_semantic']}", file=sys.stderr)
    return exit_code

def _to_markdown(data: dict) -> str:
    lines = ["# NESMA 合规性检查报告（草稿）", ""]
    cfg = data.get("config", {})
    lines.append(f"**组织**: {cfg.get('org','')} | **项目类型**: {cfg.get('project_type','')} "
                 f"| **时间**: {data.get('run_id','')}")
    lines.append("")
    lines.append("## 摘要")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|------|----|")
    s = data.get("summary", {})
    lines.append(f"| 执行规则 | {s.get('executed',0)} |")
    lines.append(f"| 通过 | {s.get('pass',0)} |")
    lines.append(f"| 不通过 | {s.get('fail',0)} |")
    lines.append(f"| 下沉语义层 | {s.get('skipped_semantic',0)} |")
    lines.append("")
    lines.append("## 详情")
    lines.append("")
    lines.append("| 序号 | 规则ID | 结果 | 位置 | 说明 |")
    lines.append("|------|--------|------|------|------|")
    for i, r in enumerate(data.get("results", []), 1):
        v = {"pass":"✅","fail":"❌","skipped":"⏭️"}.get(r["verdict"], r["verdict"])
        reason = r.get("reason","")[:80]
        lines.append(f"| {i} | {r['rule_id']} | {v} | {r.get('location','')} | {reason} |")
    return "\n".join(lines)

if __name__ == "__main__":
    sys.exit(main())
