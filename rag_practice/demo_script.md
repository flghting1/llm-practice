# RAG 求职知识库助手演示脚本

## 演示目标

展示项目如何读取岗位 JD 和学习资料，完成语义检索、来源引用、无答案拒答，以及可选真实模型生成。

## 演示前准备

### 本地前端

真实模型演示时，从任意 PowerShell 目录执行以下命令，按提示隐藏输入 API Key：

```powershell
& "C:\Users\flghting\Documents\ChatGPT\AI职业\llm_practice\rag_practice\.venv\Scripts\python.exe" "C:\Users\flghting\Documents\ChatGPT\AI职业\llm_practice\rag_practice\start_with_llm.py" --base-url "https://your-openai-compatible-endpoint/v1" --model "your-model-name" --port 8013
```

验收真实模型调用：

```powershell
$response = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8013/ask -ContentType "application/json; charset=utf-8" -Body '{"question":"怎样把项目上线？"}'
$response.answer_mode
$response.generation_status
```

两个字段分别返回 `llm` 和 `success`，才说明本次真实调用成功。随后演示“公司年会什么时候举办？”应返回 `no_answer` 和空来源。

终端 1：

```powershell
$env:HF_HUB_OFFLINE = "1"
$env:TRANSFORMERS_OFFLINE = "1"
.venv\Scripts\python.exe -m uvicorn rag_api:app --host 127.0.0.1 --port 8001
