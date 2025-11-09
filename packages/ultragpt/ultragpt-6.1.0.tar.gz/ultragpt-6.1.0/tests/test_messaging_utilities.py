#!/usr/bin/env python3
"""Manual verification for LangChain messaging utilities.

This script focuses on the post-refactor helpers that operate purely on
LangChain ``BaseMessage`` objects. It simulates user style chat histories,
converts them with ``ensure_langchain_messages``, and exercises the cleanup and
validation helpers so we can confirm their behaviour without relying on the old
Responses API specific plumbing.
"""

from __future__ import annotations

from pprint import pprint
from typing import List

from langchain_core.messages import BaseMessage, ToolMessage

from ultragpt.messaging import (
    concat_messages_safe_lc,
    ensure_langchain_messages,
    filter_messages_safe_lc,
    remove_orphaned_tool_results_lc,
    validate_tool_call_pairing_lc,
)


def to_serializable(messages: List[BaseMessage]) -> List[dict]:
    """Convert LangChain messages to a printable structure for assertions."""

    serialized: List[dict] = []
    for message in messages:
        entry: dict = {
            "type": message.type,
            "content": getattr(message, "content", None),
        }
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            entry["tool_calls"] = tool_calls
        if isinstance(message, ToolMessage):
            entry["tool_call_id"] = message.tool_call_id
        serialized.append(entry)
    return serialized


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def run_orphan_cleanup_demo() -> None:
    print_header("Scenario 1: Orphaned tool results are removed cleanly")

    raw_messages = [
        {"role": "system", "content": "You are an analyst."},
        {"role": "user", "content": "Summarise yesterday's metrics."},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_keep",
                    "type": "function",
                    "function": {"name": "summarise_metrics", "arguments": "{}"},
                }
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_keep",
            "content": "Net revenue grew 12%.",
        },
        {
            "role": "tool",
            "tool_call_id": "call_orphan",
            "content": "Legacy response that should be dropped.",
        },
        {"role": "assistant", "content": "Here is the updated summary."},
    ]

    lc_messages = ensure_langchain_messages(raw_messages)
    print("Original sequence (with orphan):")
    pprint(to_serializable(lc_messages))

    diagnostics_before = validate_tool_call_pairing_lc(lc_messages)
    print("\nValidation before cleanup:")
    pprint(diagnostics_before)

    cleaned = remove_orphaned_tool_results_lc(lc_messages, verbose=True)
    print("\nCleaned sequence (orphan removed, order preserved):")
    pprint(to_serializable(cleaned))

    diagnostics_after = validate_tool_call_pairing_lc(cleaned)
    print("\nValidation after cleanup:")
    pprint(diagnostics_after)

    assert diagnostics_after["valid"], "Cleanup should fix pairing"
    assert len(cleaned) == len(lc_messages) - 1, "Orphan should be removed"
    print("\n✅ PASS: Orphan cleanup works correctly")


def run_missing_result_detection_demo() -> None:
    print_header("Scenario 2: Missing tool results are detected")

    raw_messages = [
        {"role": "user", "content": "Fetch the product catalog and pricing."},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_catalog",
                    "type": "function",
                    "function": {"name": "fetch_catalog", "arguments": "{}"},
                },
                {
                    "id": "call_pricing",
                    "type": "function",
                    "function": {"name": "fetch_pricing", "arguments": "{}"},
                },
            ],
        },
        {
            "role": "tool",
            "tool_call_id": "call_catalog",
            "content": "Catalog synced.",
        },
        {"role": "assistant", "content": "Catalog loaded. Waiting on pricing."},
    ]

    lc_messages = ensure_langchain_messages(raw_messages)
    diagnostics = validate_tool_call_pairing_lc(lc_messages)

    print("Validation results (pricing result should be missing):")
    pprint(diagnostics)

    assert not diagnostics["valid"], "Should detect missing result"
    assert "call_pricing" in diagnostics["missing_tool_results"], "Pricing call missing"
    print("\n✅ PASS: Missing result detection works correctly")


def run_concat_and_filter_demo() -> None:
    print_header("Scenario 3: concat and filter helpers keep histories tidy")

    system_and_user = ensure_langchain_messages(
        [
            {"role": "system", "content": "You are a researcher."},
            {"role": "user", "content": "Analyse the attached document."},
        ]
    )

    assistant_batch = ensure_langchain_messages(
        [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_analysis",
                        "type": "function",
                        "function": {"name": "analyze_document", "arguments": "{}"},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_analysis",
                "content": "Document processed.",
            },
            {
                "role": "assistant",
                "content": "Highlights extracted successfully.",
            },
        ]
    )

    merged = concat_messages_safe_lc(system_and_user, assistant_batch)
    print("Merged sequence (no orphaned results expected):")
    pprint(to_serializable(merged))

    validation_merged = validate_tool_call_pairing_lc(merged)
    assert validation_merged["valid"], "Merged sequence should be valid"

    only_user_and_tool = filter_messages_safe_lc(
        merged,
        lambda message: message.type in {"human", "tool"},
        verbose=True,
    )
    print("\nFiltered sequence (only user + tool messages retained):")
    pprint(to_serializable(only_user_and_tool))

    validation = validate_tool_call_pairing_lc(only_user_and_tool)
    print("\nValidation of filtered result:")
    pprint(validation)

    # filter_messages_safe_lc automatically cleans orphaned results, so validation should pass
    assert validation["valid"], "Filter should auto-cleanup orphaned results"
    # The tool message should have been removed along with the AI messages
    assert not any(msg.type == "tool" for msg in only_user_and_tool), "Orphaned tool results should be removed"
    print("\n✅ PASS: Concat and filter helpers work correctly (auto-cleanup confirmed)")


def main() -> None:
    print("UltraGPT Messaging Utilities - LangChain verification suite")
    print("=" * 80)
    
    try:
        run_orphan_cleanup_demo()
        run_missing_result_detection_demo()
        run_concat_and_filter_demo()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
