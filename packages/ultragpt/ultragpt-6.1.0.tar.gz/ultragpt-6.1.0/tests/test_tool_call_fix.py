"""
Test script to verify UltraGPT OpenAI Responses API tool call fix
This tests that output_text is not used as content when tool calls are present
"""

import sys
import os

# Add UltraGPT to path
ultragpt_path = r"e:\Python and AI\_MyLibraries\UltraGPT\src"
if ultragpt_path not in sys.path:
    sys.path.insert(0, ultragpt_path)

from ultragpt import UltraGPT
import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using system environment variables")

# Initialize UltraGPT with OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found in .env file or environment variables!")
    print("Please create a .env file in the UltraGPT directory with: OPENAI_API_KEY=your_key_here")
    exit(1)

ultragpt = UltraGPT(
    api_key=api_key,
    verbose=True
)

# Define a simple test tool
test_tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        },
        "usage_guide": "Use this to get weather information",
        "when_to_use": "When user asks about weather"
    }
]

print("=" * 80)
print("TEST 1: Tool call response (should NOT have output_text as content)")
print("=" * 80)

messages1 = [
    {"role": "user", "content": "What's the weather in New York?"}
]

try:
    response1, tokens1, details1 = ultragpt.tool_call(
        messages=messages1,
        user_tools=test_tools,
        model="gpt-4o",
        allow_multiple=False
    )
    
    print(f"\nResponse type: {type(response1)}")
    print(f"Response: {response1}")
    
    # Verify response structure
    if isinstance(response1, dict):
        if "id" in response1 and "function" in response1:
            print("✅ PASS: Response is a tool call object")
            print(f"   - Tool: {response1['function']['name']}")
            print(f"   - Arguments: {response1['function']['arguments']}")
            
            # Check that content is NOT present or is None
            if "content" not in response1:
                print("✅ PASS: No 'content' field in response (expected)")
            elif response1.get("content") is None:
                print("✅ PASS: 'content' field is None (expected)")
            else:
                print(f"❌ FAIL: 'content' field has value: {response1['content']}")
                print("   This might be output_text contamination!")
        elif "content" in response1 and len(response1) == 1:
            print("⚠️  Response is a content-only dict (no tool calls)")
            print(f"   Content: {response1['content'][:100]}...")
        else:
            print(f"❌ FAIL: Unknown response structure: {list(response1.keys())}")
    elif isinstance(response1, list):
        print(f"✅ PASS: Response is a list of tool calls (length: {len(response1)})")
        for idx, tc in enumerate(response1):
            print(f"   Tool {idx+1}: {tc['function']['name']}")
    else:
        print(f"❌ FAIL: Unexpected response type: {type(response1)}")
    
    print(f"\nTokens used: {tokens1}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST 2: Regular text response (should have content)")
print("=" * 80)

messages2 = [
    {"role": "user", "content": "Hello, how are you?"}
]

try:
    # For regular chat without tool calls, use chat method
    response2, tokens2, details2 = ultragpt.chat(
        messages=messages2,
        model="gpt-4o"
    )
    
    print(f"\nResponse type: {type(response2)}")
    print(f"Response: {response2[:100]}..." if len(response2) > 100 else f"Response: {response2}")
    
    if isinstance(response2, str) and len(response2) > 0:
        print("✅ PASS: Response is non-empty string")
    else:
        print(f"❌ FAIL: Expected non-empty string, got {type(response2)}")
    
    print(f"\nTokens used: {tokens2}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST 3: Multiple tool calls (should deduplicate)")
print("=" * 80)

# Add more tools for multi-call test
multi_tools = test_tools + [
    {
        "name": "get_time",
        "description": "Get the current time",
        "parameters_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "The timezone, e.g. America/New_York"
                }
            },
            "required": ["timezone"]
        },
        "usage_guide": "Use this to get time information",
        "when_to_use": "When user asks about time"
    }
]

messages3 = [
    {"role": "user", "content": "What's the weather and time in New York?"}
]

try:
    response3, tokens3, details3 = ultragpt.tool_call(
        messages=messages3,
        user_tools=multi_tools,
        model="gpt-4o",
        allow_multiple=True  # Allow multiple tool calls
    )
    
    print(f"\nResponse type: {type(response3)}")
    
    if isinstance(response3, list):
        print(f"✅ PASS: Response is a list of tool calls (length: {len(response3)})")
        
        # Check for duplicates by call_id
        call_ids = [tc.get('id') for tc in response3]
        unique_ids = set(call_ids)
        
        if len(call_ids) == len(unique_ids):
            print(f"✅ PASS: No duplicate tool call IDs (all {len(unique_ids)} are unique)")
        else:
            print(f"❌ FAIL: Found duplicate tool call IDs!")
            print(f"   Total calls: {len(call_ids)}, Unique IDs: {len(unique_ids)}")
            print(f"   IDs: {call_ids}")
        
        for idx, tc in enumerate(response3):
            print(f"   Tool {idx+1}: {tc['function']['name']} (ID: {tc.get('id', 'N/A')})")
    else:
        print(f"⚠️  Response is not a list (might be single tool call): {type(response3)}")
    
    print(f"\nTokens used: {tokens3}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("If all tests passed, the fix is working correctly:")
print("1. Tool calls don't have output_text contamination")
print("2. Regular text responses work normally")
print("3. Multiple tool calls are deduplicated")
print("=" * 80)
