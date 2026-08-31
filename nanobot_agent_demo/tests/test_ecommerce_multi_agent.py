from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ecommerce_multi_agent.workflow import run_workflow


class EcommerceMultiAgentWorkflowTests(unittest.TestCase):
    def run_in_temp_database(self, request: str):
        with tempfile.TemporaryDirectory() as directory:
            return run_workflow(request, Path(directory) / "demo.sqlite3")

    def test_sales_report_uses_simulated_data_and_is_reviewed(self) -> None:
        state = self.run_in_temp_database("生成 2026-08-30 的销售日报")
        self.assertEqual(state.route, "sales_report")
        self.assertTrue(state.review_passed)
        self.assertIn("404.00", state.final_answer)
        self.assertIn("模拟电商数据", state.final_answer)

    def test_inventory_alert_lists_only_below_safety_stock_products(self) -> None:
        state = self.run_in_temp_database("请输出库存预警")
        self.assertTrue(state.review_passed)
        self.assertIn("CB-001", state.final_answer)
        self.assertIn("NB-003", state.final_answer)
        self.assertNotIn("BM-002：", state.final_answer)

    def test_customer_service_reply_is_grounded_in_policy(self) -> None:
        state = self.run_in_temp_database("客户想退货，整理客服话术")
        self.assertTrue(state.review_passed)
        self.assertIn("7 天", state.final_answer)
        self.assertIn("customer_service_rules.md", state.final_answer)

    def test_unknown_request_is_blocked(self) -> None:
        state = self.run_in_temp_database("帮我预测下个月的广告 ROAS")
        self.assertFalse(state.review_passed)
        self.assertIn("未识别业务类型", state.final_answer)


if __name__ == "__main__":
    unittest.main()
