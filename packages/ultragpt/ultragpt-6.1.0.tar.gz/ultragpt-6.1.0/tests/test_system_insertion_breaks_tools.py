import sys, json
from pprint import pprint

# Add UltraGPT src to path
sys.path.append(r"e:\Python and AI\_MyLibraries\UltraGPT\src")

from ultragpt.messaging.token_manager import ensure_langchain_messages
from ultragpt.messaging.history_utils import remove_orphaned_tool_results_lc, drop_unresolved_tool_calls_lc, validate_tool_call_pairing_lc
from ultragpt.messaging.message_ops import integrate_tool_call_prompt

# Test case: tool call followed by tool result, then system insertion breaks ordering
messages = [
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
                    "arguments": json.dumps({"foo": "bar"}),
                },
            }
        ],
    },
    {
        "role": "tool",
        "tool_call_id": "call_2kDEgsDYjjpdbacd6cRsWFMI",
        "name": "import_to_sequence",
        "content": json.dumps({"success": True}),
    },
]

print("BEFORE system message insertion:")
lc_before = ensure_langchain_messages(messages)
for i, m in enumerate(lc_before):
    print(f"{i}: {type(m).__name__} - tool_calls: {getattr(m, 'tool_calls', None)} - tool_call_id: {getattr(m, 'tool_call_id', None)}")

# Now apply system message insertion (this is what happens in UltraGPT)
tool_prompt = "You are a helpful assistant with access to tools."
lc_after_system = integrate_tool_call_prompt(lc_before, tool_prompt)

print("\nAFTER system message insertion:")
for i, m in enumerate(lc_after_system):
    print(f"{i}: {type(m).__name__} - tool_calls: {getattr(m, 'tool_calls', None)} - tool_call_id: {getattr(m, 'tool_call_id', None)}")

print("\nValidation after system insertion:")
diag = validate_tool_call_pairing_lc(lc_after_system)
pprint(diag)

print("\n" + "="*60)
print("PROBLEM IDENTIFIED:")
print("The system message gets inserted as SECOND-TO-LAST, which means:")
print("- Assistant tool_call is at position 1")
print("- System message gets inserted at position 2 (second-to-last)")  
print("- Tool result gets pushed to position 3 (last)")
print("- OpenAI sees: [user, assistant_with_tool_calls, system, tool_result]")
print("- OpenAI expects tool_result to IMMEDIATELY follow assistant_with_tool_calls")
print("- The system message breaks this expectation -> 400 error")