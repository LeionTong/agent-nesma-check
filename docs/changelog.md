# Changelog

## v3.1.1 (2026-06-30)

### 参考目录扁平化重构

`skills/nesma-check/references/` 目录结构调整与溯源指针同步：

- **目录扁平化**：删除 `rules@20260618/`、`rules@20260625/` 等快照子目录，所有参考文件直接置于 `references/` 根目录
- **命名统一**：合并规则快照统一为 `checklist@<date>.{md,xlsx}`；第三方审计标准统一为 `ref-<source>-review.{md,xlsx}`（如 `ref-cq-review`、`ref-ceprei-review`）
- **溯源指针同步**：`checklist/*.yaml` 与 `references/checklist@20260625.md` 中的 `references:` 字段由旧名（`cq-review-rules.md`、`ceprei-review-rules.md`）更新为新名，`idNN` 后缀原样保留
- **SKILL.md 导航**：参考文件导航表新增合并规则快照与审计标准条目
- **无行为变化**：规则内容、规则 ID、`/nesma-check` 检查结果均未改变（153 条规则，SHA256 一致）；本次为知识库结构整理，非破坏性变更

## v3.1.0 (2026-06-25)

### 报告输出路径默认行为（BREAKING）

省略 `--output` 参数时的行为变更：

- **旧行为**：报告仅显示在对话界面，不写入文件（`2026-04-12-fix-nesma-report-bugs` 引入）
- **新行为**：默认写入**首个输入路径**的所在目录，并自动生成文件名
  - 单文件输入 → 文件所在目录；多文件输入 → 首个文件所在目录；目录输入 → 该目录本身
  - 自动文件名：`NESMA合规性检查报告-YYYYMMDD-HHmm.md`（时间戳精确到分钟，避免同日多次运行覆盖）
- **对话输出策略**：报告写入文件后，对话界面仅显示文件路径 + 检查摘要（通过/不通过/不适用计数 + 整体结论），不再贴报告全文
- **统一文件名规则**：显式指定 `--output` 为目录路径时，文件名从 `NESMA合规性检查报告-YYYYMMDD.md`（仅到日）升级为带时分的统一格式
- **迁移**：依赖旧"仅对话显示、不落盘"行为的调用方需改用显式 `--output`，或自行从对话提取

## v2.0.0 (2026-06-02)

### 规则引擎重建（Phase 1）

- 规则体系从静态 Markdown 重建为标准化 YAML，一个文件一条规则
- 62 条规则按类别组织：data-functions（15）、transaction-functions（20）、cross-validation（15）、format（12）
- 自动发现加载：`rules/base/{category}/*.yaml`
- 组织覆盖：`rules/orgs/ORG_B/{project-type}.yaml`
- `_base-rules.md` 重命名为 `_base-rules-reference.md`（不再直接加载）

### 架构重设计（Phase 2）

- 两层检查架构：Layer 1 程序化检查（~38 项）+ Layer 2 LLM 语义检查（~24 项）
- 工作流定义单一来源：`main-workflow.md`（SKILL.md 只引用不重复）
- LLM 检查配置：置信度机制（高/中直接采用，低置信度待复核）
- 冲突解决策略：语义层结果优先，记录冲突供人工审核

### 输出质量提升（Phase 3）

- 报告三级结构：摘要→详情→建议
- 8 列输出格式：序号、分类、检查项、结果、位置、说明、严重级别、建议
- 每个"不通过"结果必须包含修改建议和标准引用
- 位置格式：分号分隔多行引用（`行1; 行2; 行3`）
- 删除所有验证脚本，改为 prompt 约束验证

### 文档更新（Phase 4）

- 重写 `docs/roadmap.md`：按 Phase 1-4 组织的项目路线图
- 更新 `docs/system-architecture.drawio`：v2.0 两层架构图
- 补全 `references/llm-prompts.md`：19 条语义规则全覆盖，统一 JSON 输出格式
- 旧检查项编号 → 新规则 ID 映射表

## v0.3.0 (2026-05-12)

### LLM 语义检查

NESMA Check Skill 从纯程序化检查升级为两层检查架构：

- **Layer 1 程序化检查（11 项）**：模板校验、类别验证、命名规范、唯一性检查等
- **Layer 2 LLM 语义检查（44 项）**：功能点定义合规、跨文档对应关系、ILF/EI/EQ 关系验证、描述质量评估等
- **Subagent 并行**：需求说明书、NESMA 功能清单、测试报告三路并行检查
- **置信度评分**：高/中置信度直接采用，低置信度标注"待复核"

### 报告模板优化

- 3.3 检查详情表新增"分类"列（7 列 → 8 列）
- 位置格式规范简化：统一为 `行{N}; 行{N}; ... (共XX行)`
- 验证脚本同步更新，支持更多位置格式（行范围、约数、N/A 等）

### 规则体系

- ORG_B 检查单精简（65 → 62 项）
- 新增 LLM 检查配置文档和 44 项 prompt 模板

## v0.2.0 (2026-04-29)

### 规则重构

- 拆分基础规则为项目类型特定文件（`_base-rules.md` + `ORG_B-工程项目-checklist.md` / `ORG_B-新需求项目-checklist.md`）
- 新增规则路由（`router.md`），按 `--org` + `--project-type` 参数加载对应规则
- 移除 cui_ah 组织规则，聚焦 ORG_B

### 报告验证

- 新增检查表格式验证脚本（列数、列顺序、位置格式、行顺序）
- 新增输出范围验证脚本（footer 检测、终止标记、越界内容）
- 位置信息格式标准化：`行{N}, 列{Col}` → 脚本化格式化

### 文档与工具

- 新增路线图、架构设计文档
- 新增 docx/xlsx 技能说明和格式转换前置检查
- 新增批量 markdown 转换脚本
- 精简 SKILL.md，移除冗余内容

## v0.1.0 (2026-04-10)

### 初始版本

- 项目初始化：NESMA Check Skill 基础框架
- 基础规则文档（`_base-rules.md`，~2650 行）
- 主工作流定义（接收文件 → 检测依赖 → 加载规则 → 读取文档 → 执行检查 → 生成报告）
- 通过 docx skill（pandoc）读取 Word 文档，xlsx skill（openpyxl）读取 Excel 表格
- 报告模板（标准 Markdown 格式）
- OpenSpec 归档：remove-complexity-calculation、restructure-nesma-standards
