import json
import re

from tool_agent import execute_tool


OPERATION_KEYWORDS = {
    "加": "add",
    "减": "subtract",
    "乘": "multiply",
    "除": "divide",
}
MAX_RETRIES = 1


def decide_action(
    question: str,
) -> dict | None:
    operation = None

    for keyword, operation_name in (
        OPERATION_KEYWORDS.items()
    ):
        if keyword in question:
            operation = operation_name
            break

    numbers = re.findall(
        r"-?\d+(?:\.\d+)?",
        question,
    )

    if operation is None:
        return None

    if len(numbers) != 2:
        return None

    return {
        "tool": "calculator",
        "arguments": {
            "a": float(numbers[0]),
            "b": float(numbers[1]),
            "operation": operation,
        },
    }


def run_agent(question: str) -> dict:
    state = {
        "question": question,
        "steps": [],
    }

    tool_call = decide_action(question)

    if tool_call is None:
        return {
            "answer": "无法确定要调用的工具。",
            "state": state,
        }

    state["steps"].append(
        {
            "type": "decision",
            "content": tool_call,
        }
    )

    attempt = 0
    tool_result = None

    while attempt <= MAX_RETRIES:
        tool_result = execute_tool(tool_call)

        state["steps"].append(
            {
                "type": "observation",
                "attempt": attempt + 1,
                "content": tool_result,
            }
        )

        if tool_result["status"] == "success":
            break

        if attempt == MAX_RETRIES:
            break

        state["steps"].append(
            {
                "type": "retry",
                "content": "工具失败，准备最后一次重试",
            }
        )

        attempt += 1

    if tool_result["status"] == "error":
        answer = (
            "工具执行失败："
            + tool_result["error"]
        )
    else:
        answer = (
            "计算结果是 "
            + str(tool_result["result"])
        )

    return {
        "answer": answer,
        "state": state,
    }

    tool_result = execute_tool(tool_call)

    state["steps"].append(
        {
            "type": "observation",
            "content": tool_result,
        }
    )

    if tool_result["status"] == "error":
        answer = (
            "工具执行失败："
            + tool_result["error"]
        )
    else:
        answer = (
            "计算结果是 "
            + str(tool_result["result"])
        )

    return {
        "answer": answer,
        "state": state,
    }


def main():
    questions = [
        "请计算 15 乘 4",
        "请计算 10 除 0",
        "帮我查询今天的天气",
        "请计算 5 加多少",
    ]

    for question in questions:
        print("\n用户问题：", question)

        result = run_agent(question)

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                indent=2,
            )
        )
        print("=" * 50)


if __name__ == "__main__":
    main()