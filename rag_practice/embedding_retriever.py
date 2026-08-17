from sentence_transformers import SentenceTransformer

from keyword_retriever import load_documents


MODEL_NAME = "BAAI/bge-small-zh-v1.5"
MODEL = SentenceTransformer(MODEL_NAME)


def embedding_search(
    question: str,
    documents: list[dict],
    top_k: int = 3,
) -> list[dict]:
    document_texts = [
        document["title"] + " " + document["content"]
        for document in documents
    ]

    document_embeddings = MODEL.encode(
        document_texts,
        normalize_embeddings=True,
    )

    question_embedding = MODEL.encode(
        question,
        normalize_embeddings=True,
    )

    scores = question_embedding @ document_embeddings.T
    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:
        results.append(
            {
                **documents[index],
                "score": round(float(scores[index]), 4),
            }
        )

    return results


def main():
    question = "怎么保存代码版本？"
    documents = load_documents("documents.json")

    results = embedding_search(
        question,
        documents,
        top_k=3,
    )

    print("问题：", question)

    for result in results:
        print("\n标题：", result["title"])
        print("相似度：", result["score"])
        print("来源：", result["source"])


if __name__ == "__main__":
    main()