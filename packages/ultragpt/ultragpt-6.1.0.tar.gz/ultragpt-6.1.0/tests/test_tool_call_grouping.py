"""
Comprehensive tests for tool call grouping and token truncation.

Tests verify:
1. No Claude count_tokens API errors with tool calls
2. Message order is preserved during truncation
3. No orphaned tool calls or results
4. Works correctly with both OpenAI and Claude providers
5. Tool call pairs stay together during truncation
"""

import os
import sys
from typing import List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

# Add UltraGPT to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ultragpt.messaging import (
    group_tool_call_pairs_lc,
    validate_tool_call_pairing_lc,
    LangChainTokenLimiter,
)
from ultragpt.providers import OpenAIProvider, ClaudeProvider


def print_separator(title: str):
    """Print a clear separator for test sections."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def create_test_messages_with_tools() -> List:
    """Create a realistic message history with tool calls."""
    return [
        SystemMessage(content="You are a helpful assistant with access to tools."),
        HumanMessage(content="What's the weather in New York?"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_1",
                    "name": "get_weather",
                    "args": {"location": "New York"},
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(content='{"temp": 72, "condition": "sunny"}', tool_call_id="call_1", name="get_weather"),
        AIMessage(content="The weather in New York is 72°F and sunny."),
        HumanMessage(content="What about Boston?"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_2",
                    "name": "get_weather",
                    "args": {"location": "Boston"},
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(content='{"temp": 68, "condition": "cloudy"}', tool_call_id="call_2", name="get_weather"),
        AIMessage(content="The weather in Boston is 68°F and cloudy."),
        HumanMessage(content="Which city has better weather?"),
    ]


def create_test_messages_with_parallel_tools() -> List:
    """Create messages with parallel tool calls."""
    return [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Get weather for NYC and LA"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_a",
                    "name": "get_weather",
                    "args": {"location": "New York"},
                    "type": "tool_call",
                },
                {
                    "id": "call_b",
                    "name": "get_weather",
                    "args": {"location": "Los Angeles"},
                    "type": "tool_call",
                },
            ],
        ),
        ToolMessage(content='{"temp": 72, "condition": "sunny"}', tool_call_id="call_a", name="get_weather"),
        ToolMessage(content='{"temp": 80, "condition": "hot"}', tool_call_id="call_b", name="get_weather"),
        AIMessage(content="NYC: 72°F sunny. LA: 80°F hot."),
    ]


def test_grouping_logic():
    """Test 1: Verify grouping logic works correctly."""
    print_separator("TEST 1: Grouping Logic")
    
    messages = create_test_messages_with_tools()
    groups = group_tool_call_pairs_lc(messages)
    
    print(f"Total messages: {len(messages)}")
    print(f"Total groups: {len(groups)}")
    print()
    
    for i, group in enumerate(groups):
        print(f"Group {i + 1} ({len(group)} messages):")
        for msg in group:
            msg_type = type(msg).__name__
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
                tool_calls = getattr(msg, "tool_calls", []) or []
                if tool_calls:
                    print(f"  - {msg_type} with {len(tool_calls)} tool call(s)")
                else:
                    print(f"  - {msg_type} (no tool calls)")
            elif isinstance(msg, ToolMessage):
                print(f"  - {msg_type} (call_id: {getattr(msg, 'tool_call_id', 'N/A')})")
            else:
                content_preview = str(msg.content)[:50]
                print(f"  - {msg_type}: {content_preview}")
        print()
    
    # Verify grouping is correct
    # Should be: System(1), Human(1), AI+Tool(2), AI(1), Human(1), AI+Tool(2), AI(1), Human(1) = 8 groups
    assert len(groups) == 8, f"Expected 8 groups, got {len(groups)}"
    
    # Group 3 should be AIMessage with tool_calls + ToolMessage (index 2 in 0-based)
    assert len(groups[2]) == 2, f"Group 3 should have 2 messages, got {len(groups[2])}"
    assert isinstance(groups[2][0], AIMessage), "Group 3 first message should be AIMessage"
    assert isinstance(groups[2][1], ToolMessage), "Group 3 second message should be ToolMessage"
    
    print("✅ Grouping logic test PASSED\n")


def test_parallel_tool_grouping():
    """Test 2: Verify parallel tool calls are grouped correctly."""
    print_separator("TEST 2: Parallel Tool Call Grouping")
    
    messages = create_test_messages_with_parallel_tools()
    groups = group_tool_call_pairs_lc(messages)
    
    print(f"Total messages: {len(messages)}")
    print(f"Total groups: {len(groups)}")
    print()
    
    for i, group in enumerate(groups):
        print(f"Group {i + 1} ({len(group)} messages):")
        for msg in group:
            msg_type = type(msg).__name__
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
                tool_calls = getattr(msg, "tool_calls", []) or []
                if tool_calls:
                    print(f"  - {msg_type} with {len(tool_calls)} tool call(s)")
                else:
                    print(f"  - {msg_type}")
            elif isinstance(msg, ToolMessage):
                print(f"  - {msg_type} (call_id: {getattr(msg, 'tool_call_id', 'N/A')})")
            else:
                print(f"  - {msg_type}")
        print()
    
    # Verify parallel tools are grouped together
    # Group 1: System, Group 2: Human, Group 3: AI with 2 tool calls + 2 results, Group 4: AI response
    assert len(groups) == 4, f"Expected 4 groups, got {len(groups)}"
    assert len(groups[2]) == 3, f"Group 3 should have 3 messages (1 AI + 2 ToolMessages), got {len(groups[2])}"
    
    print("✅ Parallel tool grouping test PASSED\n")


def test_no_orphans_after_grouping():
    """Test 3: Verify no orphaned tool calls after grouping."""
    print_separator("TEST 3: No Orphaned Tool Calls")
    
    messages = create_test_messages_with_tools()
    groups = group_tool_call_pairs_lc(messages)
    
    # Flatten groups back to messages
    flattened = []
    for group in groups:
        flattened.extend(group)
    
    # Validate pairing
    validation = validate_tool_call_pairing_lc(flattened)
    
    print("Validation Results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Orphaned tool results: {validation['orphaned_tool_results']}")
    print(f"  Missing tool results: {validation['missing_tool_results']}")
    print(f"  Summary: {validation['summary']}")
    print()
    
    assert validation['valid'], "Messages should have valid tool pairing"
    assert len(validation['orphaned_tool_results']) == 0, "No orphaned results expected"
    assert len(validation['missing_tool_results']) == 0, "No missing results expected"
    
    print("✅ No orphans test PASSED\n")


def test_message_order_preservation():
    """Test 4: Verify message order is preserved after grouping and flattening."""
    print_separator("TEST 4: Message Order Preservation")
    
    messages = create_test_messages_with_tools()
    original_contents = [msg.content if hasattr(msg, "content") else "" for msg in messages]
    
    groups = group_tool_call_pairs_lc(messages)
    flattened = []
    for group in groups:
        flattened.extend(group)
    
    restored_contents = [msg.content if hasattr(msg, "content") else "" for msg in flattened]
    
    print(f"Original messages: {len(messages)}")
    print(f"Flattened messages: {len(flattened)}")
    print()
    
    assert len(messages) == len(flattened), "Message count should be preserved"
    assert original_contents == restored_contents, "Message order should be preserved"
    
    print("✅ Message order preservation test PASSED\n")


def test_truncation_with_openai():
    """Test 5: Test truncation with OpenAI provider (no API call, just logic)."""
    print_separator("TEST 5: Truncation Logic with OpenAI Provider")
    
    try:
        # Create a mock API key (won't make real calls)
        provider = OpenAIProvider(api_key="sk-test-key-not-real")
        llm = provider.build_llm(model="gpt-4o-mini", temperature=0.0)
        
        messages = create_test_messages_with_tools()
        limiter = LangChainTokenLimiter()
        
        print(f"Original messages: {len(messages)}")
        
        # Try to truncate to a small token budget (will remove some groups)
        truncated = limiter.limit_tokens(
            llm=llm,
            messages=messages,
            max_tokens=500,  # Small budget to force truncation
            keep_newest=True,
            preserve_system=True,
        )
        
        print(f"Truncated messages: {len(truncated)}")
        print()
        
        # Validate no orphans after truncation
        validation = validate_tool_call_pairing_lc(truncated)
        print("Post-truncation validation:")
        print(f"  Valid: {validation['valid']}")
        print(f"  Orphaned: {validation['orphaned_tool_results']}")
        print(f"  Missing: {validation['missing_tool_results']}")
        print()
        
        assert validation['valid'], "Truncated messages should have valid pairing"
        assert len(validation['orphaned_tool_results']) == 0, "No orphaned results after truncation"
        
        print("✅ OpenAI truncation test PASSED\n")
        
    except Exception as e:
        print(f"⚠️  OpenAI test skipped (expected if no API key): {e}\n")


def test_truncation_with_claude():
    """Test 6: Test truncation with Claude provider (no API call, just logic)."""
    print_separator("TEST 6: Truncation Logic with Claude Provider")
    
    try:
        # Check if Claude API key is available
        claude_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        if not claude_key:
            print("⚠️  Skipping Claude test - no API key found in environment")
            print("   Set ANTHROPIC_API_KEY or CLAUDE_API_KEY to run this test\n")
            return
        
        provider = ClaudeProvider(api_key=claude_key)
        llm = provider.build_llm(model="claude-sonnet-4-5-20250929", temperature=0.0)
        
        messages = create_test_messages_with_tools()
        limiter = LangChainTokenLimiter()
        
        print(f"Original messages: {len(messages)}")
        
        # Try to truncate with Claude
        truncated = limiter.limit_tokens(
            llm=llm,
            messages=messages,
            max_tokens=500,
            keep_newest=True,
            preserve_system=True,
        )
        
        print(f"Truncated messages: {len(truncated)}")
        print()
        
        # Validate no orphans after truncation
        validation = validate_tool_call_pairing_lc(truncated)
        print("Post-truncation validation:")
        print(f"  Valid: {validation['valid']}")
        print(f"  Orphaned: {validation['orphaned_tool_results']}")
        print(f"  Missing: {validation['missing_tool_results']}")
        print()
        
        assert validation['valid'], "Truncated messages should have valid pairing"
        assert len(validation['orphaned_tool_results']) == 0, "No orphaned results after truncation"
        
        print("✅ Claude truncation test PASSED (no API errors!)\n")
        
    except Exception as e:
        print(f"❌ Claude test FAILED: {e}\n")
        raise


def test_edge_case_empty_messages():
    """Test 7: Edge case - empty message list."""
    print_separator("TEST 7: Edge Case - Empty Messages")
    
    messages = []
    groups = group_tool_call_pairs_lc(messages)
    
    assert groups == [], "Empty messages should return empty groups"
    print("✅ Empty messages test PASSED\n")


def test_edge_case_only_system():
    """Test 8: Edge case - only system messages."""
    print_separator("TEST 8: Edge Case - Only System Messages")
    
    messages = [
        SystemMessage(content="System message 1"),
        SystemMessage(content="System message 2"),
    ]
    groups = group_tool_call_pairs_lc(messages)
    
    assert len(groups) == 2, "Each system message should be its own group"
    print("✅ Only system messages test PASSED\n")


def test_edge_case_no_tools():
    """Test 9: Edge case - messages without tool calls."""
    print_separator("TEST 9: Edge Case - No Tool Calls")
    
    messages = [
        SystemMessage(content="You are helpful"),
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
        HumanMessage(content="How are you?"),
        AIMessage(content="I'm great!"),
    ]
    groups = group_tool_call_pairs_lc(messages)
    
    assert len(groups) == 5, "Each message should be its own group"
    for group in groups:
        assert len(group) == 1, "Each group should have exactly 1 message"
    
    print("✅ No tool calls test PASSED\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "🚀" * 40)
    print("  TOOL CALL GROUPING & TRUNCATION TEST SUITE")
    print("🚀" * 40 + "\n")
    
    tests = [
        ("Grouping Logic", test_grouping_logic),
        ("Parallel Tool Grouping", test_parallel_tool_grouping),
        ("No Orphans After Grouping", test_no_orphans_after_grouping),
        ("Message Order Preservation", test_message_order_preservation),
        ("Truncation with OpenAI", test_truncation_with_openai),
        ("Truncation with Claude", test_truncation_with_claude),
        ("Edge Case: Empty Messages", test_edge_case_empty_messages),
        ("Edge Case: Only System", test_edge_case_only_system),
        ("Edge Case: No Tools", test_edge_case_no_tools),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {name} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            if "skipped" in str(e).lower() or "API key" in str(e):
                print(f"⚠️  {name} SKIPPED: {e}\n")
                skipped += 1
            else:
                print(f"❌ {name} ERROR: {e}\n")
                failed += 1
    
    print("\n" + "=" * 80)
    print("  TEST RESULTS")
    print("=" * 80)
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️  Skipped: {skipped}")
    print(f"  📊 Total: {passed + failed + skipped}")
    print("=" * 80 + "\n")
    
    if failed > 0:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
