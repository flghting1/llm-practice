import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def main():
    source_path = BASE_DIR / "documents.json"
    target_dir = (
        BASE_DIR
        / "knowledge_base"
        / "study_notes"
        / "imported"
    )
    target_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents = json.loads(
        source_path.read_text(encoding="utf-8")
    )

    for document in documents:
        target_path = (
            target_dir / document["source"]
        )

        if target_path.exists():
            print("跳过已有文件：", target_path.name)
            continue

        markdown = (
            f"# {document['title']}\n\n"
            f"{document['content']}\n"
        )
        target_path.write_text(
            markdown,
            encoding="utf-8",
        )
        print("已创建：", target_path.name)


if __name__ == "__main__":
    main()