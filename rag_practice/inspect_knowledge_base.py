from collections import Counter

from keyword_retriever import (
    load_markdown_documents,
)


def main():
    documents = load_markdown_documents(
        "knowledge_base"
    )

    source_counts = Counter(
        document["source"]
        for document in documents
    )

    print("Markdown 文档数量：", len(source_counts))
    print("切分后的片段数量：", len(documents))
    print("\n各文档片段数量：")

    for source, count in sorted(
        source_counts.items()
    ):
        print(f"- {source}: {count}")


if __name__ == "__main__":
    main()