# NESMA LLM 语义检查 Prompt 模板

**版本**: 3.0.0
**日期**: 2026-06-23
**说明**: 所有 `layer: semantic` 规则的 Prompt 模板，按规则类别分组。共 73 条语义规则。

## 使用方式

在 Subagent 中，对每个检查项使用对应的 Prompt 模板调用 LLM。

## 统一输出格式

所有 Prompt 的输出 MUST 使用以下 JSON 格式：

```json
{
  "verdict": "pass|fail|uncertain",
  "confidence": 0.0-1.0,
  "reason": "判断理由",
  "location": "位置信息",
  "evidence": "原始内容片段"
}
```

## 置信度指导

| 等级 | 范围 | 含义 |
|------|------|------|
| 高 | 0.85 - 1.0 | 证据充分，语义明确 |
| 中 | 0.60 - 0.85 | 证据较充分，基本清晰 |
| 低 | 0.00 - 0.60 | 证据不足，需人工复核 |

confidence < 0.6 时，verdict 后附加"待复核"。

---

## 一、Base-All-Data 语义规则

### Base-All-Data-003: ILF 复杂度评估

```markdown
## 规则 Base-All-Data-003: ILF 复杂度评估必须符合 NESMA 复杂度矩阵

### 任务
验证 ILF 的复杂度评估是否符合 NESMA 标准复杂度矩阵（DET × RET）。

### 输入
- 功能名称: {function_name}
- 功能类型: ILF
- DET 数量: {det_count}（数据元素类型）
- RET 数量: {ret_count}（记录元素类型）
- 当前评估复杂度: {current_complexity}

### NESMA 复杂度矩阵

| RET \ DET | 1-19 DET | 20-50 DET | >50 DET |
|-----------|----------|-----------|---------|
| 1 RET | 低 | 低 | 中 |
| 2-5 RET | 低 | 中 | 高 |
| >5 RET | 中 | 高 | 高 |

### 判定标准
- pass: 当前复杂度与矩阵匹配
- fail: 当前复杂度与矩阵不匹配
- uncertain: DET/RET 数据不足，无法判断

### 参考
GB/T 42588-2023 §6.2.4
```

### Base-All-Data-007: ILF 与 EIF 正确区分

```markdown
## 规则 Base-All-Data-007: ILF 必须与 EIF 正确区分（基于数据所有权）

### 任务
验证被标记为 ILF 的数据存储是否确实由本系统拥有和维护，而非外部系统。

### NESMA 规范
- ILF: 由本应用维护的内部逻辑数据组
- EIF: 由外部系统维护、本应用只读引用的外部接口数据

### 判定标准
- pass: 数据确实由本系统拥有和维护
- fail: 数据实际由外部系统拥有，应归类为 EIF
- uncertain: 数据所有权不明确

### 参考
GB/T 42588-2023 §6.2.7
```

---

## 二、Base-All-Transaction 语义规则

### Base-All-Transaction-012: 基本过程识别规则检查

```markdown
## 规则 Base-All-Transaction-012: 识别的功能必须是一个基本过程

### 任务
验证 NESMA 拆分表中的每个功能是否满足基本过程定义。

### NESMA 基本过程定义
1. 对用户具有独立存在的意义，执行一个完整的信息处理过程
2. 执行完毕后应用程序处于稳定状态
3. 不能将子系统、模块等过大功能单元作为基本过程
4. 必须站在用户业务视角而非技术视角
5. 基本过程应包含从开始到结束的所有正常和异常情况

### 判定标准
- pass: 所有功能满足基本过程条件
- fail: 存在不符合基本过程条件的功能
- uncertain: 功能描述不足以判断

### 参考
GB-T42588-2023 §9.1, §10.1, §11.1
```

### Base-All-Transaction-018: EI 类别与功能描述一致性检查

```markdown
## 规则 Base-All-Transaction-018: EI 类别与功能描述必须一致

### 任务
验证类别为 EI 的功能的描述是否符合 EI 定义。

### EI 定义
- 数据/控制信息从应用边界外输入
- 对一个或多个 ILF 进行新增/更改/删除操作

### 判定标准
- pass: EI 功能描述符合 EI 定义
- fail: EI 功能描述不符合 EI 定义
- uncertain: 描述不明确

### 参考
GB-T42588-2023 §9.1, §9.2.1, §9.2.12
```

### Base-All-Transaction-019: EO 类别与功能描述一致性检查

```markdown
## 规则 Base-All-Transaction-019: EO 类别与功能描述必须一致

### 任务
验证类别为 EO 的功能的描述是否符合 EO 定义。

### EO 定义
- 输出产品跨越应用边界
- 输出规模大小不等或需要进一步数据处理
- 不能仅是简单查询

### 判定标准
- pass: EO 功能描述符合 EO 定义
- fail: EO 功能描述不符合 EO 定义
- uncertain: 描述不明确

### 参考
GB-T42588-2023 §10.1, §10.2.1, §10.2.2
```

### Base-All-Transaction-021: EQ 类别与功能描述一致性检查

```markdown
## 规则 Base-All-Transaction-021: EQ 类别与功能描述必须一致

### 任务
验证类别为 EQ 的功能的描述是否符合 EQ 定义。

### EQ 定义
- 独特的输入/输出组合
- 输出规模明确，不需要进一步数据处理
- 输入部分的数据应能够唯一地标识所需的输出

### 判定标准
- pass: EQ 功能描述符合 EQ 定义
- fail: EQ 功能描述不符合 EQ 定义
- uncertain: 描述不明确

### 参考
GB-T42588-2023 §11.1
```

---

## 三、跨文档一致性规则

### Orgs-ORG_B-Cross-071: NESMA拆分表与需求说明书层级对应检查(工程类)

```markdown
## 规则 Orgs-ORG_B-Cross-071: NESMA拆分表与需求说明书层级必须对应

### 任务
验证 NESMA 拆分表各层级与需求说明书目录层级是否一一对应。

### 对应关系
- NESMA【一级模块】←→ SRS【4.X.X目录】
- NESMA【二级模块】←→ SRS【4.X.X.X目录】
- NESMA【功能点计数项名称】←→ SRS【4.X.X.X.X.X目录】
- NESMA【修改类型】←→ SRS【功能类别(新增/完善/下线)】

### 判定标准
- pass: 所有层级一一对应
- fail: 存在不匹配的层级
- uncertain: 目录结构不明确

### 参考
重庆设计院审计标准43
```

### Orgs-ORG_A-Cross-134: NESMA拆分表与需求说明书层级对应检查(GD版)

```markdown
## 规则 Orgs-ORG_A-Cross-134: NESMA拆分表与需求说明书层级必须对应(GD版)

### 任务
验证 NESMA 拆分表各层级与需求说明书目录层级是否一一对应。

### 对应关系
- NESMA【一级模块】←→ SRS【X.X目录】
- NESMA【二级模块】←→ SRS【X.X.X目录】
- NESMA【三级模块】←→ SRS【X.X.X.X目录】
- NESMA【四级模块】←→ SRS【X.X.X.X目录】

### 判定标准
- pass: 所有层级一一对应
- fail: 存在不匹配的层级
- uncertain: 目录结构不明确
```

---

## 附录：v3.0.0 规则文件索引

| 文件 | 语义规则数 | 主要内容 |
|------|-----------|----------|
| `Base-All-Data.yaml` | ~6 条 | ILF/EIF 复杂度、DET/RET 计数、命名规范 |
| `Base-All-Transaction.yaml` | ~41 条 | 基本过程、EI/EO/EQ 分类、独特性判定 |
| `Orgs-ORG_B-Data.yaml` | ~7 条 | ILF/EIF 描述完整性、逻辑文件差异性 |
| `Orgs-ORG_B-Transaction.yaml` | ~11 条 | 重用程度判定、功能项描述完整性 |
| `Orgs-ORG_B-Format.yaml` | ~8 条 | 功能项名称/描述合规性、重用程度检查 |
| `Orgs-ORG_B-Cross.yaml` | ~5 条 | 层级对应、跨文档一致性 |
| `Orgs-ORG_A-Data.yaml` | ~14 条 | DET/FTR 识别规则、字段标准检查 |
| `Orgs-ORG_A-Transaction.yaml` | ~1 条 | EI 至少包含一个 FTR |
| `Orgs-ORG_A-Format.yaml` | ~8 条 | 功能项名称/描述合规性、截图完整性 |
| `Orgs-ORG_A-Cross.yaml` | ~5 条 | 层级对应、跨文档一致性 |

---

*本文件由 NESMA Check Skill 维护*