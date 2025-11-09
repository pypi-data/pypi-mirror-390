import sys, json
from pprint import pprint

# Add UltraGPT src to path
sys.path.append(r"e:\Python and AI\_MyLibraries\UltraGPT\src")

from ultragpt.providers.providers import ProviderManager
from ultragpt.messaging.token_manager import ensure_langchain_messages
from ultragpt.messaging.history_utils import remove_orphaned_tool_results_lc, drop_unresolved_tool_calls_lc, validate_tool_call_pairing_lc

# Sample messages reflecting the user's log
messages = [
    {"role": "user", "content": "Context notice: 1 media item(s) available in project library. Preloaded 1 item(s) for immediate reference; use media query tools for more."},
    {"role": "user", "content": "make this video shorter under 60sec"},
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_2kDEgsDYjjpdbacd6cRsWFMI",
                "type": "function",
                "function": {
                    "name": "import_to_sequence",
                    "arguments": json.dumps({
                        "path": "userdata/5b74c7f415e04dfdb7d0ec60ba801e35.mp4",
                        "sequence_id": "1d9affbb-db82-4178-88a6-b7838f6026b2",
                        "notes": "Importing for timeline editing. User wants final cut under 60s.",
                        "markers": [],
                        "reasoning": "To make the video shorter, import it first.",
                        "stop_after_tool_call": False
                    }),
                },
            }
        ],
    },
    {
        "role": "tool",
        "tool_call_id": "call_2kDEgsDYjjpdbacd6cRsWFMI",
        "name": "import_to_sequence",
        "content": json.dumps({
            "success": True,
            "asset_id": "asset-782c2024",
            "sequence_id": "1d9affbb-db82-4178-88a6-b7838f6026b2"
        }),
    },
]

print("Raw messages:")
pprint(messages)

lc = ensure_langchain_messages(messages)
print("\nLangChain messages:")
for i, m in enumerate(lc):
    print(i, type(m).__name__, getattr(m, 'tool_calls', None), getattr(m, 'tool_call_id', None))

print("\nvalidate_tool_call_pairing_lc:")
diag = validate_tool_call_pairing_lc(lc)
pprint(diag)

cleaned = remove_orphaned_tool_results_lc(lc, verbose=True)
cleaned = drop_unresolved_tool_calls_lc(cleaned, verbose=True)
print("\nAfter sanitizers:")
for i, m in enumerate(cleaned):
    print(i, type(m).__name__, getattr(m, 'tool_calls', None), getattr(m, 'tool_call_id', None))

# Run through ProviderManager._prepare_messages to confirm it preserves pairs when truncation is OFF
mgr = ProviderManager(token_limiter=None, default_input_truncation="OFF", verbose=True)
prepped = mgr._prepare_messages("openai", "gpt-4.1", messages, input_truncation="OFF", keep_newest=True)
print("\nProviderManager._prepare_messages (OFF truncation):")
for i, m in enumerate(prepped):
    print(i, type(m).__name__, getattr(m, 'tool_calls', None), getattr(m, 'tool_call_id', None))
