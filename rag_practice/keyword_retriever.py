import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_documents(filename: str) -> list[dict]:
    file_path = BASE_DIR / filename
    text = file_path.read_text(encoding="utf-8")
    return json.loads(text)


def split_text(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError(
            "chunk_size 必须大于 overlap"
        )

    chunks = []
    start = 0

    while start < len(text):
        end = min(
            start + chunk_size,
            len(text),
        )
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - overlap

    return chunks


def load_markdown_documents(
    folder_name: str,
) -> list[dict]:
    folder_path = BASE_DIR / folder_name
    documents = []

    markdown_files = sorted(
        folder_path.rglob("*.md")
    )

    for index, file_path in enumerate(
        markdown_files,
        start=1,
    ):
        content = file_path.read_text(
            encoding="utf-8"
        )
        lines = content.splitlines()
        title = file_path.stem.replace("_", " ")

        if lines and lines[0].startswith("# "):
            title = lines[0][2:].strip()

        chunks = split_text(content)

        for chunk_index, chunk in enumerate(
            chunks,
            start=1,
        ):
            documents.append(
                {
                    "id": (
                        f"md-{index}-{chunk_index}"
                    ),
                    "title": title,
                    "content": chunk,
                    "source": file_path.relative_to(
                        BASE_DIR
                    ).as_posix(),
                    "chunk_index": chunk_index,
                }
            )

    return documents


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
    question = "RAG 的完整流程是什么？"
    documents = load_markdown_documents(
        "knowledge_base"
    )
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
        print("片段：", result["chunk_index"])
        print("正文：", result["content"])


if __name__ == "__main__":
    main()