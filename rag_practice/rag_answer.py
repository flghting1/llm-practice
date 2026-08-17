from embedding_retriever import embedding_search
from keyword_retriever import load_documents


REWRITE_RULES = {
    "上线": "Docker 部署 容器 服务器",
    "代码版本": "Git 提交",
}


def rewrite_question(question: str) -> str:
    rewritten_question = question

    for original, replacement in REWRITE_RULES.items():
        rewritten_question = rewritten_question.replace(
            original,
            replacement,
        )

    return rewritten_question


def build_prompt(
    question: str,
    results: list[dict],
) -> str:
    context_parts = []

    for result in results:
        context_parts.append(
            f"标题：{result['title']}\n"
            f"正文：{result['content']}\n"
            f"来源：{result['source']}"
        )

    context = "\n\n".join(context_parts)

    return f"""
请只根据以下资料回答问题。
如果资料中没有答案，请明确回答不知道。

资料：
{context}

问题：
{question}
""".strip()


def answer_question(question: str) -> dict:
    documents = load_documents("documents.json")
    rewritten_question = rewrite_question(question)

    results = embedding_search(
        rewritten_question,
        documents,
        top_k=3,
    )

    if not results or results[0]["score"] < 0.60:
        return {
            "answer": "根据现有资料无法确定。",
            "sources": [],
            "prompt": "",
        }

    prompt = build_prompt(question, results)
    best_result = results[0]

    # 目前用检索到的正文模拟模型回答。
    answer = best_result["content"]

    return {
        "answer": answer,
        "sources": [
            {
                "title": result["title"],
                "source": result["source"],
                "score": result["score"],
            }
            for result in results
        ],
        "prompt": prompt,
    }


def main():
    question = "怎样把项目上线？"
    result = answer_question(question)

    print("问题：", question)
    print("回答：", result["answer"])
    print("来源：")

    for source in result["sources"]:
        print(
            f"- {source['title']} "
            f"({source['source']}, "
            f"score={source['score']})"
        )

    print("\n生成的 Prompt：")
    print(result["prompt"] or "未生成 Prompt")


if __name__ == "__main__":
    main()