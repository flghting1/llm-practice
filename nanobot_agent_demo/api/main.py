"""FastAPI entrypoint that keeps model credentials on the server."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from ecommerce_multi_agent.model_client import model_is_configured
from ecommerce_multi_agent.workflow import run_workflow


load_dotenv()


class WorkflowRequest(BaseModel):
    request: str = Field(min_length=2, max_length=500, description="A supported e-commerce operations request.")
    mode: Literal["deterministic", "auto"] = "auto"


class WorkflowResponse(BaseModel):
    request: str
    route: str
    knowledge: list[dict[str, str]]
    data: dict
    warnings: list[str]
    review_passed: bool
    final_answer: str
    trace: list[str]
    execution_mode: str
    model_error: str


def _cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app = FastAPI(
    title="E-commerce Multi-Agent Demo API",
    version="1.0.0",
    description="Local, simulated-data demo. It does not connect to real stores or ad platforms.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "workflow": "ecommerce-multi-agent",
        "model_configured": model_is_configured(),
        "data_scope": "local_simulated",
    }


@app.post("/api/workflows", response_model=WorkflowResponse)
def execute_workflow(payload: WorkflowRequest) -> WorkflowResponse:
    try:
        state = run_workflow(payload.request.strip(), execution_mode=payload.mode)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    result = asdict(state)
    return WorkflowResponse(**result)
