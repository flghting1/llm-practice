import os

import requests

from embedding_retriever import embedding_search
from keyword_retriever import (
    load_markdown_documents,
)


REWRITE_RULES = {
    "上线": "Docker 部署 容器 服务器",
    "代码版本": "Git 提交",
}


def call_compatible_llm(
    question: str,
    evidence: str,
) -> tuple[str | None, str]:
    """Call an optional OpenAI-compatible endpoint without breaking offline mode."""
    base_url = os.getenv("RAG_LLM_BASE_URL", "").rstrip("/")
    api_key = os.getenv("RAG_LLM_API_KEY", "")
    model = os.getenv("RAG_LLM_MODEL", "")

    if not base_url or not api_key or not model:
        return None, "not_configured"

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是企业知识库助手。只能根据用户提供的证据回答，"
                    "证据不足时明确回答‘根据现有资料无法确定’，不要补充外部知识。"
                ),
            },
            {
                "role": "user",
                "content": f"问题：{question}\n\n证据：{evidence}",
            },
        ],
    }

    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except requests.HTTPError as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else "unknown"
        )
        return None, f"http_{status_code}"
    except requests.RequestException:
        return None, "network_error"
    except (KeyError, IndexError, TypeError, ValueError):
        return None, "invalid_response"

    answer = str(content).strip()
    if not answer:
        return None, "empty_response"

    return answer, "success"


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
    documents = load_markdown_documents(
    "knowledge_base"
)
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
            "answer_mode": "no_answer",
            "generation_status": "not_called",
        }

    prompt = build_prompt(question, results)
    best_result = results[0]

    evidence = "\n\n".join(
        f"标题：{result['title']}\n"
        f"正文：{result['content']}\n"
        f"来源：{result['source']}"
        for result in results
    )
    generated_answer, generation_status = call_compatible_llm(question, evidence)
    answer_mode = "llm" if generated_answer else "extractive_fallback"
    answer = generated_answer or best_result["content"]

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
        "answer_mode": answer_mode,
        "generation_status": generation_status,
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
