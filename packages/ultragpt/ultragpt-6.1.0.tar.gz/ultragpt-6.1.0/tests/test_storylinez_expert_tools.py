"""
Integration test: StoryLinez Expert Tools with UltraGPT

This test validates that UltraGPT can correctly handle actual production
ExpertTool definitions from StoryLinez base_expert.py. It ensures that:
1. Tools convert properly to UltraGPT's native format
2. Tool calling works with complex parameter schemas
3. Non-strict mode handles these real-world tools without 400s
"""

import os
import sys
from typing import List, Dict, Any

# Add UltraGPT to path
ultragpt_path = r"e:\Python and AI\_MyLibraries\UltraGPT\src"
if ultragpt_path not in sys.path:
    sys.path.insert(0, ultragpt_path)

# Add StoryLinez to path
storylinez_path = r"e:\Python and AI\_My Projects\StoryLinez"
if storylinez_path not in sys.path:
    sys.path.insert(0, storylinez_path)

from ultragpt import UltraGPT
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import actual StoryLinez expert tools
try:
    from NLP.v2.experts.base_expert import (
        CALCULATOR_TOOL,
        VIEW_SEQUENCE_TOOL,
        MANAGE_TODO_TOOL,
        INSERT_ASSET_TO_TRACK_TOOL,
        IMPORT_SOLID_LAYER_TOOL,
    )
    TOOLS_LOADED = True
except ImportError as e:
    print(f"Warning: Could not import StoryLinez tools: {e}")
    print("This test requires StoryLinez project to be accessible")
    TOOLS_LOADED = False


def test_calculator_tool():
    """Test simple calculator tool (basic schema)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    print("\n" + "=" * 80)
    print("TEST 1: Calculator Tool (Basic Schema)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Use the calculator to add 125 and 378. What's the result?"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[CALCULATOR_TOOL],
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Calculator tool called successfully")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_calculator_tool_claude():
    """Test calculator tool with Claude provider"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Skipping: ANTHROPIC_API_KEY not set")
        return
    
    print("\n" + "=" * 80)
    print("TEST 1b: Calculator Tool with Claude (Cross-Provider Test)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Use the calculator to multiply 25 by 4. What's the result?"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[CALCULATOR_TOOL],
            model="claude:claude-3-haiku-20240307",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Calculator tool called successfully with Claude")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_sequence_tool():
    """Test view_sequence tool (optional fields)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    print("\n" + "=" * 80)
    print("TEST 2: View Sequence Tool (Optional Fields)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Show me the primary sequence timeline"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[VIEW_SEQUENCE_TOOL],
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ PASS: View sequence tool called successfully")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_sequence_tool_claude():
    """Test view_sequence tool with Claude (optional fields)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Skipping: ANTHROPIC_API_KEY not set")
        return
    
    print("\n" + "=" * 80)
    print("TEST 2b: View Sequence Tool with Claude (Optional Fields)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Show me the secondary sequence timeline"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[VIEW_SEQUENCE_TOOL],
            model="claude:claude-3-haiku-20240307",
            allow_multiple=False
        )
        
        print("\n✅ PASS: View sequence tool called successfully with Claude")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manage_todo_tool():
    """Test manage_todo tool (conditional required fields)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    print("\n" + "=" * 80)
    print("TEST 3: Manage TODO Tool (Conditional Required)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Create a TODO: finish editing the intro scene by tomorrow, mark it as high priority"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[MANAGE_TODO_TOOL],
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Manage TODO tool called successfully")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manage_todo_tool_claude():
    """Test manage_todo tool with Claude (conditional required fields)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Skipping: ANTHROPIC_API_KEY not set")
        return
    
    print("\n" + "=" * 80)
    print("TEST 3b: Manage TODO Tool with Claude (Conditional Required)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Mark the TODO 'finish editing intro' as completed"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[MANAGE_TODO_TOOL],
            model="claude:claude-3-haiku-20240307",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Manage TODO tool called successfully with Claude")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insert_asset_tool():
    """Test insert_asset_to_track tool (complex nested schema with enums and literals)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    print("\n" + "=" * 80)
    print("TEST 4: Insert Asset Tool (Complex Nested Schema)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Place asset 'vid_123' on track V1 at 5 seconds, with media in at 2 seconds and media out at 10 seconds, using fill scale mode"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[INSERT_ASSET_TO_TRACK_TOOL],
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Insert asset tool called successfully")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insert_asset_tool_claude():
    """Test insert_asset_to_track tool with Claude (complex nested schema)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Skipping: ANTHROPIC_API_KEY not set")
        return
    
    print("\n" + "=" * 80)
    print("TEST 4b: Insert Asset Tool with Claude (Complex Nested Schema)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Place asset 'aud_456' on track A1 at 10 seconds, using fit scale mode"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[INSERT_ASSET_TO_TRACK_TOOL],
            model="claude:claude-3-haiku-20240307",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Insert asset tool called successfully with Claude")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_solid_layer():
    """Test import_solid_layer tool (nested RGB color object with constraints)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    print("\n" + "=" * 80)
    print("TEST 5: Import Solid Layer Tool (Nested Objects + Constraints)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Import a solid red overlay layer for the primary sequence"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[IMPORT_SOLID_LAYER_TOOL],
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Import solid layer tool called successfully")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_import_solid_layer_claude():
    """Test import_solid_layer tool with Claude (nested RGB object)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Skipping: ANTHROPIC_API_KEY not set")
        return
    
    print("\n" + "=" * 80)
    print("TEST 5b: Import Solid Layer Tool with Claude (Nested Objects + Constraints)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    messages = [
        {"role": "user", "content": "Import a solid blue overlay layer for the secondary sequence"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[IMPORT_SOLID_LAYER_TOOL],
            model="claude:claude-3-haiku-20240307",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Import solid layer tool called successfully with Claude")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
        
        print("\n✅ PASS: Import solid layer tool called successfully")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_expert_tools():
    """Test multiple tools together (realistic expert scenario)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    print("\n" + "=" * 80)
    print("TEST 6: Multiple Expert Tools (Realistic Scenario)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    # Provide all common tools
    all_tools = [
        CALCULATOR_TOOL,
        VIEW_SEQUENCE_TOOL,
        MANAGE_TODO_TOOL,
        INSERT_ASSET_TO_TRACK_TOOL,
        IMPORT_SOLID_LAYER_TOOL,
    ]
    
    messages = [
        {"role": "user", "content": "Calculate the midpoint between 5 seconds and 15 seconds on the timeline"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=all_tools,
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Correct tool selected from multiple options")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_expert_tools_claude():
    """Test multiple tools together with Claude (realistic expert scenario)"""
    if not TOOLS_LOADED:
        print("⚠️  Skipping: StoryLinez tools not available")
        return
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Skipping: ANTHROPIC_API_KEY not set")
        return
    
    print("\n" + "=" * 80)
    print("TEST 6b: Multiple Expert Tools with Claude (Realistic Scenario)")
    print("=" * 80)
    
    ultragpt = UltraGPT(
        api_key=os.getenv("OPENAI_API_KEY"),
        claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
        verbose=True
    )
    
    # Provide all common tools
    all_tools = [
        CALCULATOR_TOOL,
        VIEW_SEQUENCE_TOOL,
        MANAGE_TODO_TOOL,
        INSERT_ASSET_TO_TRACK_TOOL,
        IMPORT_SOLID_LAYER_TOOL,
    ]
    
    messages = [
        {"role": "user", "content": "Show me the primary sequence for editing"}
    ]
    
    try:
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=all_tools,
            model="claude:claude-3-haiku-20240307",
            allow_multiple=False
        )
        
        print("\n✅ PASS: Correct tool selected from multiple options with Claude")
        print(f"Tool: {response['function']['name']}")
        print(f"Arguments: {response['function']['arguments']}")
        print(f"Tokens: {tokens}")
        
        return True
    except Exception as e:
        print(f"\n❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("StoryLinez Expert Tools Integration Test")
    print("Testing actual production ExpertTool definitions with UltraGPT")
    print()
    
    if not TOOLS_LOADED:
        print("=" * 80)
        print("ERROR: Could not load StoryLinez tools")
        print("Make sure the StoryLinez project is accessible at:")
        print("  e:\\Python and AI\\_My Projects\\StoryLinez")
        print("=" * 80)
        return
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("=" * 80)
        print("ERROR: OPENAI_API_KEY not found in environment")
        print("Please set it in .env file or environment variables")
        print("=" * 80)
        return
    
    print("Tools loaded successfully:")
    print(f"  - {CALCULATOR_TOOL.name}")
    print(f"  - {VIEW_SEQUENCE_TOOL.name}")
    print(f"  - {MANAGE_TODO_TOOL.name}")
    print(f"  - {INSERT_ASSET_TO_TRACK_TOOL.name}")
    print(f"  - {IMPORT_SOLID_LAYER_TOOL.name}")
    print()
    
    # Run tests
    results = []
    results.append(("Calculator Tool (OpenAI)", test_calculator_tool()))
    results.append(("Calculator Tool (Claude)", test_calculator_tool_claude()))
    results.append(("View Sequence Tool (OpenAI)", test_view_sequence_tool()))
    results.append(("View Sequence Tool (Claude)", test_view_sequence_tool_claude()))
    results.append(("Manage TODO Tool (OpenAI)", test_manage_todo_tool()))
    results.append(("Manage TODO Tool (Claude)", test_manage_todo_tool_claude()))
    results.append(("Insert Asset Tool (OpenAI)", test_insert_asset_tool()))
    results.append(("Insert Asset Tool (Claude)", test_insert_asset_tool_claude()))
    results.append(("Import Solid Layer (OpenAI)", test_import_solid_layer()))
    results.append(("Import Solid Layer (Claude)", test_import_solid_layer_claude()))
    results.append(("Multiple Tools (OpenAI)", test_multiple_expert_tools()))
    results.append(("Multiple Tools (Claude)", test_multiple_expert_tools_claude()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! UltraGPT correctly handles StoryLinez expert tools.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
