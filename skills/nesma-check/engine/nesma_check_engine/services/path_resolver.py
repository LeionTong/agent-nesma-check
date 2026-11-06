"""输出路径解析：解析 --output 参数与输入路径，确定最终文件路径。"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path

_AUTO_FILENAME = "NESMA合规性检查报告-{ts}.md"


def resolve(output_arg: str | None, first_input: Path) -> Path:
    """解析输出路径，返回最终文件 Path 并确保父目录存在。"""
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    auto_name = _AUTO_FILENAME.format(ts=ts)
    if output_arg is None:
        out_dir = Path(first_input).parent
        out_path = out_dir / auto_name
    else:
        p = Path(output_arg)
        is_dir = output_arg.endswith(("/", "\\")) or (p.suffix == "" and "." not in p.name)
        if is_dir:
            out_path = p / auto_name
        else:
            out_path = p
    out_dir = out_path.parent
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
    return out_path
