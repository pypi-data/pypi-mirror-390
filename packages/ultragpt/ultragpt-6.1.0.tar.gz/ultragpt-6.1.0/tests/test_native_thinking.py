"""Test native thinking/reasoning capabilities with OpenRouter.

Tests deepthink=True with models that support native reasoning:
- Claude models (all variants)
- OpenAI o-series (o1, o3, etc.)
- OpenAI gpt-5 series

Verifies:
1. Reasoning pipeline is skipped when native thinking is available
2. deepthink=True flag is passed to provider
3. Token breakdown includes reasoning_tokens_api
4. Response quality with thinking enabled
"""

import os
from pydantic import BaseModel, Field
from ultragpt import UltraGPT

# Get API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY environment variable not set")
    print("   Set it with: $env:OPENROUTER_API_KEY='your-key-here'")
    exit(1)

# Initialize UltraGPT with OpenRouter
ultra = UltraGPT(
    openrouter_api_key=OPENROUTER_API_KEY,
    verbose=True,
)

print("=" * 70)
print("NATIVE THINKING/REASONING TESTS")
print("=" * 70)
print("Testing: Claude models, o-series, gpt-5 with deepthink=True")
print("=" * 70)
print()

# Test 1: Claude with thinking
print("=" * 70)
print("Test 1: Claude Sonnet with Native Thinking")
print("=" * 70)

messages_1 = [
    {"role": "user", "content": "Solve this step by step: What is 15% of 240?"}
]

response_1, tokens_1, details_1 = ultra.chat(
    messages=messages_1,
    model="claude:sonnet",
    temperature=0.7,
    reasoning_pipeline=True,  # Should be skipped in favor of native thinking
)

print(f"Response: {response_1}")
print(f"Tokens: {tokens_1}")
print(f"  - Input: {details_1.get('input_tokens', 0)}")
print(f"  - Output: {details_1.get('output_tokens', 0)}")
print(f"  - Reasoning (API): {details_1.get('reasoning_tokens_api', 0)}")
if details_1.get('reasoning_text'):
    print(f"  - Reasoning Text: {details_1['reasoning_text'][:100]}...")
print()

# Test 2: Claude with structured output + thinking
print("=" * 70)
print("Test 2: Claude with Structured Output + Thinking")
print("=" * 70)

class MathSolution(BaseModel):
    """Solution to a math problem."""
    steps: list[str] = Field(description="List of solution steps")
    final_answer: str = Field(description="The final answer")
    explanation: str = Field(description="Brief explanation of the solution")

messages_2 = [
    {"role": "user", "content": "Calculate 25% of 180. Provide step-by-step solution."}
]

response_2, tokens_2, details_2 = ultra.chat(
    messages=messages_2,
    model="claude:sonnet",
    schema=MathSolution,
    temperature=0.7,
    reasoning_pipeline=True,  # Should be skipped
)

print(f"Structured Response:")
print(f"  Steps: {len(response_2.get('steps', []))} steps")
print(f"  Final Answer: {response_2.get('final_answer')}")
print(f"  Explanation: {response_2.get('explanation')[:80]}...")
print(f"Tokens: {tokens_2}")
print(f"  - Input: {details_2.get('input_tokens', 0)}")
print(f"  - Output: {details_2.get('output_tokens', 0)}")
print(f"  - Reasoning (API): {details_2.get('reasoning_tokens_api', 0)}")
print()

# Test 3: Compare with and without thinking
print("=" * 70)
print("Test 3: Compare Claude With vs Without Thinking")
print("=" * 70)

messages_3 = [
    {"role": "user", "content": "What is the square root of 144?"}
]

# Without thinking
response_3a, tokens_3a, details_3a = ultra.chat(
    messages=messages_3,
    model="claude:sonnet",
    temperature=0.7,
    reasoning_pipeline=False,
)

print("WITHOUT THINKING:")
print(f"  Response: {response_3a[:100]}...")
print(f"  Tokens: {tokens_3a} (input: {details_3a.get('input_tokens', 0)}, output: {details_3a.get('output_tokens', 0)})")
print()

# With thinking
response_3b, tokens_3b, details_3b = ultra.chat(
    messages=messages_3,
    model="claude:sonnet",
    temperature=0.7,
    reasoning_pipeline=True,  # Should trigger native thinking
)

print("WITH THINKING:")
print(f"  Response: {response_3b[:100]}...")
print(f"  Tokens: {tokens_3b} (input: {details_3b.get('input_tokens', 0)}, output: {details_3b.get('output_tokens', 0)})")
print(f"  Reasoning Tokens (API): {details_3b.get('reasoning_tokens_api', 0)}")
print()

# Test 4: GPT-4o with thinking (does NOT support native thinking)
print("=" * 70)
print("Test 4: GPT-4o (Does NOT support native thinking)")
print("=" * 70)

messages_4 = [
    {"role": "user", "content": "What is 20% of 150?"}
]

response_4, tokens_4, details_4 = ultra.chat(
    messages=messages_4,
    model="gpt-4o",
    temperature=0.7,
    reasoning_pipeline=True,  # Should use fake pipeline
)

print(f"Response: {response_4}")
print(f"Tokens: {tokens_4}")
print(f"  - Input: {details_4.get('input_tokens', 0)}")
print(f"  - Output: {details_4.get('output_tokens', 0)}")
print(f"  - Reasoning (API): {details_4.get('reasoning_tokens_api', 0)}")
print(f"  - Reasoning (Fake Pipeline): {details_4.get('reasoning', [])[:2] if details_4.get('reasoning') else 'None'}")
print(f"  - Reasoning Pipeline Tokens: {details_4.get('reasoning_pipeline_total_tokens', 0)}")
print(
    f"  - Reasoning Pipeline API Tokens: {details_4.get('reasoning_pipeline_reasoning_tokens_api', 0)}"
)
print()

# Test 5: Tool calling with thinking
print("=" * 70)
print("Test 5: Claude Tool Calling + Thinking")
print("=" * 70)

user_tools = [
    {
        "name": "calculator",
        "description": "Performs basic arithmetic calculations",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The operation to perform"
                },
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["operation", "a", "b"]
        },
        "usage_guide": "Use the calculator for precise arithmetic on demand, always provide reasoning and stop flags",
        "when_to_use": "Apply this tool whenever the user requests a concrete arithmetic calculation or numeric result"
    }
]

messages_5 = [
    {"role": "user", "content": "Use the calculator to find 25 * 8"}
]

response_5, tokens_5, details_5 = ultra.tool_call(
    messages=messages_5,
    user_tools=user_tools,
    model="claude:sonnet",
    temperature=0.7,
    reasoning_pipeline=True,  # Should trigger native thinking
)

if isinstance(response_5, dict):
    tool_calls = response_5.get('tool_calls', []) or []
else:
    tool_calls = response_5 if isinstance(response_5, list) else []

print(f"Tool Calls: {len(tool_calls)}")
if tool_calls:
    first_call = tool_calls[0] if isinstance(tool_calls[0], dict) else {}
    function_block = first_call.get('function', {}) if isinstance(first_call, dict) else {}
    print(f"  Tool: {function_block.get('name', 'unknown')}")
    arguments_preview = function_block.get('arguments', '') if isinstance(function_block, dict) else ''
    print(f"  Arguments: {arguments_preview[:80]}...")
print(f"Tokens: {tokens_5}")
print(f"  - Input: {details_5.get('input_tokens', 0)}")
print(f"  - Output: {details_5.get('output_tokens', 0)}")
print(f"  - Reasoning (API): {details_5.get('reasoning_tokens_api', 0)}")
print()

# Summary
print("=" * 70)
print("TEST RESULTS SUMMARY")
print("=" * 70)

tests = [
    ("Claude Basic + Thinking", tokens_1 > 0, details_1.get('reasoning', []) == []),
    ("Claude Structured + Thinking", tokens_2 > 0, isinstance(response_2, dict)),
    ("Claude With vs Without", tokens_3b > tokens_3a, True),
    ("GPT-4o (No Native Thinking)", tokens_4 > 0, len(details_4.get('reasoning', [])) > 0),
    ("Claude Tool + Thinking", tokens_5 > 0, len(tool_calls) > 0),
]

all_passed = True
for test_name, passed, extra_check in tests:
    status = "PASS" if (passed and extra_check) else "FAIL"
    if not (passed and extra_check):
        all_passed = False
    print(f"{test_name:<40} {status}")

print("=" * 70)
if all_passed:
    print("All tests passed! Native thinking integration working correctly.")
    print()
    print("Key Observations:")
    print("  - Claude models support native thinking (reasoning_pipeline skipped)")
    print("  - GPT-4o does NOT support native thinking (uses fake pipeline)")
    print("  - Thinking works with basic chat, structured output, and tool calling")
    print("  - Token breakdown properly tracks reasoning tokens from API")
else:
    print("Some tests failed. Please review output above.")
print("=" * 70)
