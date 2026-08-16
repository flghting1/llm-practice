import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_documents(filename: str) -> list[dict]:
    file_path = BASE_DIR / filename
    text = file_path.read_text(encoding="utf-8")
    return json.loads(text)


def tokenize(text: str) -> set[str]:
    tokens = set()

    english_words = re.findall(
        r"[A-Za-z0-9_]+",
        text.lower(),
    )
    tokens.update(english_words)

    chinese_parts = re.findall(
        r"[\u4e00-\u9fff]+",
        text,
    )

    for part in chinese_parts:
        for index in range(len(part) - 1):
            tokens.add(part[index:index + 2])

    return tokens


def keyword_search(
    question: str,
    documents: list[dict],
    top_k: int = 3,
) -> list[dict]:
    question_tokens = tokenize(question)
    results = []

    for document in documents:
        document_text = (
            document["title"]
            + " "
            + document["content"]
        )
        document_tokens = tokenize(document_text)

        common_tokens = (
            question_tokens & document_tokens
        )
        score = len(common_tokens)

        if score > 0:
            results.append(
                {
                    **document,
                    "score": score,
                    "matched_tokens": sorted(common_tokens),
                }
            )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]


def main():
    question = "怎样把项目上线？"
    documents = load_documents("documents.json")
    results = keyword_search(
        question,
        documents,
        top_k=3,
    )

    print("问题：", question)
    print("召回数量：", len(results))

    for result in results:
        print("\n标题：", result["title"])
        print("分数：", result["score"])
        print("匹配词：", result["matched_tokens"])
        print("来源：", result["source"])
        print("正文：", result["content"])


if __name__ == "__main__":
    main()