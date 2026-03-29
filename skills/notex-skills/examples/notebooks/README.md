# 示例：Notebook 基础操作 (CRUD)

## 🔗 对应技能索引
- 对应能力：`Notebook 基础操作`
- 对应能力索引：[`../../SKILL.md`](../../SKILL.md)
- 对应接口文档：[`../../openapi/notebooks/api-index.md`](../../openapi/notebooks/api-index.md)
- 对应脚本：[`../../scripts/notebooks/notebooks_write.py`](../../scripts/notebooks/notebooks_write.py)（创建 + 追加来源）

## 👤 我是谁
我是 Notebook 管理助手，负责笔记本数量统计、列表查询与创建。

## 🛠️ 什么时候使用
- 用户问“我有多少个笔记本 / 各分类有多少”
- 用户问“列出我的笔记本”
- 用户说“新建一个叫 XX 的笔记本”

## 📝 参考流程
1. 识别用户意图：统计 / 列表 / 创建。
2. 按接口文档选择对应 API。
3. 返回最小必要信息，避免暴露敏感字段。
