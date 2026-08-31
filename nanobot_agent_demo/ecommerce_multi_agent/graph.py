"""LangGraph orchestration for the existing deterministic e-commerce roles."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .workflow import (
    WorkflowState,
    content_agent,
    data_agent,
    finalizer_agent,
    knowledge_agent,
    review_agent,
    router_agent,
)


class GraphState(TypedDict):
    request: str
    route: str
    knowledge: list[dict[str, str]]
    data: dict
    draft: str
    warnings: list[str]
    review_passed: bool
    final_answer: str
    trace: list[str]
    execution_mode: str
    model_error: str


def _to_workflow_state(values: GraphState) -> WorkflowState:
    return WorkflowState(**values)


def _as_update(state: WorkflowState) -> GraphState:
    return asdict(state)  # type: ignore[return-value]


def run_langgraph_workflow(request: str, database_path: Path, execution_mode: str) -> WorkflowState:
    """Execute the same six roles as a visible LangGraph state machine."""
    def router(values: GraphState) -> GraphState:
        state = _to_workflow_state(values)
        router_agent(state)
        return _as_update(state)

    def knowledge(values: GraphState) -> GraphState:
        state = _to_workflow_state(values)
        knowledge_agent(state)
        return _as_update(state)

    def data(values: GraphState) -> GraphState:
        state = _to_workflow_state(values)
        data_agent(state, database_path)
        return _as_update(state)

    def content(values: GraphState) -> GraphState:
        state = _to_workflow_state(values)
        content_agent(state, execution_mode)
        return _as_update(state)

    def review(values: GraphState) -> GraphState:
        state = _to_workflow_state(values)
        review_agent(state)
        return _as_update(state)

    def finalizer(values: GraphState) -> GraphState:
        state = _to_workflow_state(values)
        finalizer_agent(state)
        state.trace.append("Workflow runtime: completed through LangGraph")
        return _as_update(state)

    def route_after_router(values: GraphState) -> Literal["knowledge", "finalizer"]:
        return "knowledge" if values["route"] else "finalizer"

    graph = StateGraph(GraphState)
    graph.add_node("router", router)
    graph.add_node("knowledge", knowledge)
    graph.add_node("data", data)
    graph.add_node("content", content)
    graph.add_node("review", review)
    graph.add_node("finalizer", finalizer)
    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", route_after_router, {"knowledge": "knowledge", "finalizer": "finalizer"})
    graph.add_edge("knowledge", "data")
    graph.add_edge("data", "content")
    graph.add_edge("content", "review")
    graph.add_edge("review", "finalizer")
    graph.add_edge("finalizer", END)

    initial = asdict(WorkflowState(request=request))
    initial["execution_mode"] = "deterministic" if execution_mode == "deterministic" else "model_requested"
    result = graph.compile().invoke(initial)
    return WorkflowState(**result)
