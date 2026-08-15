def call_model(prompt: str) -> str:
    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("prompt 不能为空")

    return (
        "模拟模型回答："
        f"已收到长度为 {len(cleaned_prompt)} 的 prompt。"
    )


def main():
    prompt = """
    请根据以下资料回答问题：

    资料：RAG 会先检索相关资料，再让模型基于资料回答。

    问题：RAG 的基本流程是什么？
    """

    try:
        answer = call_model(prompt)
    except ValueError as error:
        print("调用失败：", error)
        return

    print("调用成功")
    print("回答：", answer)


if __name__ == "__main__":
    main()