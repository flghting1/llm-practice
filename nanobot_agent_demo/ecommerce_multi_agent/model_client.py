"""Optional OpenAI-compatible content generation for the demo workflow."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def model_is_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_BASE_URL") and os.getenv("OPENAI_MODEL"))


def generate_grounded_draft(
    request: str,
    deterministic_draft: str,
    knowledge: list[dict[str, str]],
    data: dict[str, Any],
) -> tuple[str, str]:
    """Return generated text or an error message without leaking credentials."""
    if not model_is_configured():
        return deterministic_draft, "未配置 OPENAI_API_KEY、OPENAI_BASE_URL 或 OPENAI_MODEL。"

    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    url = base_url if base_url.endswith("/chat/completions") else f"{base_url}/chat/completions"
    evidence = {
        "rules": [{"source": item["source"], "excerpt": item["excerpt"]} for item in knowledge],
        "data": data,
    }
    system_prompt = (
        "你是电商运营文案助手。只能基于给出的草稿和证据改写，不得编造价格、库存、销量、平台规则或承诺。"
        "保留必要的模拟数据说明；输出纯文本，不要解释你的推理。"
    )
    user_prompt = (
        f"用户请求：{request}\n\n确定性草稿：\n{deterministic_draft}\n\n"
        f"可用证据：\n{json.dumps(evidence, ensure_ascii=False)}"
    )
    payload = json.dumps(
        {
            "model": os.environ["OPENAI_MODEL"],
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
    ).encode("utf-8")
    request_object = Request(
        url,
        data=payload,
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request_object, timeout=25) as response:
            body = json.loads(response.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"].strip()
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, UnicodeDecodeError, json.JSONDecodeError) as error:
        return deterministic_draft, f"模型调用失败：{type(error).__name__}"
    if not content:
        return deterministic_draft, "模型未返回有效内容。"
    return content, ""
