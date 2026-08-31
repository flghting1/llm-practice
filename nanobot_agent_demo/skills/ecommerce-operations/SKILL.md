# 电商运营 Multi-Agent 工作流

当用户要处理商品文案、售后客服、销售日报或库存预警时，使用本项目的可验证工作流，而不是直接编造结论。

## 使用方式

1. 先识别请求属于 `listing`、`customer_service`、`sales_report` 或 `inventory_alert`。
2. 在项目根目录执行：

   `python -m ecommerce_multi_agent.run_demo --scenario sales_report`

3. 根据实际场景替换 `sales_report`，可选值为 `listing`、`customer_service`、`sales_report`、`inventory_alert`。
4. 向用户返回经审核的 `final_answer`，不要省略“本地模拟数据”的边界。

## 约束

- 数据库只包含本地演示数据，不能描述为真实店铺、广告或客户数据。
- 不声称接入 Shopify、广告平台、MCP、Dify、n8n 或生产环境。
- 不能绕过 Review Agent；若审核失败，应说明缺少的事实或不支持的请求。
