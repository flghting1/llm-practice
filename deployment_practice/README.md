\# AI 项目统一部署链路



一个用于统一检查、构建、启动和验收三个 AI 求职项目的本地 Docker 部署工具。



\## 纳入部署的项目



| 项目 | 容器 | 主机端口 |

| --- | --- | ---: |

| RAG 求职知识库助手 | `rag-practice-api` | 8001 |

| SQL 数据分析 Agent | `sql-agent-api` | 8004 |

| 简历与 JD 匹配助手 | `resume-matcher-api` | 8006 |



\## 部署流程



```text

检查项目文件

&#x20;     |

&#x20;     v

构建三个 Docker 镜像

&#x20;     |

&#x20;     v

清理旧容器并启动新容器

&#x20;     |

&#x20;     v

轮询三个健康检查接口

&#x20;     |

&#x20;     v

验证三个核心业务接口

&#x20;     |

&#x20;     v

记录 JSONL 验收结果

```



\## 文件说明



\- `deployment\_plan.md`：部署目标和验收标准

\- `deploy\_check.py`：部署前关键文件检查

\- `deploy\_all.ps1`：统一构建并启动三个容器

\- `verify\_deployment.py`：验证健康检查和核心接口

\- `stop\_all.ps1`：统一停止并删除项目容器



\## 环境要求



\- Windows 10 或 Windows 11

\- PowerShell

\- Python 3.12

\- Docker Desktop

\- 已缓存 RAG Embedding 模型：

&#x20; `BAAI/bge-small-zh-v1.5`



模型缓存默认位于：



```text

C:\\Users\\当前用户名\\.cache\\huggingface

```



部署脚本会把缓存以只读方式挂载到 RAG 容器，并设置：



```text

HF\_HUB\_OFFLINE=1

TRANSFORMERS\_OFFLINE=1

```



这样可以避免容器启动时访问 Hugging Face。



\## 使用方法



进入目录：



```text

cd C:\\Users\\flghting\\Documents\\ChatGPT\\AI职业\\llm\_practice\\deployment\_practice

```



部署前检查：



```text

py -3.12 deploy\_check.py

```



统一构建并启动：



```text

powershell -ExecutionPolicy Bypass -File .\\deploy\_all.ps1

```



统一验收：



```text

py -3.12 verify\_deployment.py

```



查看容器：



```text

docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"

```



停止所有项目容器：



```text

powershell -ExecutionPolicy Bypass -File .\\stop\_all.ps1

```



\## 验收内容



\### RAG API



\- `GET http://127.0.0.1:8001/health`

\- `POST http://127.0.0.1:8001/ask`

\- 检查回答和来源字段



\### SQL Agent API



\- `GET http://127.0.0.1:8004/health`

\- `POST http://127.0.0.1:8004/ask`

\- 检查 SQL、查询解释和结果字段



\### 简历匹配 API



\- `GET http://127.0.0.1:8006/health`

\- `POST http://127.0.0.1:8006/compare`

\- 检查岗位对比、最佳岗位和建议字段



\## 当前验收结果



\- 部署服务数量：3

\- 健康检查通过率：100%

\- 核心接口通过率：100%

\- 三个容器均支持 Docker 健康检查

\- RAG 支持挂载本地模型缓存离线启动



\## 日志和隐私



`deployment\_verification\_results.jsonl` 是运行日志，不提交 Git。



部署过程不会上传真实简历、手机号、邮箱或其他个人隐私数据。



\## 当前限制



\- 当前是 Windows 本地 Docker 部署链路

\- RAG 容器依赖主机已有模型缓存

\- 尚未部署到公网云服务器

\- 尚未配置 HTTPS、域名和用户认证

\- 尚未接入 GitHub Actions 自动部署

