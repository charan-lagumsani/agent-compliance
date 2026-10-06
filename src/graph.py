"""LangGraph workflow with validation gates between agents."""
from __future__ import annotations

from langgraph.graph import END, StateGraph

from .agents import TradeState, escalate, extractor, policy_validator, quarantine, reporter


def schema_gate(state: TradeState) -> str:
    """Gate 1: records failing schema validation never reach the policy engine."""
    from .rules import rule_schema

    if rule_schema(state["trade"]):
        return "quarantine"
    return "validate"


def risk_gate(state: TradeState) -> str:
    """Gate 2: critical violations escalate instead of getting a clean report."""
    if any(v["severity"] == "critical" for v in state.get("violations", [])):
        return "escalate"
    return "report"


def build_workflow():
    graph = StateGraph(TradeState)
    graph.add_node("extract", extractor)
    graph.add_node("validate", policy_validator)
    graph.add_node("quarantine", quarantine)
    graph.add_node("escalate", escalate)
    graph.add_node("report", reporter)

    graph.set_entry_point("extract")
    graph.add_conditional_edges("extract", schema_gate,
                               {"quarantine": "quarantine", "validate": "validate"})
    graph.add_edge("quarantine", "report")
    graph.add_conditional_edges("validate", risk_gate,
                               {"escalate": "escalate", "report": "report"})
    graph.add_edge("escalate", "report")
    graph.add_edge("report", END)
    return graph.compile()


def review_trade(trade: dict) -> dict:
    app = build_workflow()
    return app.invoke({"trade": trade, "trace": []})
