# RAG 求职知识库助手演示脚本

## 演示目标

展示项目如何读取岗位 JD 和学习资料，完成语义检索、来源引用、无答案拒答和 Docker 运行。

## 演示前准备

### 本地前端

终端 1：

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
.venv\Scripts\python.exe -m uvicorn rag_api:app --host 127.0.0.1 --port 8001