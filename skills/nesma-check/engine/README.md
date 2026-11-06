# nesma-check-engine

NESMA 交付物检查代理 — 程序化检查脚本底座（SP-1）。

## 安装

```sh
pip install -e .
```

依赖：Python 3.10+，openpyxl，python-docx，PyYAML。

## 使用

```sh
# 基本用法（JSON 输出到 stdout）
nesma-check-engine 拆分表.xlsx SRS.docx 测试报告.docx

# 指定组织和项目类型
nesma-check-engine --org ORG_B --project-type engineering 拆分表.xlsx

# Markdown 格式
nesma-check-engine --format markdown 拆分表.xlsx

# 输出到文件
nesma-check-engine --output report.json 拆分表.xlsx SRS.docx

# 仅提取中间 JSON（不执行检查）
nesma-check-engine --extract-only 拆分表.xlsx
```

### 参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `--org` | 组织 | `ORG_B` |
| `--project-type` | 项目类型 | `engineering` |
| `--output` | 报告输出路径 | stdout |
| `--format` | 输出格式 | `json` |
| `--checklist-dir` | 规则目录 | `../checklist` |
| `--extract-only` | 仅提取数据 | False |
| `--quiet` | 抑制详情 | False |
| `--version` | 版本 | — |

### 退出码

| 码 | 含义 |
|----|------|
| 0 | 全部 pass 或 skipped |
| 1 | 存在 fail |
| 2 | 存在检查器内部错误 |
| 3 | 参数错误 / 文件不可读 |

## 架构

```
文档 → extract（每文件只读一次）→ 中间 JSON → checkers → results → summary 聚合
```

- **数据流单向**：检查器不回源文件，只消费中间 Document 对象
- **summary 程序化聚合**：由 results 统计生成，自校验不一致则终止
- **规则分派**：硬编码 DISPATCH 表（`rule_loader.py`），不改 checklist YAML
- **scope 过滤**：加载阶段完成，仅匹配 project_type 的规则进入执行队列

### 程序化规则（16 条可执行 + 7 条下沉语义层）

| 规则 | 检查器 | 说明 |
|------|--------|------|
| 063-066 | submission | 提交完备性（文件集存在性） |
| 067-070 | — (skipped) | 模板合规性（模板不固定，下沉语义层） |
| 079 | nonnull | 必填列非空 |
| 080 | enum | 类别枚举值（ILF/ELF/EIF/EI/EO/EQ） |
| 081 | enum | 重用程度枚举值（低/中/高） |
| 082 | builtin:sc_format_082 | 修改/删除功能重用程度检查 |
| 087 | enum | 修改类型枚举值（新增/修改/删除） |
| 091 | — (skipped) | 下沉语义层 |
| 093 | unique | 功能点计数项名称唯一 |
| 095 | unique | 功能项描述唯一 |
| 071 | builtin:cross_doc | 跨文档层级对应：拆分表↔SRS |
| 072 | builtin:cross_doc | 跨文档层级对应：新需求拆分表↔SRS |
| 073 | builtin:cross_doc | 存在性匹配：拆分表↔测试报告 |
| 074 | builtin:cross_doc | 层级匹配：新需求拆分表↔测试报告 |
| 075 | — (skipped) | 无技术规范书模板，下沉语义层 |
| 096 | — (skipped) | 下沉语义层 |
| 097 | numeric_relation | 开发费用数值关系（C20-C27 ≤ C22） |

### JSON 输出结构

```json
{
  "version": "0.1.0",
  "run_id": "20260701-1530",
  "config": {"org": "ORG_B", "project_type": "engineering"},
  "documents": [{"file_path": "...", "doc_type": "...", "parsed": true}],
  "summary": {"total_rules": 21, "executed": 12, "pass": 8, "fail": 3, "skipped_semantic": 10, "errors": 0},
  "results": [{"rule_id": "...", "verdict": "...", "location": "...", "evidence": "...", "reason": "..."}]
}
```

## 测试

```sh
pytest
```

151 个测试覆盖：单元（checkers）、集成（readers）、端到端（CLI），含 59 个跨文档一致性检查新增测试。

## 目录结构

```
engine/
├── pyproject.toml
├── nesma_check_engine/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口
│   ├── extract.py          # 一次性提取
│   ├── models/             # 数据模型（Rule/Document/CheckResult）
│   ├── services/           # 文档读取（xlsx_reader/docx_reader/doc_parser）
│   ├── utils/              # 工具（sheet_locator/section_locator/location/logger）
│   └── engine/             # 检查引擎
│       ├── rule_loader.py  # 规则加载 + DISPATCH 分派表
│       ├── rule_router.py  # org/scope/layer 过滤
│       ├── main.py         # 编排主流程 + summary 聚合
│       ├── checkers/       # 检查器库
│       │   ├── cross_doc_matcher.py   # 跨文档匹配核心（归一化/层级/存在性/功能类型/降级）
│       │   └── cross_doc_checker.py   # 跨文档层级对应检查器
└── tests/
    ├── fixtures/           # 真实测试数据（.gitignore 忽略）
    ├── test_checkers/      # 单元测试
    ├── test_e2e.py         # 端到端测试
    └── ...
```
