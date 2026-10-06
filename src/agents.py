"""The three agents plus quarantine/escalate handlers.

Each agent is a pure function: TradeState -> partial TradeState update.
"""
from __future__ import annotations

from typing import TypedDict

from .rules import RULES


class TradeState(TypedDict, total=False):
    trade: dict
    extracted: dict
    violations: list[dict]
    verdict: str
    report: str
    trace: list[str]


def _note(state: TradeState, step: str) -> list[str]:
    return [*state.get("trace", []), step]


# -- agents -----------------------------------------------------------------
def extractor(state: TradeState) -> dict:
    """Agent 1: normalize the raw trade record into a structured form."""
    raw = state["trade"]
    extracted = {
        "trade_id": raw.get("trade_id"),
        "symbol": raw.get("symbol"),
        "side": raw.get("side"),
        "quantity": raw.get("quantity"),
        "price": raw.get("price"),
        "notional": (raw.get("quantity") or 0) * (raw.get("price") or 0),
        "client_type": raw.get("client_type"),
        "is_recommendation": bool(raw.get("is_recommendation")),
    }
    return {"extracted": extracted, "trace": _note(state, "extract")}


def policy_validator(state: TradeState) -> dict:
    """Agent 2: run the extracted record against every policy rule."""
    rec = state["trade"]
    violations = []
    for rule in RULES:
        message = rule["check"](rec)
        if message:
            violations.append(
                {"rule_id": rule["id"], "severity": rule["severity"],
                 "message": message}
            )
    return {"violations": violations, "trace": _note(state, "validate")}


def reporter(state: TradeState) -> dict:
    """Agent 3: produce the review report and machine-readable verdict."""
    trade_id = state["trade"].get("trade_id", "?")
    violations = state.get("violations", [])
    verdict = state.get("verdict", "CLEARED")
    lines = [f"# Compliance review — {trade_id}", "", f"**Verdict: {verdict}**", ""]
    if violations:
        lines.append("## Findings")
        for v in violations:
            lines.append(f"- [{v['severity'].upper()}] {v['message']}")
    else:
        lines.append("No policy violations found.")
    lines += ["", f"_trace: {' → '.join(state.get('trace', []))}_"]
    return {"report": "\n".join(lines), "trace": _note(state, "report")}


def quarantine(state: TradeState) -> dict:
    return {
        "verdict": "QUARANTINED — manual review required",
        "violations": state.get("violations", []),
        "trace": _note(state, "quarantine"),
    }


def escalate(state: TradeState) -> dict:
    return {
        "verdict": "ESCALATED — critical violation",
        "trace": _note(state, "escalate"),
    }
