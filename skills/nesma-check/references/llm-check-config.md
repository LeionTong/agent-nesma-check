# LLM 语义检查配置

**版本**: 3.0.0
**日期**: 2026-06-23

## 启用方式

LLM 语义检查默认启用。配置位于 `SKILL.md`:

```yaml
llm-check-enabled: true
```

如需禁用，将 `llm-check-enabled` 设为 `false` 或删除该行。

## 置信度机制

### 评分标准

LLM 返回的结构化结果必须包含 `confidence` 字段，范围 0.0-1.0。

| 等级 | 范围 | 含义 |
|------|------|------|
| 高 | 0.85 - 1.0 | 非常有把握，证据充分且明确 |
| 中 | 0.60 - 0.85 | 比较有把握，证据基本充分 |
| 低 | 0.00 - 0.60 | 把握不足，需要人工复核 |

### 判决规则

```
confidence >= 0.6 → verdict 直接采用
confidence < 0.6 → verdict + "待复核"
```

### 冲突解决策略

当程序化检查和语义检查结果冲突时：

1. **语义层结果优先**（因为语义层可以理解上下文）
2. **记录冲突到报告**（供人工审核）
3. **冲突时置信度降低**（标记为"待确认"）

## LLM 调用约束

1. **不调用额外 API**: 复用当前 agent 会话的 LLM
2. **每次只处理一个项目**: 不批量处理
3. **分批处理**: 单批不超过 10 个检查项，避免 token 消耗过大
4. **使用中文 LLM**: MiniMax-M2.7 / GLM-5.1 等中文模型

## 检查项分层（v3.0.0）

### Layer 1: 程序化检查 (~80 项)

这些检查项不需要 LLM，直接检查文档内容：

| 类别 | 规则数量 | 检查内容 |
|------|----------|----------|
| Base-All-Data | ~5 项 | DET 定义、RET 计数、命名规范、唯一性 |
| Base-All-Transaction | ~10 项 | DET 定义、FTR 计数、基本过程完整性 |
| Orgs-{org}-Format | ~45 项 | 位置格式、列数、编号连续性、命名规范、提交完备性 |
| Orgs-{org}-Cross | ~10 项 | 层级对应检查、跨文档对齐 |

规则文件：`checklist/` 中 `layer: programmatic` 的 YAML 文件。

### Layer 2: LLM 语义检查 (~73 项)

这些检查项需要 LLM 语义理解，详见 `llm-prompts.md`：

| 类别 | 规则数量 | 检查内容 |
|------|----------|----------|
| Base-All-Data | ~6 项 | 复杂度矩阵、ILF/EIF 区分、ILF-EI 关联 |
| Base-All-Transaction | ~41 项 | 基本过程识别、EI/EO/EQ 分类、独特性判定 |
| Orgs-{org}-Data | ~10 项 | DET 计数规则、FTR 识别规则 |
| Orgs-{org}-Format | ~6 项 | 功能项描述合规性、重用程度判定 |
| Orgs-{org}-Cross | ~5 项 | 跨文档一致性、架构图对比 |

规则文件：`checklist/` 中 `layer: semantic` 的 YAML 文件。

## LLM 结果格式

```json
{
  "verdict": "pass|fail|uncertain",
  "confidence": 0.0-1.0,
  "reason": "判断理由",
  "location": "位置信息",
  "evidence": "原始内容片段"
}
```

## 规则 ID 映射（v2 → v3）

| v2 旧 ID | v3 新 ID | 说明 |
|----------|---------|------|
| DF-004, DF-012 | Base-All-Data-003, Base-All-Data-011 | ILF/EIF 复杂度矩阵 |
| TF-004, TF-011, TF-018 | Base-All-Transaction-023, Base-All-Transaction-035, Base-All-Transaction-051 | EI/EO/EQ 复杂度矩阵 |
| CV-001, CV-002 | Base-All-Transaction-013, Base-All-Transaction-034 | 基本过程/跨文档关联 |
| FM-001 ~ FM-012 | Orgs-ORG_B-Format-063 ~ Orgs-ORG_B-Format-097 | ORG_B 格式规则 |
| — | Orgs-ORG_A-Format-112 ~ Orgs-ORG_A-Format-133 | ORG_A 格式规则（新增） |