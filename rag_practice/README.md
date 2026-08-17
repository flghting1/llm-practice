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

## 当前评测结果

测试问题数量：5。

- 关键词检索 Top 1 准确率：60%
- Embedding Top 1 准确率：80%
- 优化前 Embedding Top 3 召回率：80%
- 优化知识库后 Embedding Top 3 召回率：100%

已记录的坏案例：

- “怎样把项目上线？”仅使用原始 Embedding 时排序错误
- 补充知识库表达后，Docker 文档进入 Top 3
- 加入查询改写后，Docker 文档排到第一

## 当前限制

- 知识库目前只有少量练习文档
- 回答暂时使用第一条检索资料模拟，尚未调用真实 LLM
- 文档向量会在每次请求时重新计算
- 查询改写规则目前为人工维护
- 网页目前只支持单轮问答
- 还没有上传文档和用户反馈功能

## 下一步计划

- 缓存文档向量，减少重复计算
- 接入真实大模型 API
- 增加知识库文档数量
- 增加响应时间和错误日志