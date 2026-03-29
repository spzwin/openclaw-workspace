---
name: cms-find-skills
description: CMS Skill 发现工具，调用 get-skills 接口浏览和搜索 Skill，并按 downloadUrl 下载 ZIP 安装到本地
skillCode: cms-find-skills
---

# cms-find-skills

只做两件事：

1. 调用 `get-skills` 接口查看平台上的 Skill
2. 根据 `downloadUrl` 下载 ZIP 并解压到本地

不要登录，不要授权，不要扩展上传、发布、更新、下架能力。

## 当前目录

- `SKILL.md`
- `openapi/skill-registry/get-skills.md`
- `scripts/skill_registry/get_skills.py`
- `scripts/skill_registry/install_skill.py`

目录内实际只有这 4 个文件。

## 路由

- 查看列表：`python3 cms-find-skills/scripts/skill_registry/get_skills.py`
- 搜索：`python3 cms-find-skills/scripts/skill_registry/get_skills.py --search "关键词"`
- 查看详情：`python3 cms-find-skills/scripts/skill_registry/get_skills.py --detail "code 或 name"`
- 取下载地址：`python3 cms-find-skills/scripts/skill_registry/get_skills.py --url "code 或 name"`
- 安装到本地：`python3 cms-find-skills/scripts/skill_registry/install_skill.py --code "code"`
- 已知下载地址时安装：`python3 cms-find-skills/scripts/skill_registry/install_skill.py --url "https://..."`

## 规则

1. 统一以 `get-skills` 返回的数据为准
2. 安装方式固定为：下载 ZIP -> 解压到目标目录
3. 默认安装到脚本所在 workspace 的 `skills/` 目录（从 `__file__` 向上动态查找，不写死路径），可用 `--target` 覆盖
4. 本地已存在同名 Skill 时默认跳过，加 `--force` 可删除旧目录并重新安装
