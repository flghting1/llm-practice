import json

with open("day1_plan.json", "r", encoding="utf-8") as file:
    plan = json.load(file)

total_minutes = sum(task["minutes"] for task in plan["tasks"])
task_types = {task["type"] for task in plan["tasks"]}
required_types = {"learn", "code", "review"}

print("学习目标：", plan["goal"])
print("任务数量：", len(plan["tasks"]))
print("总时长：", total_minutes)
print("任务类型：", task_types)

assert total_minutes == 240, "任务总时长不是 240 分钟"
assert required_types.issubset(task_types), "缺少学习、编码或复盘任务"

print("验证通过：JSON 可解析，任务类型完整，总时长为 240 分钟。")