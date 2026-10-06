"""Run the compliance workflow over the sample trades and print results."""
from __future__ import annotations

import json
from pathlib import Path

from src.graph import review_trade


def main() -> None:
    trades = json.loads(Path("data/trades.json").read_text())
    for trade in trades:
        result = review_trade(trade)
        print(f"TRADE {trade['trade_id']} — verdict: {result.get('verdict', 'CLEARED')}")
        print(f"  trace: {' → '.join(result['trace'])}")
        for v in result.get("violations", []):
            print(f"  [{v['severity'].upper():8}] {v['message']}")
        print()


if __name__ == "__main__":
    main()
