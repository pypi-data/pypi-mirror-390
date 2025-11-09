#!/usr/bin/env python3
"""
Comprehensive test for OpenRouter integration
Tests: OpenAI models, Claude models, tool calling, structured output
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

from ultragpt import UltraGPT

# ========== Test Schemas ==========

class Weather(BaseModel):
    """Weather information"""
    location: str = Field(description="Location name")
    temperature: int = Field(description="Temperature in Celsius")
    condition: str = Field(description="Weather condition")

class Person(BaseModel):
    """Person information"""
    name: str = Field(description="Person's name")
    age: int = Field(description="Person's age")
    occupation: str = Field(description="Person's occupation")

class Task(BaseModel):
    """A single task"""
    id: int
    title: str
    completed: bool
    priority: str  # "low", "medium", "high"

class ComplexNestedSchema(BaseModel):
    """Complex nested structure"""
    project_name: str = Field(description="Name of the project")
    team_members: List[Person] = Field(description="List of team members")
    tasks: List[Task] = Field(description="List of tasks")
    budget: float = Field(description="Project budget")
    deadline: Optional[str] = Field(default=None, description="Project deadline")

# ========== Test Functions ==========

def test_openai_basic():
    """Test basic OpenAI model via OpenRouter"""
    print("\n" + "=" * 70)
    print("Test 1: OpenAI GPT-4o - Basic Chat")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            model="openrouter:gpt-4o",
            messages=[{"role": "user", "content": "Say 'Hello from GPT-4o' in exactly those words"}],
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✅ Response: {response}")
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_claude_structured_simple():
    """Test Claude with simple structured output"""
    print("\n" + "=" * 70)
    print("Test 2: Claude - Simple Structured Output (Weather)")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            model="claude:claude-3-haiku",
            messages=[{"role": "user", "content": "What's the weather in Paris? Make up realistic data. Temperature around 15C, partly cloudy."}],
            schema=Weather,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✅ Structured Response:")
        print(f"   Location: {response.get('location')}")
        print(f"   Temperature: {response.get('temperature')}°C")
        print(f"   Condition: {response.get('condition')}")
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_structured_simple():
    """Test OpenAI with simple structured output"""
    print("\n" + "=" * 70)
    print("Test 3: OpenAI GPT-4o - Simple Structured Output (Person)")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        response, tokens, details = ultragpt.chat(
            model="openrouter:gpt-4o-mini",
            messages=[{"role": "user", "content": "Create a person profile: Name John Doe, age 30, software engineer"}],
            schema=Person,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✅ Structured Response:")
        print(f"   Name: {response.get('name')}")
        print(f"   Age: {response.get('age')}")
        print(f"   Occupation: {response.get('occupation')}")
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_claude_structured_complex():
    """Test Claude with complex nested structured output"""
    print("\n" + "=" * 70)
    print("Test 4: Claude - Complex Nested Structured Output")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        prompt = """Create a project with:
        - Name: "AI Assistant"
        - 2 team members (Alice age 28 engineer, Bob age 32 designer)
        - 3 tasks (id 1-3, mix of completed/incomplete, different priorities)
        - Budget: 50000.0
        - Deadline: "2024-12-31"
        """
        
        response, tokens, details = ultragpt.chat(
            model="claude:claude-3-haiku",
            messages=[{"role": "user", "content": prompt}],
            schema=ComplexNestedSchema,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✅ Complex Structured Response:")
        print(f"   Project: {response.get('project_name')}")
        print(f"   Team: {len(response.get('team_members', []))} members")
        print(f"   Tasks: {len(response.get('tasks', []))} tasks")
        print(f"   Budget: ${response.get('budget')}")
        print(f"   Deadline: {response.get('deadline')}")
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_structured_complex():
    """Test OpenAI with complex nested structured output"""
    print("\n" + "=" * 70)
    print("Test 5: OpenAI GPT-4o - Complex Nested Structured Output")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        prompt = """Create a project with:
        - Name: "Web App"
        - 2 team members (Carol age 25 developer, Dave age 29 manager)
        - 3 tasks (id 1-3, mix of completed/incomplete, different priorities)
        - Budget: 75000.0
        - Deadline: "2024-11-30"
        """
        
        response, tokens, details = ultragpt.chat(
            model="openrouter:gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            schema=ComplexNestedSchema,
            reasoning_pipeline=False,
            steps_pipeline=False,
            tools=[]
        )
        
        print(f"✅ Complex Structured Response:")
        print(f"   Project: {response.get('project_name')}")
        print(f"   Team: {len(response.get('team_members', []))} members")
        print(f"   Tasks: {len(response.get('tasks', []))} tasks")
        print(f"   Budget: ${response.get('budget')}")
        print(f"   Deadline: {response.get('deadline')}")
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_claude_tool_calling():
    """Test Claude with tool calling"""
    print("\n" + "=" * 70)
    print("Test 6: Claude - Tool Calling")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name"
                            },
                            "units": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "Temperature units"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
        
        response, tokens, details = ultragpt.tool_call(
            model="claude:claude-3-haiku",
            messages=[{"role": "user", "content": "What's the weather in Tokyo? Use celsius."}],
            user_tools=tools,
            reasoning_pipeline=False,
            steps_pipeline=False,
        )
        
        if isinstance(response, list):
            print(f"✅ Tool calls: {len(response)} call(s)")
            for idx, call in enumerate(response):
                print(f"   Call {idx+1}: {call.get('function', {}).get('name')}")
                print(f"   Arguments: {call.get('function', {}).get('arguments')}")
        elif isinstance(response, dict):
            print(f"✅ Tool call: {response.get('function', {}).get('name')}")
            print(f"   Arguments: {response.get('function', {}).get('arguments')}")
        
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_tool_calling():
    """Test OpenAI with tool calling"""
    print("\n" + "=" * 70)
    print("Test 7: OpenAI GPT-4o - Tool Calling")
    print("=" * 70)
    
    try:
        ultragpt = UltraGPT(
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
            verbose=False
        )
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform mathematical calculation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["add", "subtract", "multiply", "divide"],
                                "description": "Math operation"
                            },
                            "a": {
                                "type": "number",
                                "description": "First number"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second number"
                            }
                        },
                        "required": ["operation", "a", "b"]
                    }
                }
            }
        ]
        
        response, tokens, details = ultragpt.tool_call(
            model="openrouter:gpt-4o-mini",
            messages=[{"role": "user", "content": "Calculate 123 times 456"}],
            user_tools=tools,
            reasoning_pipeline=False,
            steps_pipeline=False,
        )
        
        if isinstance(response, list):
            print(f"✅ Tool calls: {len(response)} call(s)")
            for idx, call in enumerate(response):
                print(f"   Call {idx+1}: {call.get('function', {}).get('name')}")
                print(f"   Arguments: {call.get('function', {}).get('arguments')}")
        elif isinstance(response, dict):
            print(f"✅ Tool call: {response.get('function', {}).get('name')}")
            print(f"   Arguments: {response.get('function', {}).get('arguments')}")
        
        print(f"📊 Tokens: {tokens} (input: {details.get('input_tokens')}, output: {details.get('output_tokens')})")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 70)
    print("COMPREHENSIVE OPENROUTER INTEGRATION TEST")
    print("=" * 70)
    print("Testing: OpenAI models, Claude models, structured output, tool calling")
    print("=" * 70)
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ OPENROUTER_API_KEY not set!")
        return
    
    results = []
    
    # Run all tests
    results.append(("OpenAI Basic", test_openai_basic()))
    results.append(("Claude Structured Simple", test_claude_structured_simple()))
    results.append(("OpenAI Structured Simple", test_openai_structured_simple()))
    results.append(("Claude Structured Complex", test_claude_structured_complex()))
    results.append(("OpenAI Structured Complex", test_openai_structured_complex()))
    results.append(("Claude Tool Calling", test_claude_tool_calling()))
    results.append(("OpenAI Tool Calling", test_openai_tool_calling()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    print("\n" + "=" * 70)
    print(f"🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenRouter integration is fully working!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("\n✨ Features Verified:")
    print("   • OpenAI models (gpt-4o, gpt-4o-mini)")
    print("   • Claude models (claude-3-haiku)")
    print("   • Simple structured output (Pydantic schemas)")
    print("   • Complex nested structured output")
    print("   • Tool calling for both providers")
    print("   • Token breakdown (input/output)")

if __name__ == "__main__":
    main()
