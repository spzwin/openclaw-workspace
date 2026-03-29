# GET https://sg-cwork-api.mediportal.com.cn/im/skill/nologin/list

## 作用

获取平台上已发布的 Skill 列表，并从响应中拿到每个 Skill 的 `downloadUrl`。

> **无需鉴权**：这是 `nologin` 接口，不需要 `access-token`、`appKey` 或登录态。

## Headers

| Header | 必填 | 说明 |
|---|---|---|
| `Content-Type` | 否 | `application/json` |

## 参数表

无参数。

## 响应重点字段

```json
{
  "resultCode": 1,
  "data": [
    {
      "id": "2037739875444424706",
      "code": "cms-auth-skills",
      "name": "cms-auth-skills",
      "description": "cms基础 Skill — 登录授权、appKey 获取、access-token 获取",
      "version": 1.0,
      "downloadUrl": "https://filegpt-hn.file.mediportal.com.cn/cwork_skill/cms-auth-skills_1.0.zip",
      "isInternal": true,
      "createTime": "2026-03-28T03:53:40.000+00:00"
    }
  ]
}
```

## 使用约定

- 浏览列表：直接调用接口并展示结果
- 搜索 Skill：在返回列表里按 `name` / `code` / `description` 过滤
- 查看详情：从返回列表里挑出单个 Skill 展示
- 安装到本地：读取对应 Skill 的 `downloadUrl`，下载 ZIP 后解压

## 脚本映射

- 浏览 / 搜索 / 详情：`../../scripts/skill_registry/get_skills.py`
- 安装：`../../scripts/skill_registry/install_skill.py`
