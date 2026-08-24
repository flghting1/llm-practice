"""Lightweight portfolio Agent API.

The server never executes arbitrary commands and file access is limited to
the local knowledge_base directory. An optional OpenAI-compatible endpoint
can summarize retrieved evidence when AGENT_LLM_BASE_URL and AGENT_LLM_API_KEY
are configured on the server.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = (BASE_DIR / "knowledge_base").resolve()
app = FastAPI(title="Personal Knowledge Agent", version="1.0.0")


def load_agent_documents(folder_name):
    folder = BASE_DIR / folder_name
    documents = []
    for index, path in enumerate(sorted(folder.rglob("*.md")), 1):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else path.stem
        documents.append({"id": "agent-%s" % index, "title": title, "content": text, "source": path.relative_to(BASE_DIR).as_posix()})
    return documents


def keyword_search(question, documents, top_k=3):
    tokens = set(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", question.lower()))
    ranked = []
    for document in documents:
        text = (document["title"] + " " + document["content"]).lower()
        score = sum(1 for token in tokens if token in text)
        if score:
            ranked.append(dict(document, score=score))
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    mode: str = "knowledge"


def safe_knowledge_path(relative_path: str) -> Path:
    candidate = (KNOWLEDGE_DIR / relative_path).resolve()
    if candidate != KNOWLEDGE_DIR and KNOWLEDGE_DIR not in candidate.parents:
        raise HTTPException(status_code=400, detail="只能访问知识库目录")
    return candidate


def search_web(question: str) -> List[Dict[str, str]]:
    """Use DuckDuckGo's public HTML endpoint; no API key is required."""
    try:
        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": question},
            headers={"User-Agent": "portfolio-agent/1.0"},
            timeout=8,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return [{"title": "搜索暂时不可用", "snippet": str(exc), "url": ""}]

    from html.parser import HTMLParser

    class ResultParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.results = []
            self.current = None
            self.in_title = False
            self.in_snippet = False

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "a" and "result__a" in attrs.get("class", ""):
                self.current = {"title": "", "snippet": "", "url": attrs.get("href", "")}
                self.in_title = True
            elif tag in {"a", "div"} and self.current and "result__snippet" in attrs.get("class", ""):
                self.in_snippet = True

        def handle_data(self, data):
            if self.current and self.in_title:
                self.current["title"] += data
            elif self.current and self.in_snippet:
                self.current["snippet"] += data

        def handle_endtag(self, tag):
            if tag == "a" and self.in_title:
                self.in_title = False
            if self.current and self.in_snippet and tag in {"a", "div"}:
                self.in_snippet = False
                self.results.append(self.current)
                self.current = None

    parser = ResultParser()
    parser.feed(response.text)
    return parser.results[:5]


def model_summary(question: str, evidence: str) -> Optional[str]:
    base_url = os.getenv("AGENT_LLM_BASE_URL", "").rstrip("/")
    api_key = os.getenv("AGENT_LLM_API_KEY", "")
    model = os.getenv("AGENT_LLM_MODEL", "qwen-turbo")
    if not base_url or not api_key:
        return None
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": 0.2,
                "messages": [
                    {"role": "system", "content": "只根据提供的证据回答，证据不足时明确说明。"},
                    {"role": "user", "content": f"问题：{question}\n\n证据：{evidence}"},
                ],
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, TypeError):
        return None


@app.get("/agent/health")
def health() -> dict:
    return {"ok": True, "service": "personal-knowledge-agent"}


@app.get("/agent/files")
def files() -> dict:
    items = [
        str(path.relative_to(BASE_DIR).as_posix())
        for path in sorted(KNOWLEDGE_DIR.rglob("*.md"))
    ]
    return {"files": items, "count": len(items)}


@app.post("/agent/ask")
def ask(request: AgentRequest) -> dict:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question 不能为空")
    if request.mode not in {"knowledge", "search", "files"}:
        raise HTTPException(status_code=400, detail="mode 必须是 knowledge、search 或 files")

    if request.mode == "files":
        results = keyword_search(question, load_agent_documents("knowledge_base"), top_k=5)
        return {
            "answer": "已在受限知识库目录中找到相关文件。",
            "evidence": [
                {"title": item["title"], "source": item["source"], "score": item["score"]}
                for item in results
            ],
            "tool": "knowledge_files",
        }

    if request.mode == "search":
        web_results = search_web(question)
        evidence = "\n".join(f"{item['title']}：{item['snippet']} ({item['url']})" for item in web_results)
        return {
            "answer": model_summary(question, evidence) or "已完成联网搜索，请查看下方结果。",
            "evidence": web_results,
            "tool": "web_search",
        }

    results = keyword_search(question, load_agent_documents("knowledge_base"), top_k=3)
    if not results:
        return {"answer": "根据现有资料无法确定。", "evidence": [], "tool": "knowledge_search"}
    evidence = "\n\n".join(f"{item['title']}\n{item['content']}\n来源：{item['source']}" for item in results)
    return {
        "answer": model_summary(question, evidence) or results[0]["content"],
        "evidence": [
            {"title": item["title"], "source": item["source"], "score": item["score"], "snippet": item["content"]}
            for item in results
        ],
        "tool": "knowledge_search",
    }
