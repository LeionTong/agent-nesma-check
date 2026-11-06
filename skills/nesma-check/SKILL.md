---
name: nesma-check
description: 检查工作量评估文档是否符合 NESMA 规范。用于需求说明书(SRS)、功能清单拆分表、测试报告的 NESMA 合规性检查。
argument-hint: <文件路径或目录> [--org <组织>] [--project-type <项目类型>] [--output <报告路径>]
compatibility: 需要 .claude/skills/ 目录下存在 nesma-check docx xlsx 技能
user-invocable: true
llm-check-enabled: true
metadata:
  author: LeiTong
  source: nesma-check/SKILL.md
---
# NESMA Check Skill

NESMA 合规检查引擎：检查工作量评估文档是否符合 NESMA (Netherlands Software Metrics Association) 规范。用于需求说明书(SRS)、功能清单拆分表、测试报告的 NESMA 合规性检查。

## 触发命令

```sh
/nesma-check [--org <组织>] [--project-type <项目类型>] [--output <报告路径或目录>] <文件路径或目录> [<文件路径2> ...]
# 示例1：指定逐个文件路径
/nesma-check --org ORG_B --project-type new_demand --output @test/report.md @test/需求说明书.docx @test/功能清单拆分表.docx @test/测试需求说明书.docx 
# 示例2：指定目录路径
/nesma-check --org ORG_B --project-type new_demand --output @test/202605-nesma/ @test/202605-nesma/ 
# 示例3：省略 --output，报告默认落在首个输入路径所在目录，自动命名为 NESMA合规性检查报告-YYYYMMDD-HHmm.md
/nesma-check --org ORG_B --project-type new_demand @test/需求说明书.docx
```

## 支持的文档类型

| 文档类型                    | 说明                                |
| --------------------------- | ----------------------------------- |
| `srs`                     | 需求说明书                          |
| `function_breakdown`      | 功能清单拆分表（NESMA 拆分表）      |
| `test_report`             | 测试报告                            |
| `technical_specification` | 技术规范书                          |
| `spds`                    | 系统概详要设计说明书（ORG_A 特有） |
| `demand_review_form`      | 需求评审表（ORG_A 特有）           |
| `ppt`                     | 汇报PPT（ORG_A 特有）              |

## 支持的文档格式

## 参数说明

| 参数               | 说明                               | 可选值                                                                                                                                                 |
| ------------------ | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `--org`          | 组织分支                           | `ORG_B`、`ORG_A`                                                                                                         |
| `--project-type` | 项目类型                           | `engineering`（工程类）、`new_demand`（新需求类）                                                                                                  |
| `--output`       | 指定报告输出路径（文件路径或目录） | 文件路径或目录路径；目录路径或省略时自动生成`NESMA合规性检查报告-YYYYMMDD-HHmm.md`（时间戳精确到分钟）；省略时默认取**首个输入路径**的所在目录 |

不指定 `--org`/`--project-type` 时使用基础规则（`checklist/Base-All-*.yaml` 目录下所有规则）。

## 前置依赖

| 依赖       | 检测方式                         | 不可用时的错误信息                                                    |
| ---------- | -------------------------------- | --------------------------------------------------------------------- |
| docx skill | `pandoc --version`             | `错误: docx skill 未安装，请先安装 docx skill 后再使用 nesma-check` |
| xlsx skill | `python3 -c "import openpyxl"` | `错误: xlsx skill 未安装，请先安装 xlsx skill 后再使用 nesma-check` |

## 规则体系（v3.0.0）

规则按类别组织在 `checklist/` 目录下，自动发现加载。规则按 `group` 前缀和文件名前缀双重匹配：

| 类别              | 文件                                       | 说明                     |
| ----------------- | ------------------------------------------ | ------------------------ |
| 基础-数据功能     | `checklist/Base-All-Data.yaml`           | ILF/EIF 相关规则         |
| 基础-事务功能     | `checklist/Base-All-Transaction.yaml`    | EI/EO/EQ 相关规则        |
| ORG_B-数据功能   | `checklist/Orgs-ORG_B-Data.yaml`        | ORG_B ILF/EIF 特有规则  |
| ORG_B-事务功能   | `checklist/Orgs-ORG_B-Transaction.yaml` | ORG_B EI/EO/EQ 特有规则 |
| ORG_B-格式检查   | `checklist/Orgs-ORG_B-Format.yaml`      | ORG_B 格式/完备性规则   |
| ORG_B-跨类型验证 | `checklist/Orgs-ORG_B-Cross.yaml`       | ORG_B 跨文档一致性规则  |
| ORG_A-数据功能   | `checklist/Orgs-ORG_A-Data.yaml`        | ORG_A ILF/EIF 特有规则  |
| ORG_A-事务功能   | `checklist/Orgs-ORG_A-Transaction.yaml` | ORG_A EI/EO/EQ 特有规则 |
| ORG_A-格式检查   | `checklist/Orgs-ORG_A-Format.yaml`      | ORG_A 格式/完备性规则   |
| ORG_A-跨类型验证 | `checklist/Orgs-ORG_A-Cross.yaml`       | ORG_A 跨文档一致性规则  |

- 组织规则按 `--org` 参数过滤（如 `--org ORG_B` 只加载 `Orgs-ORG_B-*.yaml`）
- 项目类型按规则内部 `scope` 字段过滤（如 `--project-type engineering` 只执行 `scope` 包含 `engineering` 的规则）
- 规则 ID 格式：`{Group}-{Classification}-{No.}`（如 `Base-All-Data-001`、`Orgs-ORG_B-Format-063`）

详见 `references/router.md`。

## 执行流程

详见 `references/main-workflow.md`。

**关键流程**：

1. 接收并验证文件 + 解析参数
2. 检测 docx/xlsx skills 可用性
3. 加载规则（自动发现 `checklist/`）
4. 读取文档内容 + 识别文档类型
5. 执行分项检查（两层架构：程序化 + LLM 语义）
6. 生成检查报告（三级结构：摘要→详情→建议）
7. 验证报告格式

## 两层检查架构

| 层                    | 职责                                       | 执行方式 |
| --------------------- | ------------------------------------------ | -------- |
| Layer 1: 程序化检查   | 格式、编号、必填字段、数值范围、提交完备性 | 直接检查 |
| Layer 2: LLM 语义检查 | 分类准确性、复杂度评估、跨文档一致性       | LLM 会话 |

**冲突解决**：语义层结果优先，记录冲突供人工审核。

## 输出格式（规则结构）

每条规则的 YAML 格式：

```yaml
- id: Base-All-Data-001
  item_name: 逻辑文件唯一性检查
  layer: semantic                          # semantic | programmatic
  document_types: [function_breakdown]    # 适用文档类型列表
  scope: [engineering, new_demand]       # 适用项目类型
  description: |                          # 规则描述
    ...

**位置格式**：使用分号分隔多行位置（如 `行1; 行2; 行3`）。

## LLM 置信度机制

| 置信度 | 范围 | 处理方式 | 报告展示 |
|--------|------|----------|----------|
| 高/中 | >= 0.6 | verdict 直接采用 | ✅ 通过 / ❌ 不通过 |
| 低 | < 0.6 | verdict + "待复核" | ⚠️ 通过,待复核 / ⚠️ 不通过,待复核 |

## 错误处理

| 场景 | 处理方式 |
|------|----------|
| 文件不存在 | 报错：文件路径无效 |
| 参数值不合法 | 报错：参数值不在可选范围内 |
| docx skill 不可用 | 报错：docx skill 未安装，请先安装 |
| xlsx skill 不可用 | 报错：xlsx skill 未安装，请先安装 |
| 规则 YAML 格式错误 | 报错：提示具体文件和错误信息 |
| 空文档 | 警告后继续检查 |
| 大文档 | 分片处理后合并结果 |
| 写入文件失败 | 报错：无法写入报告文件，说明原因 |
| LLM 服务不可用 | 阻塞等待，超时后报错（不降级运行） |
```
