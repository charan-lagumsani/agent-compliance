# agent-compliance — Multi-Agent Trade Compliance Workflow

A **LangGraph** multi-agent system that automates trade compliance review the
way surveillance teams do it: an **extractor** agent pulls structured fields
from raw trade records, a **policy validator** agent checks them against
written rules (Reg BI / trade-reporting style), and a **reporter** agent
produces the review outcome. **Validation gates** between agents quarantine
bad records and escalate critical violations instead of letting them flow
through silently.

## Architecture

```
trade record
    │
    ▼
┌───────────┐   schema gate    ┌────────────┐
│ extractor │ ───────────────► │ quarantine │──► report (manual review)
└───────────┘  missing fields └────────────┘
    │ valid
    ▼
┌───────────┐   risk gate     ┌────────────┐
│ validator │ ───────────────► │  escalate  │──► report (escalated)
└───────────┘  critical hits └────────────┘
    │ clean / warnings
    ▼
┌───────────┐
│ reporter  │──► markdown review report + machine-readable verdict
└───────────┘
```

## Quickstart

```bash
pip install -r requirements.txt
python demo.py
```

Sample output:

```
TRADE T-1003 — verdict: ESCALATED
  trace: extract → validate → escalate → report
  violations:
    [CRITICAL] Order value $2.4M exceeds $1M supervisor pre-approval threshold
    [WARNING]  Recommendation rationale missing for retail client (Reg BI Care)
```

## How it works

- **Agents** (`src/agents.py`) are pure functions over a shared `TradeState`
  (TypedDict): `extractor`, `policy_validator`, `reporter`, plus the
  `quarantine` and `escalate` handlers.
- **Gates** (`src/graph.py`) are conditional edges: records failing schema
  validation never reach the policy engine; critical violations never get a
  clean report. Every transition is appended to `state["trace"]` for audit.
- **Rules** (`src/rules.py`) are data, not code — add a rule by appending to
  `RULES`. Each rule has a severity (`info` / `warning` / `critical`).
- **LLM swap-in** — agents are deterministic and rule-based so the demo runs
  offline. `src/llm.py` shows the exact seam: implement `call_llm(prompt)`
  (e.g. via `langchain_openai`) and the extractor/reporter can use it for
  free-text rationale parsing.

## Sample data

`data/trades.json` holds 6 synthetic trade records covering the happy path,
a schema failure, a critical threshold breach, and a retail-recommendation
case. All data is fictional.

## License

MIT — see [LICENSE](LICENSE).
