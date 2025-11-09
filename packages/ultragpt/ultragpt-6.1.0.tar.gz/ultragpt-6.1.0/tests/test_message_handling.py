"""
Tests for message handling: orphan tool results, truncation, order preservation, system message retention.
"""

import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from ultragpt.messaging import (
    remove_orphaned_tool_results_lc,
    LangChainTokenLimiter,
)
from ultragpt.providers import OpenAIProvider


@pytest.fixture
def llm():
    """Create a mock LLM for testing truncation."""
    provider = OpenAIProvider(api_key="test-key-for-testing")
    return provider.build_llm(model="gpt-4", temperature=0.0)


def test_orphan_tool_result_removal():
    """Test that orphaned tool results (without corresponding tool calls) are removed."""
    messages = [
        SystemMessage(content="You are a helpful assistant"),
        HumanMessage(content="Hello"),
        AIMessage(content="Hi! How can I help?"),
        # Orphaned tool message - no tool_calls in previous AIMessage
        ToolMessage(content="Result from nowhere", tool_call_id="orphan-123"),
        HumanMessage(content="What's the weather?"),
    ]
    
    cleaned = remove_orphaned_tool_results_lc(messages)
    
    # Should remove the orphaned ToolMessage
    assert len(cleaned) == 4
    assert isinstance(cleaned[0], SystemMessage)
    assert isinstance(cleaned[1], HumanMessage)
    assert isinstance(cleaned[2], AIMessage)
    assert isinstance(cleaned[3], HumanMessage)
    # No ToolMessage should remain
    assert not any(isinstance(msg, ToolMessage) for msg in cleaned)


def test_valid_tool_call_result_preserved():
    """Test that valid tool calls with results are preserved."""
    messages = [
        SystemMessage(content="You are a helpful assistant"),
        HumanMessage(content="Search for Python"),
        AIMessage(
            content="",
            tool_calls=[{
                "id": "call-123",
                "name": "web_search",
                "args": {"query": "Python"}
            }]
        ),
        ToolMessage(content="Python is a programming language", tool_call_id="call-123"),
        AIMessage(content="Python is a popular programming language."),
    ]
    
    cleaned = remove_orphaned_tool_results_lc(messages)
    
    # All messages should be preserved
    assert len(cleaned) == 5
    assert isinstance(cleaned[3], ToolMessage)
    assert cleaned[3].tool_call_id == "call-123"


def test_mixed_orphaned_and_valid_tool_results():
    """Test removing orphans while preserving valid tool results."""
    messages = [
        SystemMessage(content="System prompt"),
        HumanMessage(content="First query"),
        AIMessage(
            content="",
            tool_calls=[{"id": "valid-1", "name": "tool1", "args": {}}]
        ),
        ToolMessage(content="Valid result 1", tool_call_id="valid-1"),
        ToolMessage(content="Orphan result", tool_call_id="orphan-1"),  # Orphan!
        HumanMessage(content="Second query"),
        AIMessage(content="Response without tools"),
        ToolMessage(content="Another orphan", tool_call_id="orphan-2"),  # Orphan!
    ]
    
    cleaned = remove_orphaned_tool_results_lc(messages)
    
    # Should keep valid tool result, remove 2 orphans
    assert len(cleaned) == 6
    tool_messages = [msg for msg in cleaned if isinstance(msg, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].tool_call_id == "valid-1"


def test_message_truncation_preserves_order(llm):
    """Test that truncation preserves message order."""
    # Create many messages
    messages = [SystemMessage(content="System prompt")]
    for i in range(50):
        messages.append(HumanMessage(content=f"User message {i}"))
        messages.append(AIMessage(content=f"AI response {i}"))
    
    limiter = LangChainTokenLimiter()
    
    # Truncate to ~1000 tokens (should keep only recent messages)
    truncated = limiter.apply_input_truncation(
        llm=llm,
        message_groups=[messages],
        max_tokens=1000,
        keep_newest=True,
        preserve_system=True
    )
    
    # Should preserve order
    prev_idx = -1
    for msg in truncated:
        if isinstance(msg, HumanMessage) and msg.content.startswith("User message"):
            idx = int(msg.content.split()[-1])
            assert idx > prev_idx or prev_idx == -1, "Message order violated!"
            prev_idx = idx


def test_message_truncation_preserves_system_messages(llm):
    """Test that system messages are always preserved during truncation."""
    messages = [
        SystemMessage(content="Important system prompt"),
        SystemMessage(content="Another system instruction"),
    ]
    # Add many user/AI messages
    for i in range(100):
        messages.append(HumanMessage(content=f"Message {i}" * 50))  # Long messages
        messages.append(AIMessage(content=f"Response {i}" * 50))
    
    limiter = LangChainTokenLimiter()
    
    # Aggressive truncation
    truncated = limiter.apply_input_truncation(
        llm=llm,
        message_groups=[messages],
        max_tokens=500,
        keep_newest=True,
        preserve_system=True
    )
    
    # System messages MUST be preserved
    system_msgs = [msg for msg in truncated if isinstance(msg, SystemMessage)]
    assert len(system_msgs) == 2
    assert system_msgs[0].content == "Important system prompt"
    assert system_msgs[1].content == "Another system instruction"
    
    # System messages should be at the beginning
    assert isinstance(truncated[0], SystemMessage)
    assert isinstance(truncated[1], SystemMessage)


def test_truncation_removes_orphans(llm):
    """Test that truncation also removes orphaned tool results."""
    messages = [
        SystemMessage(content="System"),
        HumanMessage(content="Query 1"),
        AIMessage(content="Response 1"),
        ToolMessage(content="Orphan 1", tool_call_id="orphan-1"),  # Orphan
        HumanMessage(content="Query 2" * 100),  # Long message
        AIMessage(
            content="",
            tool_calls=[{"id": "valid-1", "name": "tool", "args": {}}]
        ),
        ToolMessage(content="Valid result", tool_call_id="valid-1"),
        AIMessage(content="Final response"),
    ]
    
    limiter = LangChainTokenLimiter()
    
    truncated = limiter.apply_input_truncation(
        llm=llm,
        message_groups=[messages],
        max_tokens=500,
        keep_newest=True,
        preserve_system=True
    )
    
    # Should remove orphans
    tool_msgs = [msg for msg in truncated if isinstance(msg, ToolMessage)]
    # Only valid tool result should remain (if it fits)
    for tool_msg in tool_msgs:
        assert tool_msg.tool_call_id != "orphan-1"


def test_huge_message_list_truncation(llm):
    """Test truncation with a huge message list (stress test)."""
    messages = [
        SystemMessage(content="System prompt"),
        SystemMessage(content="Another system message"),
    ]
    
    # Create 1000 messages
    for i in range(500):
        messages.append(HumanMessage(content=f"User query {i}: " + "word " * 100))
        messages.append(AIMessage(content=f"AI response {i}: " + "word " * 100))
    
    limiter = LangChainTokenLimiter()
    
    # Truncate to 2000 tokens
    truncated = limiter.apply_input_truncation(
        llm=llm,
        message_groups=[messages],
        max_tokens=2000,
        keep_newest=True,
        preserve_system=True
    )
    
    # Should significantly reduce message count
    assert len(truncated) < len(messages)
    
    # System messages preserved
    assert isinstance(truncated[0], SystemMessage)
    assert isinstance(truncated[1], SystemMessage)
    
    # Order preserved
    indices = []
    for msg in truncated:
        if isinstance(msg, HumanMessage) and msg.content.startswith("User query"):
            idx = int(msg.content.split()[2].rstrip(':'))
            indices.append(idx)
    
    # Indices should be monotonically increasing
    assert indices == sorted(indices)


def test_empty_message_list(llm):
    """Test handling of empty message lists."""
    messages = []
    
    cleaned = remove_orphaned_tool_results_lc(messages)
    assert len(cleaned) == 0
    
    limiter = LangChainTokenLimiter()
    truncated = limiter.apply_input_truncation(
        llm=llm,
        message_groups=[messages],
        max_tokens=1000,
        keep_newest=True,
        preserve_system=True
    )
    assert len(truncated) == 0


def test_all_orphaned_tool_results():
    """Test when all messages are orphaned tool results."""
    messages = [
        ToolMessage(content="Orphan 1", tool_call_id="orphan-1"),
        ToolMessage(content="Orphan 2", tool_call_id="orphan-2"),
        ToolMessage(content="Orphan 3", tool_call_id="orphan-3"),
    ]
    
    cleaned = remove_orphaned_tool_results_lc(messages)
    
    # All should be removed
    assert len(cleaned) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
