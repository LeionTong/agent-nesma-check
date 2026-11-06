# 文档转 Markdown 前置依赖检查提示词

本提示词用于 AI 工作流中，在执行 Office 文档转 Markdown 前，先检查环境是否满足前置依赖。

---

## 检查提示词（粘贴给 AI）

```
请检查以下前置依赖是否已安装。如果缺少依赖，请告知用户如何安装。

## 需要检查的工具

| 工具 | 用途 | 检查命令 |
|------|------|----------|
| pandoc | 将 docx/doc/xls/xlsx 转为 markdown | `pandoc --version` |
| python | 运行脚本 | `python --version` |
| python-docx | 读取 docx 文件 | `python -c "import docx; print('ok')"` |
| openpyxl | 读取 xlsx/xls 文件 | `python -c "import openpyxl; print('ok')"` |
| pandas | 数据分析/表格输出 | `python -c "import pandas; print('ok')"` |
| soffice (LibreOffice) | .doc/.xls 旧格式转换（可选） | `soffice --version` |

## 检查步骤

请逐项运行上方"检查命令"列中的命令：

1. 若命令输出版本号或 `ok`，说明已安装，继续下一步
2. 若命令报 `not found` 或 `No module named`，说明未安装
3. 将所有未安装的工具列出，提供安装命令（pip install / 官网下载链接）

## 已知限制

- `.doc` 和 `.xls` 为旧格式，pandoc 不直接支持，需要先通过 LibreOffice 转换为 `.docx` / `.xlsx`
- 如果用户只有 `.doc`/`.xls` 文件且未安装 LibreOffice，请告知：必须先安装 LibreOffice 才能继续
- `.docx` / `.xlsx` 无需 LibreOffice，pandoc + python-docx/openpyxl 即可直接转换

## 安装命令汇总

### Windows
```powershell
# Python 包（PowerShell 或 CMD）
pip install pandoc python-docx openpyxl pandas

# LibreOffice（仅 .doc/.xls 旧格式需要）
# https://www.libreoffice.org/download/download/
winget install TheDocumentFoundation.LibreOffice
```

### macOS
```bash
brew install pandoc
pip install python-docx openpyxl pandas
# LibreOffice（可选）
brew install --cask libreoffice
```

### Linux
```bash
sudo apt install pandoc
pip install python-docx openpyxl pandas
# LibreOffice（可选）
sudo apt install libreoffice
```

---

转换完成后，若原始文件为 `.doc`/`.xls` 旧格式，请告知用户已通过 LibreOffice 完成中间格式转换。
```

---

## 流程图

```
用户提交文件
      │
      ▼
检查文件扩展名
      │
      ├── .md ──────────────────► 无需转换，提示用户
      │
      ├── .docx / .xlsx ─────────► pandoc + python-docx/openpyxl → md ✅
      │
      └── .doc / .xls ───────────► 检查 LibreOffice
                │
                ├── 已安装 ──────► LibreOffice 转为新格式 → pandoc → md ✅
                │
                └── 未安装 ──────► 提示用户安装 LibreOffice ❌
```

## 各格式转换方式对照

| 源格式 | 推荐工具 | 是否需要 LibreOffice |
|--------|----------|---------------------|
| `.docx` → `.md` | pandoc | ❌ |
| `.doc` → `.md` | LibreOffice → pandoc | ✅ |
| `.xlsx` → `.md` | pandas / openpyxl | ❌ |
| `.xls` → `.md` | LibreOffice → pandas/openpyxl | ✅ |