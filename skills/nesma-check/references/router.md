# NESMA 规则路由器

**版本**: 3.0.0
**日期**: 2026-06-23
**说明**: v3.0.0 规则加载逻辑，基于 `checklist/` 目录扁平 YAML 文件结构。

## 参数定义

| 参数 | 必填 | 可选值 | 说明 |
|------|------|--------|------|
| `--org` | 否 | `ORG_B`、`ORG_A` | 组织分支 |
| `--project-type` | 否 | `engineering`（工程类）、`new_demand`（新需求类） | 项目类型 |

## 目录结构

```
checklist/
├── Base-All-Data.yaml           # 基础数据功能规则 (11 条, 001-011)
├── Base-All-Transaction.yaml    # 基础事务功能规则 (51 条, 012-062)
├── Orgs-ORG_B-Data.yaml         # ORG_B 数据功能规则 (7 条, 098,102-103,108-111)
├── Orgs-ORG_B-Transaction.yaml  # ORG_B 事务功能规则 (11 条, 083-086,099-101,104-107)
├── Orgs-ORG_B-Format.yaml      # ORG_B 格式检查规则 (26 条, 063-070,076-082,087-097)
├── Orgs-ORG_B-Cross.yaml       # ORG_B 跨类型验证规则 (5 条, 071-075)
├── Orgs-ORG_A-Data.yaml        # ORG_A 数据功能规则 (14 条, 139-143,145-153)
├── Orgs-ORG_A-Transaction.yaml  # ORG_A 事务功能规则 (1 条, 144)
├── Orgs-ORG_A-Format.yaml      # ORG_A 格式检查规则 (22 条, 112-133)
└── Orgs-ORG_A-Cross.yaml       # ORG_A 跨类型验证规则 (5 条, 134-138)

# 总计 153 条规则
```

## 加载逻辑

### 自动发现

系统自动加载 `checklist/` 目录下的所有 YAML 文件。

### 加载顺序（优先级低 → 高）

1. `checklist/Base-All-*.yaml` ← 基础规则（无 org，全部加载）
2. `checklist/Orgs-{org}-*.yaml` ← 组织规则（按 `--org` 参数过滤）

### 路由逻辑

| 输入 | 加载文件 |
|------|---------|
| （无参数） | `Base-All-*.yaml`（62 条基础规则） |
| `--org ORG_B` | `Base-All-*.yaml` + `Orgs-ORG_B-*.yaml`（111 条） |
| `--org ORG_A` | `Base-All-*.yaml` + `Orgs-ORG_A-*.yaml`（104 条） |
| `--org ORG_B --project-type engineering` | 同上，但规则内部按 `scope: [engineering]` 过滤 |
| `--org ORG_B --project-type new_demand` | 同上，但规则内部按 `scope: [new_demand]` 过滤 |

### 规则 ID 格式

```
{Group}-{Classification}-{No.}

示例：
- Base-All-Data-001          (基础-数据功能-001)
- Base-All-Transaction-012   (基础-事务功能-012)
- Orgs-ORG_B-Format-063     (ORG_B组织-格式检查-063)
- Orgs-ORG_A-Data-139      (ORG_A组织-数据功能-139)
```

## 规则字段说明

每条规则 YAML 格式：

```yaml
- id: Base-All-Data-001
  item_name: 逻辑文件唯一性检查
  layer: semantic              # semantic | programmatic
  document_types: [function_breakdown]  # 适用文档类型列表
  scope: [engineering, new_demand]     # 适用项目类型
  description: |
    规则描述...
  pass_criteria: |
    通过条件...
  fail_criteria: |
    不通过条件...
  severity: error
  references:
    - GB-T42588-2023 §6.3.1
  example: |                   # 可选
    示例...
```

### layer 字段

- `programmatic`（~80 条）：程序化检查，直接检查文档内容，无需 LLM
- `semantic`（~73 条）：LLM 语义检查，需要调用 LLM 进行上下文理解

### document_types 字段

| 值 | 含义 |
|----|------|
| `srs` | 需求说明书 |
| `function_breakdown` | 功能清单拆分表（NESMA 拆分表） |
| `test_report` | 测试报告 |
| `technical_specification` | 技术规范书 |
| `spds` | 系统概详要设计说明书（ORG_A 特有） |
| `demand_review_form` | 需求评审表（ORG_A 特有） |
| `ppt` | 汇报PPT（ORG_A 特有） |

## 错误处理

- 规则 YAML 格式错误 → **报错**，提示具体文件和错误信息
- 目录不存在 → **报错**，要求创建 `checklist/` 目录结构
- 无匹配规则文件 → **警告**，但继续执行

## 引用关系

本文件引用以下规则目录：

- `checklist/` — 所有规则文件（153 条，v3.0.0）