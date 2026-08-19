\# 简历与 JD 匹配助手



一个面向求职场景的简历与岗位 JD 匹配工具。输入简历文本和一个或多个岗位 JD，系统输出结构化匹配报告，帮助求职者识别技能缺口、选择优先投递岗位并准备面试。



\## 项目功能



\- 简历与单个 JD 匹配

\- 多个 JD 横向对比

\- 输出已掌握技能和缺少技能

\- 生成项目补强建议

\- 输出匹配分数和风险等级

\- 生成面试风险点

\- FastAPI `/match` 接口

\- FastAPI `/compare` 接口

\- Streamlit 网页前端

\- Pydantic 结构化输出

\- JSON 合法率、字段完整率、稳定性和建议可执行度评测

\- Docker 部署与健康检查



\## 系统架构



```text

简历文本 + JD 文本

&#x20;         |

&#x20;         v

&#x20;     Streamlit

&#x20;         |

&#x20;         v

&#x20;      FastAPI

&#x20;         |

&#x20;         v

&#x20;     匹配引擎

&#x20;         |

&#x20;         +-- 技能识别

&#x20;         +-- 匹配分数

&#x20;         +-- 缺口识别

&#x20;         +-- 项目建议

&#x20;         +-- 面试风险

&#x20;         |

&#x20;         v

&#x20;   MatchReport JSON

```



\## 技术栈



\- Python 3.12

\- Pydantic

\- FastAPI

\- Streamlit

\- Pandas

\- Docker



\## 输出结构



系统输出 `MatchReport`：



\- `matched\_skills`：已掌握技能

\- `missing\_skills`：缺少技能

\- `projects\_to\_build`：建议补充的项目

\- `risk\_level`：`low`、`medium` 或 `high`

\- `match\_score`：0～100 的匹配分数

\- `explanation`：匹配解释

\- `interview\_risks`：面试风险点



多 JD 对比额外输出：



\- `comparisons`：各岗位完整报告

\- `best\_match`：匹配分数最高岗位

\- `common\_missing\_skills`：多份 JD 重复出现的技能缺口

\- `recommendation`：投递优先级和补强建议



\## 匹配规则



当前版本使用可解释的技能关键词规则：



\- Python

\- Git

\- FastAPI

\- RAG

\- Embedding

\- Docker

\- SQL

\- Streamlit

\- REST API

\- Prompt

\- Pydantic

\- 测试



匹配分数计算方式：



```text

匹配分数 = 已匹配技能数量 / JD 识别出的技能数量 × 100

```



风险等级：



\- 75 分及以上：`low`

\- 50～74 分：`medium`

\- 50 分以下：`high`



\## 本地运行



进入目录：



```text

cd C:\\Users\\flghting\\Documents\\ChatGPT\\AI职业\\llm\_practice\\resume\_matcher\_practice

```



安装依赖：



```text

.venv\\Scripts\\python.exe -m pip install -r requirements.txt

```



启动 API：



```text

.venv\\Scripts\\python.exe -m uvicorn resume\_api:app --host 127.0.0.1 --port 8005

```



启动网页：



```text

.venv\\Scripts\\python.exe -m streamlit run streamlit\_app.py --server.port 8503

```



访问：



\- 网页：`http://localhost:8503`

\- API 文档：`http://127.0.0.1:8005/docs`

\- 健康检查：`http://127.0.0.1:8005/health`



\## 测试和评测



```text

.venv\\Scripts\\python.exe matcher.py

.venv\\Scripts\\python.exe evaluate\_matcher.py

.venv\\Scripts\\python.exe evaluate\_output\_quality.py

.venv\\Scripts\\python.exe test\_resume\_api.py

.venv\\Scripts\\python.exe test\_multi\_jd.py

.venv\\Scripts\\python.exe test\_resume\_api\_compare.py

```



当前评测结果：



| 指标 | 结果 |

| --- | ---: |

| JD 缺口识别准确率 | 100% |

| JSON 合法率 | 100% |

| 字段完整率 | 100% |

| 同一 JD 输出稳定率 | 100% |

| 建议可执行率 | 100% |



\## Docker 部署



构建镜像：



```text

docker build -t resume-matcher-api .

```



启动容器：



```text

docker run --rm -d --name resume-matcher-api -p 8006:8005 resume-matcher-api

```



健康检查：



```text

Invoke-RestMethod http://127.0.0.1:8006/health

```



停止容器：



```text

docker stop resume-matcher-api

```



\## 当前限制



\- 当前使用关键词规则，尚未接入真实大模型

\- 技能词表仍需继续扩充

\- 简历输入以文本为主，尚未直接解析 PDF 或 Word

\- 匹配分数是规则指标，不等于实际录用概率

\- 未加入用户账号和私有数据存储



\## 隐私说明



不要把包含手机号、邮箱、身份证号或真实住址的简历上传到公开 Git 仓库。



项目只提交示例文本、代码和评测数据；真实简历应保存在本地私有目录。



\## 后续优化



\- 接入大模型进行语义匹配

\- 增加 PDF、Word 简历解析

\- 对技能进行同义词和层级归一化

\- 增加经历与 JD 职责的逐条匹配

\- 增加 ATS 关键词覆盖率

\- 生成针对岗位的简历改写建议

