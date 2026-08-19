# 本地 RAG 知识库练习

这是一个用于学习 RAG、Embedding、来源引用和 FastAPI 的本地知识库问答项目。

当前版本使用本地中文 Embedding 模型完成文档检索，并用检索到的第一条资料模拟回答。项目尚未接入真实大模型 API。

## 已实现功能

- JSON 文档加载
- 关键词检索
- TF-IDF 向量检索
- 中文 Embedding 语义检索
- TopK 相似度排序
- 查询改写
- 低相似度拒答
- Prompt 拼接
- 来源文件与相似度展示
- `GET /health` 健康检查
- `POST /ask` 知识库问答接口
- 空输入与无答案处理
- 固定测试集批量评测

## RAG 流程

```text
用户问题
→ 查询改写
→ 生成问题 Embedding
→ 计算问题与文档的相似度
→ 返回 Top 3 文档
→ 使用 0.60 阈值过滤
→ 拼接 Prompt
→ 生成模拟回答
→ 返回答案和引用来源
```

## Markdown 知识库

知识库文档放在 `knowledge_base/` 目录下，按用途分为：

- `job_descriptions/`：岗位 JD
- `official_docs/`：官方文档
- `interview_notes/`：面试题和回答
- `study_notes/`：学习笔记

程序会递归读取目录中的 Markdown 文件，提取一级标题作为文档标题，并按 300 字符切分，片段之间保留 50 字符重叠。

查看当前知识库统计：

```powershell
.venv\Scripts\python.exe inspect_knowledge_base.py
```

将旧 JSON 资料转换为 Markdown：

```powershell
.venv\Scripts\python.exe migrate_json_to_markdown.py
```

当前知识库包含 18 份 Markdown 文档，切分后得到 35 个片段。

## 环境要求

- Python 3.12
- Windows PowerShell
- 首次运行需要下载 `BAAI/bge-small-zh-v1.5` 模型

## 安装依赖

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

如果无法连接 Hugging Face，可以在当前 PowerShell 临时使用镜像：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
$env:HF_HUB_DOWNLOAD_TIMEOUT = "120"
```

## 启动 API

```powershell
python -m uvicorn rag_api:app --host 127.0.0.1 --port 8001
```

Swagger 地址：

```text
http://127.0.0.1:8001/docs
```

## 使用 Docker 运行 API

构建 Docker 镜像：

```powershell
docker build -t rag-practice-api .
```

启动容器并映射端口：

```powershell
docker run --rm -p 8001:8001 rag-practice-api
```

启动后访问：

```text
健康检查：http://127.0.0.1:8001/health
接口文档：http://127.0.0.1:8001/docs
```

首次启动时可能需要下载 Embedding 模型，因此等待时间会稍长。终端显示 `Uvicorn running on http://0.0.0.0:8001` 表示启动成功。

按 `Ctrl + C` 可以停止并删除当前容器。

## 启动网页前端

本项目采用前后端分离方式运行，需要同时启动两个终端。

终端 1 启动 FastAPI：

```powershell
python -m uvicorn rag_api:app --host 127.0.0.1 --port 8001
```

终端 2 启动 Streamlit：

```powershell
python -m streamlit run streamlit_app.py --server.port 8501
```

网页地址：

```text
http://localhost:8501
```

前后端数据流：

```text
浏览器
→ Streamlit 网页
→ POST /ask
→ FastAPI
→ Embedding 检索
→ 返回答案和来源
→ 网页展示
```

可以通过环境变量修改后端地址：

```powershell
$env:RAG_API_URL = "http://127.0.0.1:8001/ask"
```

## 接口说明

### 健康检查

```http
GET /health
```

成功响应：

```json
{
  "ok": true
}
```

### 知识库问答

```http
POST /ask
```

请求示例：

```json
{
  "question": "怎样把项目上线？"
}
```

响应示例：

```json
{
  "answer": "项目上线可以使用 Docker 部署。",
  "sources": [
    {
      "title": "Docker 部署",
      "source": "deployment_notes.md",
      "score": 0.7819
    }
  ]
}
```

## 输入与错误处理

- 空字符串不符合 Pydantic 规则，返回 `422`
- 只有空格的输入返回 `400`
- 知识库没有答案时返回 `200`，同时 `sources` 为空
- 无依据时回答：`根据现有资料无法确定。`

## 运行自动评测

运行旧版 JSON 知识库评测：

```powershell
.venv\Scripts\python.exe evaluate_embedding.py
```

运行 Markdown 知识库评测：

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
.venv\Scripts\python.exe evaluate_markdown.py
```

评测指标包括：

- Top 1 准确率
- Top 3 召回率
- 平均响应时间
- 来源引用完整率

运行答案依据检查：

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
.venv\Scripts\python.exe evaluate_answer_evidence.py
```

该检查判断回答是否非空、是否包含来源，以及回答内容是否能在引用片段中找到，作为当前阶段的可解释 Faithfulness 基线。

评测结果会追加到 JSONL 日志。运行日志已通过 `.gitignore` 排除，不提交到 Git。

## 当前评测结果

当前知识库包含 18 份 Markdown 文档，切分后得到 35 个片段。

- 测试问题数量：6
- Top 1 准确率：67%
- Top 3 召回率：100%
- 来源引用完整率：100%
- 基于规则的答案依据通过率：100%
- 文档向量缓存优化前平均响应时间：674.01 ms
- 文档向量缓存优化后平均响应时间：252.66 ms
- 缓存生效后单题响应时间约为 14～17 ms

## 失败案例复盘

固定评测中有两个问题的正确来源排在 Top 2：

- RAG 完整流程：简短学习笔记与完整基础文档发生排序竞争。
- FastAPI 自动接口文档：学习笔记与官方文档都包含 Swagger 相关内容。

正确来源均进入 Top 3，说明系统具备稳定召回能力，但相近文档之间的 Top 1 排序仍有优化空间。

答案依据检查最初为 67%。复核后发现同一 Markdown 文件的多个片段在评测脚本中被错误覆盖。修复为“一个来源对应多个片段”后，通过率恢复为 100%。

## 性能优化

原始实现会在每次提问时重新计算全部文档 Embedding。随着知识库从 11 份扩充至 18 份，平均响应时间上升到 674.01 ms。

项目随后加入进程内文档向量缓存：

- 第一次查询完成模型和文档向量初始化。
- 后续查询直接复用文档向量。
- 平均响应时间下降至 252.66 ms。
- 检索准确率和来源引用完整率保持不变。

## Docker 与前端验收

项目已经完成以下测试：

- Docker 镜像构建
- 容器 `/health` 健康检查
- 容器 `/ask` 知识库问答
- Markdown 来源路径返回
- Streamlit 有答案展示
- Streamlit 无答案拒答
- 容器停止和清理

## 当前限制

- 回答暂时直接使用第一条检索片段模拟，尚未接入真实 LLM。
- 文档向量缓存只在当前进程内有效，服务重启后需要重新生成。
- 查询改写规则由人工维护。
- 当前固定评测集只有 6 个问题。
- 网页只支持单轮问答。
- 尚未部署到公网服务器。

## 下一步计划

- 将知识库扩充到 30～50 份文档。
- 将固定评测集扩充到至少 20 个问题。
- 接入真实大模型并进行 Faithfulness 评测。
- 增加上传文档和用户反馈功能。
- 部署到公网服务器。
- 增加演示截图和演示视频。

## 简历项目描述

### RAG 求职知识库助手

技术栈：Python、FastAPI、Sentence Transformers、Streamlit、Docker、Git

独立开发面向 AI 求职场景的 RAG 知识库助手，将岗位 JD、官方文档、面试笔记和学习资料统一转换为 Markdown 知识库。实现递归文档加载、滑动窗口切分、中文 Embedding 检索、查询改写、无答案拒答和来源引用，并通过 FastAPI 与 Streamlit 提供接口和网页体验。

建立固定评测集与 JSONL 日志，统计 Top 1 准确率、Top 3 召回率、来源引用完整率、答案依据通过率和响应时间。当前 18 份文档、35 个片段的测试结果为 Top 3 召回率 100%、来源引用完整率 100%、规则依据通过率 100%。通过文档向量缓存将平均响应时间从 674.01 ms 降低至 252.66 ms，并完成 Docker 构建、健康检查和前端验收。

## 面试讲解

### 1. 项目解决了什么问题？

它把分散的岗位 JD、技术文档和学习笔记整理成知识库。用户提问时，系统先检索相关片段，再返回答案和来源，减少没有资料依据的回答。

### 2. RAG 链路是什么？

文档读取 → Markdown 清洗 → 滑动窗口切分 → Embedding → 相似度排序 → TopK 召回 → 阈值拒答 → Prompt 拼接 → 返回答案和来源。

### 3. 如何评估效果？

使用固定问题集统计 Top 1 准确率和 Top 3 召回率，同时记录平均响应时间、来源引用完整率和基于规则的答案依据通过率。失败案例会写入复盘文件。

### 4. 遇到过什么问题？

知识库扩充后，平均响应时间从约 338 ms 上升到 674.01 ms。定位后发现每次提问都会重新计算全部文档向量，因此加入进程内缓存，将平均响应时间降低到 252.66 ms。

另一个问题是相近文档之间会竞争 Top 1，例如学习笔记和官方文档都包含 FastAPI Swagger 内容。正确来源仍能进入 Top 3，后续可以通过去重、重排序和扩大评测集继续优化。

### 5. 如何降低幻觉？

系统要求回答基于检索资料，低于相似度阈值时明确拒答，并返回来源路径。项目还使用规则检查回答内容是否能在引用片段中找到。后续接入真实 LLM 后会增加更完整的 Faithfulness 评测。
