\# SQL 数据分析 Agent 演示脚本



\## 演示目标



在 3～5 分钟内展示自然语言查询、SQL 生成、安全控制、评测和 Docker 部署能力。



\## 一、项目介绍



这是一个 SQL 数据分析 Agent。用户输入业务问题后，系统生成只读 SQL，查询 SQLite 数据库，并返回查询解释、表格和图表。



当前版本使用规则实现自然语言到 SQL 的转换，重点验证完整工程链路和 SQL 安全设计。



\## 二、系统架构



调用链路：



用户问题 → Streamlit → FastAPI → SQL Agent → SQL 安全执行层 → SQLite



核心文件：



\- `sql\_agent.py`：问题解析、SQL 生成和单次修复

\- `sql\_tool.py`：SQL 校验、权限白名单和数据库查询

\- `sql\_api.py`：FastAPI 接口

\- `streamlit\_app.py`：表格与图表前端

\- `evaluate\_sql\_agent\_metrics.py`：综合指标评测



\## 三、正常查询演示



打开：



`http://localhost:8502`



输入：



`各商品的销售额是多少？`



展示：



\- 查询解释

\- 生成的 SQL

\- SQL 执行次数

\- 商品销售额表格

\- 柱状图



切换测试：



\- 每个城市有多少客户？

\- 不同状态的订单数量是多少？

\- 谁的消费最高？



\## 四、异常输入演示



输入：



`明天天气怎么样？`



预期结果：



系统明确拒绝，提示暂时无法把问题转换为 SQL，不会生成无关查询。



\## 五、安全能力演示



运行：



`.venv\\Scripts\\python.exe test\_sql\_agent\_safety.py`



展示：



\- 空问题被拒绝

\- 未知问题被拒绝

\- DELETE 被拦截

\- DROP 被拦截



运行：



`.venv\\Scripts\\python.exe test\_sql\_permissions.py`



展示：



\- 正常业务字段可查询

\- SQLite 系统表被拦截

\- 未授权字段被拦截



\## 六、SQL 修复演示



运行：



`.venv\\Scripts\\python.exe test\_sql\_repair.py`



展示：



\- 常见错误字段被修复

\- 最多执行两次

\- 修复一次后仍失败则停止

\- 不会无限重试



\## 七、评测结果



运行：



`.venv\\Scripts\\python.exe evaluate\_sql\_agent\_metrics.py`



当前结果：



\- SQL 执行成功率：100%

\- 危险 SQL 拦截率：100%

\- 结果解释可用率：100%

\- 无效问题拒绝率：100%

\- 本地平均响应时间：约 1 ms



\## 八、Docker 部署



运行：



`docker ps --filter "name=sql-agent-api"`



展示容器状态为 `healthy`。



访问：



`http://127.0.0.1:8004/health`



说明 Docker 镜像会在构建阶段初始化示例数据库，并通过健康检查验证 API 状态。



\## 九、项目限制



当前自然语言转 SQL 使用规则实现，并非真实大模型。下一阶段可以接入大模型、数据库 Schema Prompt 和更完整的 SQL 验证器。

