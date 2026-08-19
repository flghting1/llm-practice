import json
from datetime import datetime
from pathlib import Path

from keyword_retriever import load_markdown_documents
from rag_answer import answer_question


BASE_DIR = Path(__file__).resolve().parent


def load_cases() -> list[dict]:
    path = BASE_DIR / "markdown_evaluation_cases.json"
    return json.loads(
        path.read_text(encoding="utf-8")
    )


def main():
    documents = load_markdown_documents("knowledge_base")
    source_map = {}

    for document in documents:
        source_map.setdefault(
            document["source"],
            [],
        ).append(document["content"])

    cases = load_cases()
    supported_hits = 0
    records = []

    for case in cases:
        result = answer_question(case["question"])
        answer = result["answer"].strip()
        sources = result["sources"]

        source_present = bool(sources)
        answer_nonempty = bool(answer)
        evidence_supported = False

        if source_present and answer_nonempty:
            answer_prefix = answer[:80]

            for source in sources:
                contents = source_map.get(
                    source["source"],
                    [],
                )

                if any(
                    answer_prefix in content
                    for content in contents
                ):
                    evidence_supported = True
                    break

        if evidence_supported:
            supported_hits += 1

        print("\n问题：", case["question"])
        print("回答非空：", "是" if answer_nonempty else "否")
        print("来源数量：", len(sources))
        print(
            "规则依据检查：",
            "通过" if evidence_supported else "失败",
        )

        records.append(
            {
                "question": case["question"],
                "answer_nonempty": answer_nonempty,
                "source_present": source_present,
                "evidence_supported": evidence_supported,
                "sources": sources,
            }
        )

    total = len(cases)
    evidence_rate = supported_hits / total

    print("\n答案依据检查汇总")
    print("问题数量：", total)
    print(
        "规则依据通过率：",
        f"{evidence_rate:.0%}",
    )

    log_record = {
        "evaluated_at": datetime.now()
        .astimezone()
        .isoformat(timespec="seconds"),
        "total": total,
        "evidence_rate": evidence_rate,
        "cases": records,
    }

    log_path = BASE_DIR / "answer_evidence_results.jsonl"

    with log_path.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                log_record,
                ensure_ascii=False,
            ) + "\n"
        )

    print("评测日志：", log_path.name)


if __name__ == "__main__":
    main()