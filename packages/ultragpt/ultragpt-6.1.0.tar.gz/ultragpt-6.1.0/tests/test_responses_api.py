import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.ultragpt.providers import OpenAIProvider

load_dotenv()

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def openai_provider() -> OpenAIProvider:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    return OpenAIProvider(api_key=api_key)


def _calculator_result(arguments: str) -> Dict[str, Any]:
    payload = json.loads(arguments)
    op = payload.get("operation")
    a = payload.get("a")
    b = payload.get("b")
    if op == "add":
        value = a + b
        explanation = f"added {a} and {b}"
    elif op == "subtract":
        value = a - b
        explanation = f"subtracted {b} from {a}"
    else:
        raise ValueError(f"Unsupported operation: {op}")
    return {"result": value, "explanation": explanation}


class TripPlan(BaseModel):
    destination: str
    budget_usd: float = Field(..., ge=0)
    highlights: str


@pytest.fixture(scope="module")
def calculator_tool() -> Dict[str, Any]:
    return {
        "name": "basic_calculator",
        "type": "function",
        "description": "Perform simple arithmetic on two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract"],
                },
            },
            "required": ["a", "b", "operation"],
            "additionalProperties": False,
        },
    }


def test_responses_basic_chat(openai_provider: OpenAIProvider):
    content, tokens = openai_provider.chat_completion(
        messages=[
            {"role": "system", "content": "Answer in one short sentence."},
            {"role": "user", "content": "Give me a fun fact about dolphins."},
        ],
        model="gpt-4.1-mini",
        temperature=0.4,
        max_tokens=200,
    )
    assert isinstance(content, str)
    assert len(content) > 0
    assert isinstance(tokens, int)


def test_responses_structured_output(openai_provider: OpenAIProvider):
    content, tokens = openai_provider.chat_completion_with_schema(
        messages=[
            {
                "role": "user",
                "content": "Plan a 2-day budget trip to Kyoto with highlights and total budget.",
            }
        ],
        schema=TripPlan,
        model="gpt-4.1-mini",
        temperature=0.2,
        max_tokens=300,
    )
    assert isinstance(content, dict)
    assert "destination" in content and "budget_usd" in content
    assert isinstance(tokens, int)


def test_responses_tool_call_required(openai_provider: OpenAIProvider, calculator_tool: Dict[str, Any]):
    message_dict, tokens = openai_provider.chat_completion_with_tools(
        messages=[
            {
                "role": "system",
                "content": "Always use the provided tool to compute calculations before answering.",
            },
            {
                "role": "user",
                "content": "Use the calculator tool to add 19 and 23. Fill the JSON with operation 'add' and the numbers before replying.",
            },
        ],
        tools=[calculator_tool],
        model="gpt-4.1-mini",
        temperature=0.1,
        max_tokens=200,
        parallel_tool_calls=False,
    )
    assert isinstance(tokens, int)
    assert "tool_calls" in message_dict
    assert len(message_dict["tool_calls"]) >= 1


def test_responses_parallel_tool_calls(openai_provider: OpenAIProvider, calculator_tool: Dict[str, Any]):
    message_dict, _ = openai_provider.chat_completion_with_tools(
        messages=[
            {
                "role": "system",
                "content": "Use the calculator tool for every arithmetic operation.",
            },
            {
                "role": "user",
                "content": "Use the calculator tool to compute 10 + 5 and 18 - 7. Provide JSON arguments for each call before replying.",
            },
        ],
        tools=[calculator_tool],
        model="gpt-4.1-mini",
        temperature=0.0,
        max_tokens=200,
        parallel_tool_calls=True,
    )
    assert "tool_calls" in message_dict
    assert len(message_dict["tool_calls"]) >= 1


def test_responses_tool_call_follow_up(openai_provider: OpenAIProvider, calculator_tool: Dict[str, Any]):
    initial_messages = [
        {
            "role": "system",
            "content": "Use the tool to compute before giving the final answer.",
        },
        {
            "role": "user",
            "content": "Call the calculator tool with operation 'subtract', a=42, and b=17. After the tool responds, explain the steps.",
        },
    ]

    first_response, _ = openai_provider.chat_completion_with_tools(
        messages=initial_messages,
        tools=[calculator_tool],
        model="gpt-4.1-mini",
        temperature=0.0,
        max_tokens=200,
        parallel_tool_calls=False,
    )

    # Validate tool call structure
    assert "tool_calls" in first_response
    tool_call = first_response.get("tool_calls", [])[0]
    tool_output = _calculator_result(tool_call["function"]["arguments"])

    # Test full round-trip with tool result
    follow_up_messages = initial_messages + [
        {
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "content": json.dumps(tool_output),
        }
    ]

    final_response, tokens = openai_provider.chat_completion(
        messages=follow_up_messages,
        model="gpt-4.1-mini",
        temperature=0.3,
        max_tokens=200,
    )

    assert isinstance(tokens, int)
    assert isinstance(final_response, str)
    assert len(final_response) > 0


def test_responses_structured_output_with_history(openai_provider: OpenAIProvider):
    prior_reply, _ = openai_provider.chat_completion(
        messages=[
            {"role": "system", "content": "You are a concise travel assistant."},
            {"role": "user", "content": "Share one short packing tip for a city day trip."},
        ],
        model="gpt-4.1-mini",
        temperature=0.3,
        max_tokens=120,
    )

    messages = [
        {"role": "system", "content": "You are a concise travel assistant."},
        {"role": "user", "content": "Thanks for the packing advice."},
        {"role": "assistant", "content": prior_reply},
        {
            "role": "user",
            "content": "Plan a one-day budget trip to Osaka including highlights and total budget.",
        },
    ]

    content, tokens = openai_provider.chat_completion_with_schema(
        messages=messages,
        schema=TripPlan,
        model="gpt-4.1-mini",
        temperature=0.2,
        max_tokens=300,
    )

    assert isinstance(content, dict)
    assert content.get("destination")
    assert "budget_usd" in content
    assert isinstance(tokens, int)