"""Test that message content is properly stripped of trailing/leading whitespace."""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Add the src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
load_dotenv()

from ultragpt.providers.providers import ProviderManager
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def test_strip_whitespace_basic():
    """Test that whitespace is stripped from message content."""
    pm = ProviderManager(verbose=True)
    
    # Initialize providers
    pm.add_provider("claude", os.getenv("ANTHROPIC_API_KEY"))
    pm.add_provider("openai", os.getenv("OPENAI_API_KEY"))
    
    # Create messages with trailing/leading whitespace
    messages = [
        SystemMessage(content="You are a helpful assistant.  "),  # Trailing spaces
        HumanMessage(content="  Hello there  "),  # Both sides
        AIMessage(content="Hi! How can I help?\n"),  # Trailing newline
    ]
    
    # Prepare messages (no truncation)
    prepared = pm._prepare_messages(
        provider_name="claude",
        model_name="claude-3-5-sonnet-20241022",
        messages=messages,
        input_truncation=None,
        keep_newest=True,
    )
    
    # Verify all content is stripped
    assert prepared[0].content == "You are a helpful assistant.", f"System content not stripped: '{prepared[0].content}'"
    assert prepared[1].content == "Hello there", f"Human content not stripped: '{prepared[1].content}'"
    assert prepared[2].content == "Hi! How can I help?", f"AI content not stripped: '{prepared[2].content}'"
    
    print("✅ Basic strip test passed")
    print(f"   System: '{prepared[0].content}'")
    print(f"   Human: '{prepared[1].content}'")
    print(f"   AI: '{prepared[2].content}'")


def test_strip_whitespace_with_real_api():
    """Test that stripped messages work with real Claude API."""
    pm = ProviderManager(verbose=True)
    
    # Initialize providers
    pm.add_provider("claude", os.getenv("ANTHROPIC_API_KEY"))
    pm.add_provider("openai", os.getenv("OPENAI_API_KEY"))
    
    # Create messages with trailing whitespace that would normally fail
    messages = [
        SystemMessage(content="You are a helpful assistant.  "),  # Trailing spaces
        HumanMessage(content="Say 'hello' back  "),  # Trailing spaces
    ]
    
    try:
        # This should work now because we strip whitespace
        response = pm.chat(
            provider="claude",
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            temperature=0.0,
        )
        
        print("✅ Real API test passed")
        print(f"   Response: {response['content'][:100]}")
        assert "hello" in response["content"].lower(), "Response should contain 'hello'"
        
    except Exception as e:
        print(f"❌ Real API test failed: {e}")
        raise


if __name__ == "__main__":
    print("Testing content stripping...")
    print("=" * 60)
    
    test_strip_whitespace_basic()
    print()
    
    # Only run real API test if we have an API key
    if os.getenv("ANTHROPIC_API_KEY"):
        test_strip_whitespace_with_real_api()
    else:
        print("⚠️  Skipping real API test (no ANTHROPIC_API_KEY)")
    
    print()
    print("=" * 60)
    print("All tests completed!")
