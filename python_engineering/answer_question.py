import json
from pathlib import Path

from model_client import call_model


BASE_DIR = Path(__file__).resolve().parent


def load_sections(filename: str) -> list[dict]:
    file_path = BASE_DIR / filename
    json_text = file_path.read_text(encoding="utf-8")
    return json.loads(json_text)


def find_relevant_sections(
    sections: list[dict],
    question: str,
) -> list[dict]:
    relevant_sections = []

    for section in sections:
        title = section["title"]

        if title.lower() in question.lower():
            relevant_sections.append(section)

    return relevant_sections


def build_prompt(
    question: str,
    sections: list[dict],
) -> str:
    context_parts = []

    for section in sections:
        context_parts.append(
            f"标题：{section['title']}\n"
            f"正文：{section['content']}\n"
            f"来源：{section['source']}"
        )

    context = "\n\n".join(context_parts)

    return f"""
请只根据提供的资料回答问题。

资料：
{context}

问题：
{question}
""".strip()


def main():
    question = "RAG 的基本流程是什么？"

    sections = load_sections("sections.json")
    relevant_sections = find_relevant_sections(
        sections,
        question,
    )

    if not relevant_sections:
        print("没有找到相关资料")
        return

    prompt = build_prompt(
        question,
        relevant_sections,
    )
    answer = call_model(prompt)

    print("检索数量：", len(relevant_sections))
    print("使用来源：", relevant_sections[0]["source"])
    print("生成的 Prompt：")
    print(prompt)
    print("\n模型返回：")
    print(answer)


if __name__ == "__main__":
    main()