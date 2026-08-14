import json

model_output = """```json
{
    "matched_skills":["Python","Git"],
    "missing_skills":["Docker"],
    "match_score":"50",
    "risk_level":"medium",
    "next_actions":["学习 Docker"]
}
```"""

try:
    result = json.loads(model_output)
    print("第一次解析通过")
except json.JSONDecodeError:
    print("第一次解析失败:模型返回了 Markdown 代码块")

    cleaned_output = model_output.strip()

    if cleaned_output.startswith("```json"):
        cleaned_output = cleaned_output[len("```json"):]
    if cleaned_output.endswith("```"):
        cleaned_output = cleaned_output[:-3]

    result = json.loads(cleaned_output.strip())
    print("格式修复成功")
    print("匹配分数:",result["match_score"])    