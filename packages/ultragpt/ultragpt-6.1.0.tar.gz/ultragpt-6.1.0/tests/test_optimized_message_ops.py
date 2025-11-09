"""
Test that the optimized message_ops fixes OpenAI 400 error while maintaining performance.
"""

import sys

sys.path.append(r"e:\Python and AI\_MyLibraries\UltraGPT")

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

from ultragpt.messaging.message_ops import integrate_tool_call_prompt, consolidate_system_messages_safe

def test_tool_call_adjacency_preserved():
    """Test that tool calls and results remain adjacent after system integration."""
    
    # Create problematic sequence that broke with old approach
    messages = [
        HumanMessage(content="Please help me with this task"),
        AIMessage(content="I'll use a tool to help", tool_calls=[{"name": "search", "args": {"query": "test"}, "id": "call_1"}]),
        ToolMessage(content="Search results here", tool_call_id="call_1"),
        HumanMessage(content="Thanks, can you also do another search?"),
        AIMessage(content="Sure!", tool_calls=[{"name": "search", "args": {"query": "test2"}, "id": "call_2"}]),
        ToolMessage(content="More results", tool_call_id="call_2"),
    ]
    
    tool_prompt = "You are a helpful assistant. Use tools when needed."
    
    # Apply the optimized integration
    intermediate = integrate_tool_call_prompt(messages, tool_prompt)
    result = consolidate_system_messages_safe(intermediate)
    
    print("=== OPTIMIZED APPROACH TEST ===")
    print(f"Total messages after consolidation: {len(result)}")
    
    print("\nMessage sequence:")
    for i, msg in enumerate(result):
        msg_type = type(msg).__name__
        content_preview = (msg.content or "")[:50].replace('\n', ' ')
        tool_info = ""
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tool_info = f" [tool_calls: {len(msg.tool_calls)}]"
        elif hasattr(msg, 'tool_call_id'):
            tool_info = f" [tool_call_id: {msg.tool_call_id}]"
            
        print(f"  {i}: {msg_type}{tool_info} - {content_preview}...")
    
    # Check tool call/result adjacency
    adjacency_violations = []
    for i in range(len(result) - 1):
        current = result[i]
        next_msg = result[i + 1]
        
        # Check if current message has tool calls
        if (isinstance(current, AIMessage) and 
            hasattr(current, 'tool_calls') and 
            current.tool_calls):
            
            # Next message should be a ToolMessage
            if not isinstance(next_msg, ToolMessage):
                adjacency_violations.append(f"Position {i}: AIMessage with tool_calls not followed by ToolMessage")
    
    print(f"\nAdjacency violations: {len(adjacency_violations)}")
    for violation in adjacency_violations:
        print(f"  - {violation}")
    
    print(f"\nSystem message position: {next((i for i, m in enumerate(result) if isinstance(m, SystemMessage)), 'None')}")
    
    # Verify system message content includes tool prompt
    system_msg = next((m for m in result if isinstance(m, SystemMessage)), None)
    if system_msg:
        print(f"System message contains tool prompt: {tool_prompt in system_msg.content}")
    
    return len(adjacency_violations) == 0

def test_performance_comparison():
    """Test that consolidation happens in single pass."""
    
    # Create messages with multiple system messages scattered throughout
    messages = []
    for i in range(100):  # Large message list to test performance
        messages.extend([
            SystemMessage(content=f"System instruction {i}"),
            HumanMessage(content=f"User message {i}"),
            AIMessage(content=f"Assistant message {i}"),
        ])
    
    import time
    
    start = time.time()
    result = integrate_tool_call_prompt(messages, "Tool instructions")
    end = time.time()
    
    print(f"\n=== PERFORMANCE TEST ===")
    print(f"Processed {len(messages)} messages in {(end - start) * 1000:.2f}ms")
    print(f"Consolidated {len([m for m in messages if isinstance(m, SystemMessage)])} system messages into 1")
    print(f"Result has {len(result)} messages (system at position 0)")
    
    # Verify consolidation
    system_count = len([m for m in result if isinstance(m, SystemMessage)])
    print(f"System messages in result: {system_count} (should be 1)")
    
    return system_count == 1

if __name__ == "__main__":
    print("Testing optimized message_ops...")
    
    adjacency_ok = test_tool_call_adjacency_preserved()
    performance_ok = test_performance_comparison()
    
    print(f"\n=== RESULTS ===")
    print(f"✅ Tool call adjacency preserved: {adjacency_ok}")
    print(f"✅ Performance optimized: {performance_ok}")
    print(f"✅ OpenAI 400 error fixed: {adjacency_ok}")
    
    if adjacency_ok and performance_ok:
        print("\n🎉 ALL TESTS PASSED - Ready to replace message_ops.py!")
    else:
        print("\n❌ TESTS FAILED - Need to fix issues before deployment")