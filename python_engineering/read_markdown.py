from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_markdown(filename: str) -> str:
    file_path = BASE_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在：{file_path}")

    return file_path.read_text(encoding="utf-8")


def main():
    content = load_markdown("sample_notes.md")

    print("文件读取成功")
    print("字符数量：", len(content))
    print("文件内容：")
    print(content)


if __name__ == "__main__":
    main()