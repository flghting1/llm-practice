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

先在 PowerShell 进入本目录并执行：

```powershell
.\install_to_nanobot_workspace.ps1
```

该脚本将工作流复制到 `~/.nanobot/workspace/ecommerce_multi_agent/`，并将 Skill 复制到 `~/.nanobot/workspace/skills/ecommerce-operations/`。这样 WebUI 的默认工作区权限可以直接读取运行所需的规则和模拟数据。

随后：

1. 启动 Nanobot WebUI，保持默认权限。
2. 输入 `使用 $ecommerce-operations，请输出库存预警和补货建议`。
3. Skill 在工作区内执行 `python -m ecommerce_multi_agent.run_demo --scenario <场景>`，并返回含证据与边界的审核结果。

## 给其他人的安装步骤

1. 安装并配置 Nanobot 与一个可用的模型服务；密钥仅保存在对方自己的本机配置中。
2. 克隆本仓库，进入 `nanobot_agent_demo` 目录。
3. 使用 PowerShell 执行 `.\install_to_nanobot_workspace.ps1`。
4. 启动 Nanobot WebUI，打开 `http://127.0.0.1:8765`，使用 `$ecommerce-operations` 发起四类支持请求。

该项目不提供公网共享 WebUI，也不要求或收集使用者的 API Key。每位使用者都在自己的电脑和自己的工作区内运行。

## 事实边界

- Multi-Agent 是本目录中可运行的本地 Python 角色编排原型；路由、检索、只读数据查询和审核均为可测试的确定性环节，Nanobot 负责本地 Agent 工作台和 Skill 加载。
- 规则与数据均为示例，不声称已接入 Shopify、广告平台、MCP、Dify、n8n 或生产环境。
- 不能将模拟数据中的成交额、库存和客服规则写成真实业务结果。
- API Key 仅保存在本机配置中，不提交到仓库。
