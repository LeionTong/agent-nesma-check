# assets

存放交付物模板。仓库里不带模板原件（原件含客户名称与项目编号），按自己的交付规范放进来即可。

目录约定：

- `templates-orga/`：组织 A 分支的模板（需求规格说明书、验收测试报告）
- `templates-orgb/`：组织 B 分支的模板（需求规格说明书、验收测试报告）

模板只需保证固定标签与 `skills/nesma-check/references/main-workflow.md` 描述的一致：功能编号、ILF/EIF/EI/EO/EQ 描述、DET/RET 计数、重用程度、修改类型。检查器靠这些标签定位段落，标签缺失时该文档的对应检查项会判为不通过。

引擎不读取这个目录，`--org` 只负责挑选 `checklist/` 下的规则集。模板的作用是给人照着准备交付物：检查器靠 `references/main-workflow.md` 描述的固定标签定位内容，标签是功能编号、ILF/EIF/EI/EO/EQ 描述、DET/RET 计数、重用程度、修改类型。交付物里缺这些标签，对应的检查项会直接判不通过，因此模板与检查规则必须同步维护。
