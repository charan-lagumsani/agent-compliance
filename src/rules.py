"""Compliance policy rules — data, not code.

Add a rule by appending a dict. Each rule:
  id        unique rule identifier
  severity  "info" | "warning" | "critical"
  check     function(record: dict) -> str | None  (None = pass, else message)
"""
from __future__ import annotations

SUPERVISOR_THRESHOLD = 1_000_000  # notional value requiring pre-approval
REQUIRED_FIELDS = {"trade_id", "symbol", "side", "quantity", "price"}


def _notional(rec: dict) -> float:
    return float(rec.get("quantity", 0)) * float(rec.get("price", 0))


def rule_supervisor_approval(rec: dict) -> str | None:
    if _notional(rec) > SUPERVISOR_THRESHOLD and not rec.get("supervisor_approved"):
        return (
            f"Order value ${_notional(rec):,.0f} exceeds "
            f"${SUPERVISOR_THRESHOLD:,.0f} supervisor pre-approval threshold"
        )
    return None


def rule_trade_reporting(rec: dict) -> str | None:
    if rec.get("reported_within_10s") is False:
        return "Trade not reported within 10 seconds (trade-reporting rule)"
    return None


def rule_retail_rationale(rec: dict) -> str | None:
    if rec.get("client_type") == "retail" and rec.get("is_recommendation"):
        if not rec.get("recommendation_rationale"):
            return (
                "Recommendation rationale missing for retail client "
                "(Reg BI Care Obligation)"
            )
    return None


def rule_schema(rec: dict) -> str | None:
    missing = REQUIRED_FIELDS - set(rec.keys())
    if missing:
        return f"Missing required fields: {sorted(missing)}"
    return None


RULES = [
    {"id": "schema", "severity": "critical", "check": rule_schema},
    {"id": "supervisor-approval", "severity": "critical",
     "check": rule_supervisor_approval},
    {"id": "trade-reporting", "severity": "warning", "check": rule_trade_reporting},
    {"id": "retail-rationale", "severity": "warning", "check": rule_retail_rationale},
]
