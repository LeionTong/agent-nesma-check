# XLSX 技能介绍

本文档介绍如何在 Claude Code 中使用 XLSX 技能来处理 Excel 文件。

## 快速概览

| 任务 | 方法 |
|------|------|
| 读取/分析数据 | pandas |
| 创建/编辑含公式文件 | openpyxl |
| 重新计算公式 | `scripts/recalc.py`（依赖 LibreOffice） |

## 前置依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| Python | 运行脚本 | 通常已预装 |
| openpyxl | 创建/编辑 Excel（公式、格式） | `pip install openpyxl` |
| pandas | 数据分析、批量操作 | `pip install pandas` |
| LibreOffice | 公式重新计算 | [官网下载](https://www.libreoffice.org/download/download/) |

## 常用命令

### 读取/分析数据

```python
import pandas as pd

# 读取单个 Sheet
df = pd.read_excel('file.xlsx')
df.head()      # 预览数据
df.info()      # 列信息
df.describe()  # 统计摘要

# 读取所有 Sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)

# 导出
df.to_excel('output.xlsx', index=False)
```

### 创建含公式的 Excel

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

sheet['A1'] = 'Hello'
sheet['B2'] = '=SUM(A1:A10)'  # 使用公式而非硬编码值

# 格式化
sheet['A1'].font = Font(bold=True)
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')

wb.save('output.xlsx')
```

### 编辑现有文件

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
sheet = wb.active  # 或 wb['SheetName']

sheet['A1'] = 'New Value'
sheet.insert_rows(2)    # 插入行
sheet.delete_cols(3)    # 删除列

wb.save('modified.xlsx')
```

### 重新计算公式

```bash
python scripts/recalc.py output.xlsx
```

> **注意**：openpyxl 只能写入公式字符串，不会计算结果。必须运行 `recalc.py` 才能刷新公式值并检查 `#REF!`、`#DIV/0!` 等错误。

## 关键规则

- **始终使用公式而非硬编码值** — 让 Excel 动态计算，保持表格可更新
- **LibreOffice 必需** — 公式重新计算依赖 LibreOffice
- **`data_only=True` 慎用** — 用该参数打开文件后保存会导致公式永久丢失
- **大文件优化** — 读取用 `read_only=True`，写入用 `write_only=True`

## 配色规范（金融模型）

| 颜色 | 含义 |
|------|------|
| 蓝色文字 (RGB: 0,0,255) | 硬编码输入值 |
| 黑色文字 (RGB: 0,0,0) | 公式和计算 |
| 绿色文字 (RGB: 0,128,0) | 同一工作簿内跨表引用 |
| 红色文字 (RGB: 255,0,0) | 外部文件链接 |
| 黄色背景 (RGB: 255,255,0) | 需关注的重点假设 |

## 常见错误修复

| 错误 | 原因 | 修复方法 |
|------|------|----------|
| `#REF!` | 无效的单元格引用 | 检查公式中的引用是否正确 |
| `#DIV/0!` | 除以零 | 确保分母不为零 |
| `#VALUE!` | 数据类型错误 | 检查公式参数类型 |
| `#NAME?` | 未识别的公式名 | 检查拼写和函数名 |
| `#N/A` | 查找值不存在 | 检查查找范围 |