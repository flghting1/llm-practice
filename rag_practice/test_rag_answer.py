import os
import unittest
from unittest.mock import Mock, patch

import requests

from rag_answer import answer_question, call_compatible_llm


class RagAnswerTests(unittest.TestCase):
    def test_offline_answer_uses_extract_fallback(self):
        with patch.dict(
            os.environ,
            {
                "RAG_LLM_BASE_URL": "",
                "RAG_LLM_API_KEY": "",
                "RAG_LLM_MODEL": "",
            },
            clear=False,
        ):
            result = answer_question("怎样把项目上线？")

        self.assertEqual(result["answer_mode"], "extractive_fallback")
        self.assertTrue(result["answer"])
        self.assertTrue(result["sources"])

    def test_llm_call_is_skipped_without_complete_configuration(self):
        with patch.dict(
            os.environ,
            {
                "RAG_LLM_BASE_URL": "",
                "RAG_LLM_API_KEY": "demo-key",
                "RAG_LLM_MODEL": "demo-model",
            },
            clear=False,
        ):
            answer, status = call_compatible_llm("问题", "证据")

        self.assertIsNone(answer)
        self.assertEqual(status, "not_configured")

    def test_llm_call_returns_model_answer_when_endpoint_succeeds(self):
        response = Mock()
        response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "根据资料，项目可使用 Docker 部署。",
                    },
                },
            ],
        }

        with patch.dict(
            os.environ,
            {
                "RAG_LLM_BASE_URL": "https://example.invalid/v1",
                "RAG_LLM_API_KEY": "demo-key",
                "RAG_LLM_MODEL": "demo-model",
            },
            clear=False,
        ), patch("rag_answer.requests.post", return_value=response) as post:
            answer, status = call_compatible_llm("如何部署？", "Docker 部署资料")

        self.assertEqual(answer, "根据资料，项目可使用 Docker 部署。")
        self.assertEqual(status, "success")
        self.assertEqual(
            post.call_args.kwargs["json"]["model"],
            "demo-model",
        )

    def test_low_similarity_result_returns_no_answer_mode(self):
        with patch("rag_answer.embedding_search", return_value=[]):
            result = answer_question("没有资料的问题")

        self.assertEqual(result["answer_mode"], "no_answer")
        self.assertEqual(result["answer"], "根据现有资料无法确定。")
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["generation_status"], "not_called")

    def test_llm_call_reports_http_status_without_response_body(self):
        response = Mock(status_code=429)
        error = requests.HTTPError(response=response)
        response.raise_for_status.side_effect = error

        with patch.dict(
            os.environ,
            {
                "RAG_LLM_BASE_URL": "https://example.invalid/v1",
                "RAG_LLM_API_KEY": "demo-key",
                "RAG_LLM_MODEL": "demo-model",
            },
            clear=False,
        ), patch("rag_answer.requests.post", return_value=response):
            answer, status = call_compatible_llm("如何部署？", "Docker 部署资料")

        self.assertIsNone(answer)
        self.assertEqual(status, "http_429")


if __name__ == "__main__":
    unittest.main()
