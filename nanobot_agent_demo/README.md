# 个人 Nanobot Agent

一个本地运行的个人 Agent 工作台，基于 Nanobot 和 OpenAI-compatible API，面向 AI 应用开发求职场景生成可追溯的 JD 匹配、BOSS 回复与面试训练材料。

## 已完成内容

- 配置并验证 OpenAI-compatible API 的真实模型调用。
- 编写并启用 3 个自定义 Skill：`jd-match`、`boss-reply`、`interview-drill`。
- 将 `SmartSteer_Status.md` 作为项目事实来源，约束 Agent 将内容分为已完成、可迁移能力与待补强项。
- 在 Nanobot WebUI 的 `Default Permission` 下完成技能加载和输出测试。

## 三个 Skill

| Skill | 用途 |
| --- | --- |
| `jd-match` | 提取岗位任职要求，基于已验证项目事实给出匹配和补强建议。 |
| `boss-reply` | 生成 BOSS 投递、HR 追问和面试开场文本。 |
| `interview-drill` | 围绕 RAG、受控 SQL、FastAPI、Docker 和部署边界生成面试题。 |

## 使用方式

1. 在 Nanobot WebUI 选择包含 `SmartSteer_Status.md` 的项目目录。
2. 保持 `Default Permission`。
3. 使用 `$jd-match`、`$boss-reply` 或 `$interview-drill` 发起请求。

## 事实边界

- RAG 和受控 SQL 项目的完成状态以 `SmartSteer_Status.md` 为准。
- SQL 项目是规则型受控原型，不表述为大模型驱动的自主 SQL Agent。
- 不把未验证的 Tool Calling、Agent 记忆、多 Agent 协作、MCP、LangGraph 或 Dify 写成已有经历。
- API Key 仅保存在本机配置中，不提交到仓库。

## 运行环境

- Python 3.12.6
- Nanobot v0.3.0
- OpenAI-compatible API（密钥通过本机配置注入）

Nanobot 为开源基础框架；本目录仅记录本项目新增的 Skill 和演示说明。
