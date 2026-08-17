import json
from datetime import datetime


def calculator(
    a: float,
    b: float,
    operation: str,
) -> float:
    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("除数不能为 0")
        return a / b

    raise ValueError(
        f"不支持的运算：{operation}"
    )


TOOLS = {
    "calculator": calculator,
}


def execute_tool(tool_call: dict) -> dict:
    tool_name = tool_call.get("tool")
    arguments = tool_call.get("arguments")

    if tool_name not in TOOLS:
        return {
            "status": "error",
            "error": "工具不在白名单中",
        }

    if not isinstance(arguments, dict):
        return {
            "status": "error",
            "error": "arguments 必须是对象",
        }

    print(
        "[工具日志]",
        datetime.now().isoformat(
            timespec="seconds"
        ),
        tool_name,
        arguments,
    )

    try:
        result = TOOLS[tool_name](**arguments)
    except (TypeError, ValueError) as error:
        return {
            "status": "error",
            "error": str(error),
        }

    return {
        "status": "success",
        "tool": tool_name,
        "result": result,
    }


def main():
    tool_calls = [
        {
            "tool": "delete_files",
            "arguments": {
                "path": "important_data",
            },
        },
        {
            "tool": "calculator",
            "arguments": {
                "a": 10,
                "b": 0,
                "operation": "divide",
            },
        },
        {
            "tool": "calculator",
            "arguments": "这不是一个对象",
        },
    ]

    for tool_call in tool_calls:
        response = execute_tool(tool_call)

        print(
            json.dumps(
                response,
                ensure_ascii=False,
                indent=2,
            )
        )
        print("-" * 40)


if __name__ == "__main__":
    main()