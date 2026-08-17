import json
from pathlib import Path

from embedding_retriever import embedding_search
from keyword_retriever import load_documents


BASE_DIR = Path(__file__).resolve().parent


def load_evaluation_cases(filename: str) -> list[dict]:
    file_path = BASE_DIR / filename
    text = file_path.read_text(encoding="utf-8")
    return json.loads(text)


def main():
    documents = load_documents("documents.json")
    cases = load_evaluation_cases(
        "evaluation_cases.json"
    )

    top1_hits = 0
    top3_hits = 0

    for case in cases:
        results = embedding_search(
            case["question"],
            documents,
            top_k=3,
        )

        retrieved_ids = [
            result["id"]
            for result in results
        ]
        expected_id = case["expected_id"]

        top1_correct = (
            bool(retrieved_ids)
            and retrieved_ids[0] == expected_id
        )
        top3_correct = expected_id in retrieved_ids

        if top1_correct:
            top1_hits += 1
        if top3_correct:
            top3_hits += 1

        print("\n问题：", case["question"])
        print("预期文档：", expected_id)
        print("召回文档：", retrieved_ids)
        print("Top 1：", "通过" if top1_correct else "失败")
        print("Top 3：", "通过" if top3_correct else "失败")

    total = len(cases)

    print("\n评测汇总")
    print("问题数量：", total)
    print("Top 1 准确率：", f"{top1_hits / total:.0%}")
    print("Top 3 召回率：", f"{top3_hits / total:.0%}")


if __name__ == "__main__":
    main()