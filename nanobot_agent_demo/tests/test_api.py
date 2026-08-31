from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app


class EcommerceMultiAgentApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_reports_local_simulated_scope(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["data_scope"], "local_simulated")

    def test_supported_request_returns_trace_and_boundary(self) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": "", "OPENAI_BASE_URL": "", "OPENAI_MODEL": ""}, clear=False):
            response = self.client.post("/api/workflows", json={"request": "请输出库存预警和补货建议", "mode": "auto"})
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(body["review_passed"])
        self.assertEqual(body["route"], "inventory_alert")
        self.assertTrue(body["trace"])
        self.assertIn("模拟", body["final_answer"])

    def test_unsupported_request_is_explicitly_blocked(self) -> None:
        response = self.client.post("/api/workflows", json={"request": "预测下个月的广告 ROAS"})
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(body["review_passed"])
        self.assertIn("未识别业务类型", body["final_answer"])
