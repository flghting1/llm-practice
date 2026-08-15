import json
from pathlib import Path

from read_markdown import load_markdown
from split_markdown import split_by_headings


BASE_DIR = Path(__file__).resolve().parent


def save_sections(
    sections: list[dict],
    filename: str,
) -> Path:
    output_path = BASE_DIR / filename

    records = []

    for index, section in enumerate(sections, start=1):
        records.append(
            {
                "id": index,
                "title": section["title"],
                "content": section["content"],
                "source": "sample_notes.md",
            }
        )

    json_text = json.dumps(
        records,
        ensure_ascii=False,
        indent=2,
    )

    output_path.write_text(
        json_text,
        encoding="utf-8",
    )

    return output_path


def main():
    try:
        markdown = load_markdown("sample_notes.md")
        sections = split_by_headings(markdown)
        output_path = save_sections(
            sections,
            "sections.json",
        )
    except FileNotFoundError as error:
        print("处理失败：找不到输入文件")
        print("错误详情：", error)
        return

    print("保存成功：", output_path)
    print("保存数量：", len(sections))


if __name__ == "__main__":
    main()