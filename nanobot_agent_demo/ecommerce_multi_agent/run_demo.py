"""Run a deterministic end-to-end Multi-Agent demo from the command line."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .workflow import run_workflow


SCENARIOS = {
    "listing": "请生成商品标题和详情页文案",
    "customer_service": "客户想申请退货，请整理客服话术",
    "sales_report": "生成 2026-08-30 的销售日报",
    "inventory_alert": "请输出库存预警和补货建议",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local e-commerce Multi-Agent demo.")
    parser.add_argument("--scenario", choices=SCENARIOS, default="sales_report")
    parser.add_argument("--request", help="Override the built-in scenario request.")
    args = parser.parse_args()
    state = run_workflow(args.request or SCENARIOS[args.scenario])
    print(json.dumps(asdict(state), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
