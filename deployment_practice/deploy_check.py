from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

PROJECTS = {
    "rag_practice": [
        "Dockerfile",
        "rag_api.py",
        "knowledge_base",
        "README.md",
    ],
    "sql_agent_practice": [
        "Dockerfile",
        "sql_api.py",
        "sql_agent.py",
        "sql_tool.py",
        "requirements.txt",
        "README.md",
    ],
    "resume_matcher_practice": [
        "Dockerfile",
        "resume_api.py",
        "matcher.py",
        "match_schema.py",
        "requirements.txt",
        "README.md",
    ],
}


def main():
    all_passed = True

    print("部署前文件检查")
    print("项目根目录：", BASE_DIR)

    for project_name, required_files in PROJECTS.items():
        project_dir = BASE_DIR / project_name
        print(f"\n[{project_name}]")

        if not project_dir.exists():
            print("项目目录：失败")
            all_passed = False
            continue

        print("项目目录：通过")

        for relative_path in required_files:
            target = project_dir / relative_path

            if target.exists():
                print(f"  {relative_path}: 通过")
            else:
                print(f"  {relative_path}: 失败")
                all_passed = False

    print("\n部署前检查结果：")

    if all_passed:
        print("全部通过，可以进入 Docker 自动化部署")
    else:
        print("存在缺失文件，暂不进入部署")

    raise SystemExit(0 if all_passed else 1)


if __name__ == "__main__":
    main()