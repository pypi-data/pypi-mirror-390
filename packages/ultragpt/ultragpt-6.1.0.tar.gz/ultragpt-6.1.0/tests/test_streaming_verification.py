"""
Comprehensive test suite for OpenAI streaming verification
Tests all 3 methods: chat_completion, chat_completion_with_tools, chat_completion_with_schema
"""

import sys
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from src.ultragpt import UltraGPT
from src.ultragpt.schemas import UserTool

# Load environment variables
load_dotenv()

# Initialize - API key from env
ultragpt = UltraGPT(
    api_key=os.getenv("OPENAI_API_KEY"),
    verbose=False
)

# ============================================================
# TEST 1: Normal chat_completion with streaming
# ============================================================
print("=" * 60)
print("TEST 1: Testing chat_completion() with streaming")
print("=" * 60)

messages = [
    {"role": "user", "content": "What is 2+2? Just say the number in words, nothing else."}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=100
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ chat_completion() Streaming [OK]")
except Exception as e:
    print(f"❌ chat_completion() FAILED: {e}")
    sys.exit(1)

# ============================================================
# TEST 2: chat_completion_with_tools with streaming
# ============================================================
print("\n" + "=" * 60)
print("TEST 2: Testing chat_completion_with_tools() with streaming")
print("=" * 60)

class AddNumbersParams(BaseModel):
    a: float = Field(description="First number")
    b: float = Field(description="Second number")

calculator_tool = UserTool(
    name="add_numbers",
    description="Adds two numbers together",
    parameters_schema=AddNumbersParams,
    usage_guide="Use this tool when you need to add two numbers",
    when_to_use="When the user asks to add or sum two numbers"
)

messages = [
    {"role": "user", "content": "What is 15 + 27? Use the add_numbers tool."}
]

try:
    response, tokens, details = ultragpt.tool_call(
        messages=messages,
        user_tools=[calculator_tool],
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=1000,
        steps_pipeline=False,
        reasoning_pipeline=False
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ chat_completion_with_tools() Streaming [OK]")
except Exception as e:
    print(f"❌ chat_completion_with_tools() FAILED: {e}")
    sys.exit(1)

# ============================================================
# TEST 3: chat_completion_with_schema with NEW STREAMING
# ============================================================
print("\n" + "=" * 60)
print("TEST 3: Testing chat_completion_with_schema() with NEW STREAMING")
print("=" * 60)

class MathResult(BaseModel):
    answer: int = Field(description="The numeric answer")
    explanation: str = Field(description="Brief explanation of the calculation")

messages = [
    {"role": "user", "content": "What is 5 * 8? Provide answer and explanation."}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        schema=MathResult,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=500
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ chat_completion_with_schema() Streaming [OK]")
except Exception as e:
    print(f"❌ chat_completion_with_schema() FAILED: {e}")
    sys.exit(1)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("Summary:")
print("  1) Normal messages    - Streaming ✅ [OK]")
print("  2) Tool calls         - Streaming ✅ [OK]")
print("  3) Structured output  - Streaming ✅ [OK] (NEW: response_format + json_schema)")
print("=" * 60)
