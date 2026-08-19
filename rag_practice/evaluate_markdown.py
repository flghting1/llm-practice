import json
import time
from datetime import datetime
from pathlib import Path

from embedding_retriever import embedding_search
from keyword_retriever import load_markdown_documents


BASE_DIR = Path(__file__).resolve().parent


def load_evaluation_cases(filename: str) -> list[dict]:
    file_path = BASE_DIR / filename
    return json.loads(
        file_path.read_text(encoding="utf-8")
    )


def main():
    documents = load_markdown_documents("knowledge_base")
    cases = load_evaluation_cases(
        "markdown_evaluation_cases.json"
    )

    top1_hits = 0
    top3_hits = 0
    citation_complete_hits = 0
    total_latency_ms = 0
    case_records = []

    for case in cases:
        started_at = time.perf_counter()
        results = embedding_search(
            case["question"],
            documents,
            top_k=3,
        )

        latency_ms = round(
            (time.perf_counter() - started_at) * 1000,
            2,
        )
        total_latency_ms += latency_ms

        expected_source = case["expected_source"]
        retrieved_sources = [
            result["source"]
            for result in results
        ]

        top1_correct = (
            bool(retrieved_sources)
            and retrieved_sources[0] == expected_source
        )
        top3_correct = expected_source in retrieved_sources
        citation_complete = (
           bool(results)
           and all(
               bool(result.get("source"))
               for result in results
           )
        )

        if citation_complete:
            citation_complete_hits += 1

        if top1_correct:
            top1_hits += 1

        if top3_correct:
            top3_hits += 1

        print("\n问题：", case["question"])
        print("预期来源：", expected_source)
        print("召回来源：")

        for rank, result in enumerate(results, start=1):
            print(
                f"  Top {rank}: "
                f"{result['source']} "
                f"(片段 {result['chunk_index']}, "
                f"相似度 {result['score']})"
            )

        print(
            "Top 1：",
            "通过" if top1_correct else "失败"
        )
        print(
            "Top 3：",
            "通过" if top3_correct else "失败"
        )
        print("响应时间：", latency_ms, "ms")
        print(
            "来源引用：",
            "完整" if citation_complete else "缺失",
        )

        case_records.append(
            {
                "question": case["question"],
                "expected_source": expected_source,
                "retrieved_sources": retrieved_sources,
                "top1_correct": top1_correct,
                "top3_correct": top3_correct,
                "latency_ms": latency_ms,
                "citation_complete": citation_complete,
            }
        )

    total = len(cases)
    top1_accuracy = top1_hits / total
    top3_recall = top3_hits / total

    print("\n评测汇总")
    print("问题数量：", total)
    print("Top 1 准确率：", f"{top1_accuracy:.0%}")
    print("Top 3 召回率：", f"{top3_recall:.0%}")
    average_latency_ms = round(
        total_latency_ms / total,
        2,
    )

    source_citation_completeness = (
    citation_complete_hits / total
    )

    print(
        "平均响应时间：",
        average_latency_ms,
        "ms",
    )

    print(
        "来源引用完整率：",
        f"{source_citation_completeness:.0%}",
    )

    log_record = {
        "evaluated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "knowledge_base": "knowledge_base",
        "total": total,
        "top1_accuracy": top1_accuracy,
        "top3_recall": top3_recall,
        "average_latency_ms": average_latency_ms,
        "source_citation_completeness": (
            source_citation_completeness
        ),
        "cases": case_records,
    }

    log_path = BASE_DIR / "markdown_evaluation_results.jsonl"

    with log_path.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                log_record,
                ensure_ascii=False
            ) + "\n"
        )

    print(
        "评测日志：",
        log_path.name
    )


if __name__ == "__main__":
    main()