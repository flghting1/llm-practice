# Nanobot 电商运营 Multi-Agent 原型

基于 Nanobot 的本地 Agent 工作台扩展。项目将电商运营中的商品文案、客服话术、销售日报和库存预警，拆成可运行、可追溯、可审核的五角色工作流。

> 重要边界：本项目使用本地 SQLite 模拟商品、库存和订单数据，以及示例运营规则。它不是 Shopify、广告平台或真实店铺的生产接入。

## 已完成内容

- 配置并验证 OpenAI-compatible API 的真实模型调用，Nanobot v0.3.0 在本机 WebUI 可用。
- 编写并启用 4 个自定义 Skill，新增 `ecommerce-operations`。
- 实现可单独运行的 Multi-Agent 工作流和自动化测试，无需真实密钥即可复现。
- 数据查询采用 SQLite 只读连接和 Authorizer；审核角色拦截无证据数据、空输出及夸大营销表述。

## Multi-Agent 协作链路

```text
用户请求
  -> Router Agent（识别场景）
  -> Knowledge Agent（检索示例规则）
  -> Data Agent（只读查询模拟数据）
  -> Content Agent（生成文案/日报/话术）
  -> Review Agent（校验证据与夸大承诺）
  -> Finalizer Agent（附来源与边界）
```

当前支持四类请求：`listing`、`customer_service`、`sales_report`、`inventory_alert`。每次运行会保留 `route`、数据结果、规则来源、审核状态和角色轨迹，方便演示与排错。

## 快速运行

在 `nanobot_agent_demo` 目录执行：

```powershell
python -m unittest discover -s tests -v
python -m ecommerce_multi_agent.run_demo --scenario sales_report
python -m ecommerce_multi_agent.run_demo --scenario inventory_alert
```

预期结果：测试覆盖销售日报、库存预警、客服话术和不支持请求的拦截；命令行输出完整共享状态，其中 `final_answer` 为审核通过后的最终结果。

## Skills

| Skill | 用途 |
| --- | --- |
| `ecommerce-operations` | 以可验证工作流处理四类电商运营请求。 |
| `jd-match` | 基于项目事实提取岗位匹配与待补强项。 |
| `boss-reply` | 生成 BOSS 投递、HR 追问和面试开场文本。 |
| `interview-drill` | 围绕 RAG、受控 SQL、FastAPI、Docker 和部署边界生成面试题。 |

## 纳入 Nanobot WebUI

1. 在 Nanobot WebUI 打开本目录，保持 `Default Permission`。
2. 提出商品文案、售后客服、销售日报或库存预警请求，并指定 `$ecommerce-operations`。
3. Skill 会要求执行 `python -m ecommerce_multi_agent.run_demo --scenario <场景>` 并保留输出边界。

## 事实边界

- Multi-Agent 是本目录中可运行的本地 Python 角色编排原型；路由、检索、只读数据查询和审核均为可测试的确定性环节，Nanobot 负责本地 Agent 工作台和 Skill 加载。
- 规则与数据均为示例，不声称已接入 Shopify、广告平台、MCP、Dify、n8n 或生产环境。
- 不能将模拟数据中的成交额、库存和客服规则写成真实业务结果。
- API Key 仅保存在本机配置中，不提交到仓库。
