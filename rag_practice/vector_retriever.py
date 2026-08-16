from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)
from sklearn.metrics.pairwise import (
    cosine_similarity,
)

from keyword_retriever import load_documents


def vector_search(
    question: str,
    documents: list[dict],
    top_k: int = 3,
) -> list[dict]:
    document_texts = [
        document["title"] + " " + document["content"]
        for document in documents
    ]

    all_texts = document_texts + [question]

    vectorizer = TfidfVectorizer(
        analyzer="char",
        ngram_range=(1, 3),
    )

    vectors = vectorizer.fit_transform(all_texts)

    document_vectors = vectors[:-1]
    question_vector = vectors[-1]

    scores = cosine_similarity(
        question_vector,
        document_vectors,
    )[0]

    ranked_indexes = scores.argsort()[::-1]
    results = []

    for index in ranked_indexes[:top_k]:
        if scores[index] <= 0:
            continue

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

    results = vector_search(
        question,
        documents,
        top_k=3,
    )

    print("问题：", question)
    print("召回数量：", len(results))

    for result in results:
        print("\n标题：", result["title"])
        print("相似度：", result["score"])
        print("来源：", result["source"])
        print("正文：", result["content"])


if __name__ == "__main__":
    main()