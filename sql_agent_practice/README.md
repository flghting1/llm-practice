\# SQL 数据分析 Agent



一个面向业务数据查询场景的 SQL Agent 项目。用户输入自然语言问题，系统生成只读 SQL，查询 SQLite 数据库，并返回 SQL、结果解释、表格和可视化图表。



\## 项目功能



\- 自然语言问题转换为 SQL

\- SQLite 只读查询

\- FastAPI 查询接口

\- Streamlit 可视化页面

\- 自动展示 SQL、表格和柱状图

\- 危险 SQL 拦截

\- 数据表与字段权限白名单

\- SQL 执行失败后最多修复一次

\- 综合指标评测和 JSONL 日志

\- Docker 容器化部署与健康检查



\## 系统架构



```text

用户问题

&#x20;  |

&#x20;  v

Streamlit 前端

&#x20;  |

&#x20;  v

FastAPI /ask

&#x20;  |

&#x20;  v

SQL Agent

&#x20;  |

&#x20;  +-- 问题解析与 SQL 生成

&#x20;  +-- SQL 单次修复

&#x20;  |

&#x20;  v

SQL 安全执行层

&#x20;  |

&#x20;  +-- 只允许 SELECT

&#x20;  +-- 单条 SQL 限制

&#x20;  +-- 危险关键字拦截

&#x20;  +-- 表和字段白名单

&#x20;  |

&#x20;  v

SQLite 数据库

```



\## 技术栈



\- Python 3.12

\- FastAPI

\- Streamlit

\- SQLite

\- Pandas

\- Requests

\- Docker



\## 数据库



项目包含两张示例业务表：



\### customers



\- `id`

\- `name`

\- `city`

\- `registered\_at`



\### orders



\- `id`

\- `customer\_id`

\- `product`

\- `amount`

\- `status`

\- `ordered\_at`



数据库由 `create\_database.py` 初始化，不提交生成的 `sales.db`。



\## 当前支持的问题



\- 各商品的销售额是多少？

\- 每个城市有多少客户？

\- 不同状态的订单数量是多少？

\- 谁的消费最高？



当前版本使用可解释的规则实现自然语言到 SQL 的转换，重点验证 SQL Agent 的完整工程链路、安全控制、评测和部署能力。



\## SQL 安全设计



\### 只读限制



仅允许执行以 `SELECT` 开头的单条 SQL。



\### 危险关键字拦截



拦截以下操作：



\- INSERT

\- UPDATE

\- DELETE

\- DROP

\- ALTER

\- CREATE

\- REPLACE

\- TRUNCATE

\- ATTACH

\- DETACH

\- PRAGMA



\### 权限白名单



当前允许访问：



\- `customers`：`id`、`name`、`city`

\- `orders`：`id`、`customer\_id`、`product`、`amount`、`status`



系统表和未授权字段会被 SQLite Authorizer 拦截。



\### 单次修复



当 SQL 因常见字段名错误执行失败时，系统最多修复一次。修复后仍然失败则立即停止，避免无限重试。



\## 评测结果



综合评测包含：



\- 4 个正常业务问题

\- 4 条危险 SQL

\- 空问题和未知问题

\- SQL 执行失败识别



当前结果：



| 指标 | 结果 |

| --- | ---: |

| SQL 执行成功率 | 100% |

| 危险 SQL 拦截率 | 100% |

| 结果解释可用率 | 100% |

| 无效问题拒绝率 | 100% |

| 本地平均响应时间 | 约 1 ms |



该响应时间基于本地小型 SQLite 示例数据库，仅用于当前项目基准，不代表生产环境性能。



\## 本地运行



进入项目目录：



```text

cd C:\\Users\\flghting\\Documents\\ChatGPT\\AI职业\\llm\_practice\\sql\_agent\_practice

```



安装依赖：



```text

.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



初始化数据库：



```text

.venv\\Scripts\\python.exe create\_database.py

```



启动 API：



```text

.venv\\Scripts\\python.exe -m uvicorn sql\_api:app --host 127.0.0.1 --port 8003

```



启动 Streamlit：



```text

.venv\\Scripts\\python.exe -m streamlit run streamlit\_app.py --server.port 8502

```



访问：



\- Streamlit：`http://localhost:8502`

\- API 文档：`http://127.0.0.1:8003/docs`

\- 健康检查：`http://127.0.0.1:8003/health`



\## 运行测试



```text

.venv\\Scripts\\python.exe test\_sql\_tool.py

.venv\\Scripts\\python.exe test\_sql\_agent\_safety.py

.venv\\Scripts\\python.exe test\_sql\_permissions.py

.venv\\Scripts\\python.exe test\_sql\_repair.py

.venv\\Scripts\\python.exe evaluate\_sql\_agent\_metrics.py

```



\## Docker 部署



构建镜像：



```text

docker build -t sql-agent-api .

```



启动容器：



```text

docker run --rm -d --name sql-agent-api -p 8004:8003 sql-agent-api

```



健康检查：



```text

Invoke-RestMethod http://127.0.0.1:8004/health

```



停止容器：



```text

docker stop sql-agent-api

```



\## 项目文件



```text

sql\_agent\_practice/

├── create\_database.py

├── sql\_tool.py

├── sql\_agent.py

├── sql\_api.py

├── streamlit\_app.py

├── evaluate\_sql\_agent.py

├── evaluate\_sql\_agent\_metrics.py

├── test\_sql\_tool.py

├── test\_sql\_agent\_safety.py

├── test\_sql\_permissions.py

├── test\_sql\_repair.py

├── requirements.txt

├── Dockerfile

├── .dockerignore

└── README.md

```



\## 当前限制



\- 自然语言转 SQL 当前采用规则实现，尚未接入真实大模型

\- 当前只支持预设的四类业务问题

\- 使用本地示例数据库，数据规模较小

\- 尚未加入用户身份认证和多租户权限

\- SQL 修复仅覆盖预设的常见字段名错误



\## 后续优化



\- 接入大模型生成 SQL

\- 加入数据库 Schema Prompt

\- 增加更多聚合、时间趋势和多表查询

\- 使用更大规模的业务数据集评测

\- 增加用户级数据权限

\- 增加查询历史和结果导出

