# nesma-check

按 NESMA 功能点分析法检查软件交付物。输入需求规格说明书、功能清单拆分表、测试需求说明书（`.docx` / `.xlsx`），输出逐条检查结果与扣分汇总。

规则来自两层：GB/T 42588 的通用条款，以及两个客户组织各自的定制验收标准。通用层与组织层分开存放，用 `--org` 选择走哪一套。

## 结构

```text
skills/nesma-check/
├── checklist/
│   ├── Base-All-{Data,Transaction}.yaml      通用条款
│   ├── Orgs-ORG_A-{Cross,Data,Format,Transaction}.yaml
│   └── Orgs-ORG_B-{Cross,Data,Format,Transaction}.yaml
├── engine/                                    检查引擎（Python）
│   ├── nesma_check_engine/{extract,engine,models,services}
│   └── tests/                                 pytest 用例
├── references/                                工作流、字段映射、提示词、报告模板、标准原文
└── assets/                                    交付物模板（自备）
```

`checklist/*.yaml` 每条规则带 `layer`（syntactic / semantic）、`severity`、`pass_criteria`、`fail_criteria`，与之对应的检查器在 `engine/nesma_check_engine/engine/checkers/`。纯结构校验走程序化检查，语义判断走提示词（`references/llm-prompts.md`）。

## 安装

```bash
cd skills/nesma-check/engine
uv venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

要求 Python 3.10 以上。依赖 `openpyxl`、`python-docx`、`PyYAML`。

## 用法

```bash
nesma-check-engine --org ORG_B --project-type new_demand \
  --format markdown --output report.md \
  requirement.docx function-list.xlsx test-requirement.docx
```

参数：

| 参数 | 说明 |
|---|---|
| `--org` | 组织分支，取值 `ORG_A` 或 `ORG_B`，默认 `ORG_B` |
| `--project-type` | `engineering` 或 `new_demand` |
| `--format` | `json` 或 `markdown`，默认 `json` |
| `--output` | 报告输出路径，不给则打印到标准输出 |
| `--checklist-dir` | 规则目录，默认 `skills/nesma-check/checklist` |
| `--extract-only` | 只抽取文档数据，输出中间 JSON，不跑检查 |

文件参数可以给目录，引擎会递归找 `.xlsx` 与 `.docx`。

退出码：`0` 检查完成，`3` 参数或文件有问题。

## 测试

```bash
uv run --with pytest --with pyyaml --with openpyxl --with python-docx pytest tests -q
```

## 组织分支

两套组织规则集的内容不同，取自两个客户各自的功能点计数验收标准。`ORG_A` 多几类文档要求（系统概详要设计说明书、需求评审表、汇报PPT）；`ORG_B` 按项目类型区分规则适用范围，跨文档与格式两组里有只对 `new_demand` 或只对 `engineering` 生效的条目。接入新组织时复制一套 `Orgs-*.yaml` 改 `org_id`，再把对应检查器补上。

模板原件含客户名称与项目编号，不入库。放模板的约定见 `skills/nesma-check/assets/README.md`。

## 许可

MIT，见 `LICENSE`。
