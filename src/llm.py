"""LLM seam — where a real model plugs in.

The agents in this repo are deterministic and rule-based so everything runs
offline. To use a real LLM (e.g. for parsing free-text rationales), implement
``call_llm`` below — for example with langchain_openai.ChatOpenAI — and wire
it into the extractor/reporter in agents.py. Nothing else changes.
"""
from __future__ import annotations


def call_llm(prompt: str) -> str:
    raise NotImplementedError(
        "Plug in a real LLM here (e.g. langchain_openai.ChatOpenAI). "
        "The demo runs without it by design."
    )
