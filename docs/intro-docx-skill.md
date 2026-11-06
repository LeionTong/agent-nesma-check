# DOCX 技能介绍

本文档介绍如何在 Claude Code 中使用 DOCX 技能来处理 Word 文档。

## 快速概览

| 任务 | 方法 |
|------|------|
| 读取/分析内容 | `pandoc` 或解包查看 XML |
| 创建新文档 | 使用 docx-js |
| 编辑现有文档 | 解包 → 编辑 XML → 重新打包 |

## 前置依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| pandoc | 提取 .docx 文本内容 | `pip install pandoc` |
| docx (npm) | 通过 docx-js 创建文档 | `npm install -g docx` |
| Node.js | 运行 docx-js 脚本 | [官网下载](https://nodejs.org/) |
| Python | 运行 unpack/pack/validate 等脚本 | 通常已预装 |
| LibreOffice | .doc 转 .docx、接受 tracked changes、转 PDF | [官网下载](https://www.libreoffice.org/) |
| Poppler | PDF 转图片（`pdftoppm`） | [poppler for Windows](https://github.com/oschwartz10612/poppler-windows) |

## 常用命令

Converting .doc to .docx

Legacy .doc files must be converted before editing:

```python
python scripts/office/soffice.py --headless --convert-to docx document.doc
```

### 读取文档

```bash
# 提取文本（保留 tracked changes）
pandoc --track-changes=all document.docx -o output.md

# 解包查看原始 XML
python scripts/office/unpack.py document.docx unpacked/
```

### 创建文档

```bash
# 使用 docx-js 生成 .docx 文件
node create_doc.js

# 验证生成的文档
python scripts/office/validate.py doc.docx
```

### 编辑文档

```bash
# Step 1: 解包
python scripts/office/unpack.py document.docx unpacked/

# Step 2: 编辑 unpacked/word/ 下的 XML 文件

# Step 3: 重新打包
python scripts/office/pack.py unpacked/ output.docx --original document.docx
```

### 格式转换

```bash
# .doc 转 .docx
python scripts/office/soffice.py --headless --convert-to docx document.doc

# 转为 PDF
python scripts/office/soffice.py --headless --convert-to pdf document.docx

# PDF 转图片
pdftoppm -jpeg -r 150 document.pdf page

# 接受所有 tracked changes
python scripts/accept_changes.py input.docx output.docx
```

## 关键规则

- **永远使用 `WidthType.DXA`** — 不要用 `WidthType.PERCENTAGE`
- **表格需要双重宽度设置** — 同时设置 `columnWidths` 和单元格 `width`
- **PageBreak 必须放在 Paragraph 内**
- **不要用 `\n`** — 使用独立的 Paragraph 元素
- **不要用 unicode bullets** — 使用 `LevelFormat.BULLET` 编号配置
- **docx-js 默认 A4 纸张** — 有需要时显式设置页面尺寸
- **使用 `ShadingType.CLEAR`** — 不要用 SOLID