import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--port", default="8013")
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = getpass.getpass("API Key: ")
    if not api_key.strip():
        raise SystemExit("API key is empty")

    project_root = Path(__file__).resolve().parent
    environment = os.environ.copy()
    environment.update(
        {
            "RAG_LLM_BASE_URL": args.base_url.rstrip("/"),
            "RAG_LLM_API_KEY": api_key,
            "RAG_LLM_MODEL": args.model,
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        }
    )

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "rag_api:app",
        "--app-dir",
        str(project_root),
        "--host",
        "127.0.0.1",
        "--port",
        str(args.port),
    ]
    raise SystemExit(subprocess.run(command, env=environment).returncode)


if __name__ == "__main__":
    main()
