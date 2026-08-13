import json

model_output = """
{
  "matched_skills": ["FastAPI", "RAG"],
  "missing_skills": ["Docker", "SQL"],
  "risk_level": "medium",
  "next_actions": ["学习 Docker 基础知识", "学习 SQL 基础知识"]
}
"""

required_fields = {
    "matched_skills",
    "missing_skills",
    "risk_level",
    "next_actions",
}

try:
    result = json.loads(model_output)

    missing_fields = required_fields - result.keys()

    if missing_fields:
        print("校验失败：缺少字段", missing_fields)
    elif not isinstance(result["matched_skills"], list):
        print("校验失败：matched_skills 必须是列表")
    elif not isinstance(result["missing_skills"], list):
        print("校验失败：missing_skills 必须是列表")
    elif result["risk_level"] not in {"low", "medium", "high"}:
        print("校验失败：risk_level 不合法")
    elif not isinstance(result["next_actions"], list):
        print("校验失败：next_actions 必须是列表")
    else:
        print("校验通过：结构化输出可以被程序使用")
        print("匹配技能：", result["matched_skills"])
        print("缺失技能：", result["missing_skills"])
        print("风险等级：", result["risk_level"])
        print("下一步：", result["next_actions"])

except json.JSONDecodeError as error:
    print("校验失败：不是合法 JSON")
    print(error)