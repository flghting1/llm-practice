from read_markdown import load_markdown


def split_by_headings(markdown: str) -> list[dict]:
    sections = []
    current_title = None
    current_lines = []

    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections.append(
                    {
                        "title": current_title,
                        "content": "\n".join(current_lines).strip(),
                    }
                )

            current_title = line.removeprefix("## ").strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections.append(
            {
                "title": current_title,
                "content": "\n".join(current_lines).strip(),
            }
        )

    return sections


def main():
    markdown = load_markdown("sample_notes.md")
    sections = split_by_headings(markdown)

    print("切分数量：", len(sections))

    for index, section in enumerate(sections, start=1):
        print(f"\n第 {index} 段")
        print("标题：", section["title"])
        print("正文：", section["content"])


if __name__ == "__main__":
    main()