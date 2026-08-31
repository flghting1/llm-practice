"""A small Multi-Agent orchestration demo for e-commerce operations.

Each role writes to shared state. The deterministic routing and review stages make
the workflow testable without representing model-generated content as ground truth.
"""

from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .seed_data import DATABASE_PATH, create_demo_database


KNOWLEDGE_DIR = Path(__file__).parent / "knowledge_base"
SUPPORTED_ROUTES = {"listing", "customer_service", "sales_report", "inventory_alert"}


@dataclass
class WorkflowState:
    request: str
    route: str = ""
    knowledge: list[dict[str, str]] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    draft: str = ""
    warnings: list[str] = field(default_factory=list)
    review_passed: bool = False
    final_answer: str = ""
    trace: list[str] = field(default_factory=list)
    execution_mode: str = "deterministic"
    model_error: str = ""


def _route_request(request: str) -> str:
    normalized = request.lower()
    rules = {
        "inventory_alert": ("库存", "补货", "预警"),
        "sales_report": ("日报", "销售", "订单", "营收"),
        "customer_service": ("客服", "退货", "换货", "售后"),
        "listing": ("listing", "商品文案", "标题", "详情页", "商品描述"),
    }
    for route, keywords in rules.items():
        if any(keyword in normalized for keyword in keywords):
            return route
    return ""


def router_agent(state: WorkflowState) -> None:
    state.route = _route_request(state.request)
    if state.route:
        state.trace.append(f"Router Agent: routed to {state.route}")
    else:
        state.warnings.append("未识别业务类型；当前只支持商品文案、客服话术、销售日报和库存预警。")
        state.trace.append("Router Agent: rejected unsupported request")


def _token_score(query: str, content: str) -> int:
    tokens = [token for token in re.split(r"[^0-9A-Za-z\u4e00-\u9fff]+", query) if len(token) > 1]
    return sum(1 for token in tokens if token.lower() in content.lower())


def knowledge_agent(state: WorkflowState) -> None:
    if not state.route:
        return
    route_labels = {
        "listing": "listing rules",
        "customer_service": "customer service rules",
        "sales_report": "sales report and inventory rules",
        "inventory_alert": "sales report and inventory rules",
    }
    matches: list[dict[str, str]] = []
    for path in KNOWLEDGE_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        score = _token_score(state.request, content)
        if route_labels[state.route] not in content.lower():
            continue
        score += 2
        matches.append({"source": path.name, "excerpt": content.strip(), "score": str(score)})
    matches.sort(key=lambda item: int(item["score"]), reverse=True)
    state.knowledge = matches[:2]
    state.trace.append(f"Knowledge Agent: retrieved {len(state.knowledge)} local policy documents")


def _readonly_connection(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)

    def authorizer(action: int, arg1: str | None, _arg2: str | None, _db: str | None, _trigger: str | None) -> int:
        if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    connection.set_authorizer(authorizer)
    return connection


def data_agent(state: WorkflowState, database_path: Path = DATABASE_PATH) -> None:
    if state.route not in {"listing", "sales_report", "inventory_alert"}:
        state.trace.append("Data Agent: no structured data needed")
        return
    if not database_path.exists():
        create_demo_database(database_path)
    connection = _readonly_connection(database_path)
    try:
        if state.route == "listing":
            row = connection.execute("SELECT sku, name, material, selling_points, price FROM products ORDER BY sku LIMIT 1").fetchone()
            state.data["product"] = dict(zip(("sku", "name", "material", "selling_points", "price"), row))
        elif state.route == "sales_report":
            summary = connection.execute(
                "SELECT order_date, COUNT(*) AS order_count, SUM(quantity) AS units, ROUND(SUM(paid_amount), 2) AS revenue "
                "FROM orders WHERE order_date = '2026-08-30' GROUP BY order_date"
            ).fetchone()
            top_sku = connection.execute(
                "SELECT p.name, SUM(o.quantity) AS units FROM orders o JOIN products p ON p.sku = o.sku "
                "WHERE o.order_date = '2026-08-30' GROUP BY p.name ORDER BY units DESC, p.name LIMIT 1"
            ).fetchone()
            state.data["report"] = {
                "date": summary[0], "order_count": summary[1], "units": summary[2], "revenue": summary[3],
                "top_product": top_sku[0], "top_product_units": top_sku[1],
            }
        elif state.route == "inventory_alert":
            rows = connection.execute(
                "SELECT p.sku, p.name, i.available_units, i.safety_stock, i.safety_stock - i.available_units AS shortage "
                "FROM inventory i JOIN products p ON p.sku = i.sku WHERE i.available_units < i.safety_stock ORDER BY shortage DESC"
            ).fetchall()
            state.data["alerts"] = [
                {"sku": row[0], "name": row[1], "available_units": row[2], "safety_stock": row[3], "shortage": row[4]}
                for row in rows
            ]
    finally:
        connection.close()
    state.trace.append("Data Agent: completed read-only SQLite query on simulated data")


def content_agent(state: WorkflowState, execution_mode: str = "deterministic") -> None:
    if not state.route:
        return
    if state.route == "listing":
        product = state.data["product"]
        state.draft = (
            f"商品标题：{product['name']}｜{product['material']}｜日常通勤收纳\n"
            f"商品描述：{product['selling_points']}。演示售价：{product['price']:.0f} 元。\n"
            "发布前请按实际规格、库存与平台规则复核。"
        )
    elif state.route == "customer_service":
        state.draft = (
            "您好，已收到您的售后咨询。商品如保持未使用且配件齐全，可在签收后 7 天内申请退货；"
            "如存在质量问题，请提供订单号和清晰图片，我们会在 1 个工作日内核实处理。"
        )
    elif state.route == "sales_report":
        report = state.data["report"]
        state.draft = (
            f"{report['date']} 销售日报（模拟数据）：{report['order_count']} 笔订单，"
            f"售出 {report['units']} 件，成交额 {report['revenue']:.2f} 元；"
            f"销量最高商品为 {report['top_product']}，售出 {report['top_product_units']} 件。"
        )
    elif state.route == "inventory_alert":
        alerts = state.data["alerts"]
        lines = ["库存预警（模拟数据）："]
        for alert in alerts:
            lines.append(
                f"- {alert['sku']} {alert['name']}：可售 {alert['available_units']}，安全库存 {alert['safety_stock']}，缺口 {alert['shortage']}。"
            )
        lines.append("建议：先核对在途和近 7 天销量，再决定补货数量。")
        state.draft = "\n".join(lines)
    state.trace.append("Content Agent: generated a draft from approved evidence")
    _apply_optional_model(state, execution_mode)


def review_agent(state: WorkflowState) -> None:
    if not state.draft:
        state.warnings.append("没有可审核的输出。")
        state.trace.append("Review Agent: blocked empty output")
        return
    prohibited = ("保证", "绝对", "全网最低", "疗效")
    found = [term for term in prohibited if term in state.draft]
    if found:
        state.warnings.append(f"输出含未经证实的营销或功效承诺：{', '.join(found)}。")
    if state.route in {"listing", "sales_report", "inventory_alert"} and not state.data:
        state.warnings.append("缺少结构化数据证据。")
    if state.route == "customer_service" and not state.knowledge:
        state.warnings.append("缺少售后规则证据。")
    state.review_passed = not state.warnings
    state.trace.append("Review Agent: passed evidence and claim checks" if state.review_passed else "Review Agent: blocked draft")


def finalizer_agent(state: WorkflowState) -> None:
    if not state.review_passed:
        state.final_answer = "审核未通过：" + "；".join(state.warnings)
        return
    sources = "、".join(item["source"] for item in state.knowledge) or "本地结构化模拟数据"
    state.final_answer = f"{state.draft}\n\n证据来源：{sources}\n边界：本结果基于本地模拟电商数据和示例规则，仅用于工作流演示。"
    state.trace.append("Finalizer Agent: packaged reviewed answer with boundaries")


def _apply_optional_model(state: WorkflowState, execution_mode: str) -> None:
    """Optionally refine a grounded draft with an OpenAI-compatible model.

    The deterministic draft remains the fallback so tests and local demos do not
    depend on a network connection or a paid API key.
    """
    if execution_mode != "auto":
        return

    from .model_client import generate_grounded_draft

    generated, error = generate_grounded_draft(state.request, state.draft, state.knowledge, state.data)
    if error:
        state.execution_mode = "deterministic_fallback"
        state.model_error = error
        state.trace.append("Content Agent: model unavailable; used deterministic fallback")
        return
    state.draft = generated
    state.execution_mode = "openai_compatible"
    state.trace.append("Content Agent: refined draft with optional OpenAI-compatible model")


def _run_sequentially(request: str, database_path: Path, execution_mode: str) -> WorkflowState:
    state = WorkflowState(request=request)
    router_agent(state)
    knowledge_agent(state)
    data_agent(state, database_path)
    content_agent(state, execution_mode)
    review_agent(state)
    finalizer_agent(state)
    return state


def run_workflow(
    request: str,
    database_path: Path = DATABASE_PATH,
    execution_mode: str = "deterministic",
) -> WorkflowState:
    """Run the role workflow through LangGraph when it is installed.

    Nanobot's standalone Skill still works in a minimal Python environment:
    without LangGraph the same nodes run sequentially and expose the fallback in
    the trace. Normal API and Docker installs include LangGraph.
    """
    if execution_mode not in {"deterministic", "auto"}:
        raise ValueError("execution_mode must be 'deterministic' or 'auto'")
    try:
        from .graph import run_langgraph_workflow
    except ImportError:
        state = _run_sequentially(request, database_path, execution_mode)
        state.trace.append("Workflow runtime: LangGraph unavailable; ran the same nodes sequentially")
        return state
    return run_langgraph_workflow(request, database_path, execution_mode)
