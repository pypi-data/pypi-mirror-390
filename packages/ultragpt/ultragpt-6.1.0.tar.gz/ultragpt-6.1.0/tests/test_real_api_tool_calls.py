"""
Real API test for Claude with tool calls to verify no count_tokens errors.

This test makes actual API calls to Claude to verify the grouping solution works in practice.
Run this test only when you have ANTHROPIC_API_KEY or CLAUDE_API_KEY set.
"""

import os
import sys
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from dotenv import load_dotenv

# Load .env file from UltraGPT root
ultragpt_root = Path(__file__).parent.parent
env_path = ultragpt_root / ".env"
if env_path.exists():
    load_dotenv(env_path)

# Add UltraGPT to path
sys.path.insert(0, str(ultragpt_root / "src"))

# Get API keys
claude_api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

from ultragpt.providers import ProviderManager, ClaudeProvider, OpenAIProvider
from ultragpt.messaging import LangChainTokenLimiter, validate_tool_call_pairing_lc


def print_separator(title: str):
    """Print a clear separator."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def create_long_tool_call_history():
    """Create a long history with many tool calls to trigger truncation."""
    messages = [
        SystemMessage(content="You are a helpful weather assistant with access to tools. " * 50),  # Make system message larger
        HumanMessage(content="What's the weather in New York? " * 20),  # Make user messages larger
    ]
    
    # Add many tool call interactions to ensure truncation
    cities = ["New York", "Boston", "Chicago", "LA", "Miami", "Seattle", "Denver", 
              "Portland", "Phoenix", "Atlanta", "Dallas", "Houston", "Austin", "Detroit",
              "Minneapolis", "Philadelphia", "San Francisco", "San Diego", "Las Vegas", "Orlando"]
    
    for i, city in enumerate(cities):
        messages.append(
            AIMessage(
                content="Let me check the weather for you." * 10,  # Removed trailing space
                tool_calls=[
                    {
                        "id": f"call_{i}",
                        "name": "get_weather",
                        "args": {"location": city, "detailed": True, "forecast_days": 7},
                        "type": "tool_call",
                    }
                ],
            )
        )
        messages.append(
            ToolMessage(
                content=f'{{"temp": {70 + i}, "condition": "sunny", "humidity": {50 + i}, "wind_speed": {10 + i}, "forecast": "Detailed forecast data here..." * 10}}',
                tool_call_id=f"call_{i}",
                name="get_weather",
            )
        )
        messages.append(
            AIMessage(content=f"The weather in {city} is {70 + i}°F and sunny. Here's the detailed forecast..." * 15)
        )
        
        if i < len(cities) - 1:
            messages.append(HumanMessage(content=f"What about {cities[i + 1]}? Can you give me detailed forecast? " * 10))
    
    return messages


def test_claude_with_truncation():
    """Test Claude with actual API calls and truncation."""
    print_separator("CLAUDE API TEST WITH TRUNCATION")
    
    if not claude_api_key:
        print("❌ SKIPPED: No Claude API key found")
        print("   Set ANTHROPIC_API_KEY or CLAUDE_API_KEY to run this test\n")
        return None
    
    try:
        # Create provider manager with truncation enabled
        manager = ProviderManager(
            token_limiter=LangChainTokenLimiter(),
            default_input_truncation="AUTO",  # Use model's max context
            verbose=True,
        )
        
        # Add Claude provider
        claude = ClaudeProvider(api_key=claude_api_key)
        manager.add_provider("claude", claude)
        
        # Create long history
        messages = create_long_tool_call_history()
        print(f"Created {len(messages)} messages with multiple tool calls")
        print()
        
        # Validate messages before sending
        validation = validate_tool_call_pairing_lc(messages)
        print("Pre-truncation validation:")
        print(f"  Valid: {validation['valid']}")
        print(f"  Orphaned: {validation['orphaned_tool_results']}")
        print(f"  Missing: {validation['missing_tool_results']}")
        print()
        
        # Make API call with larger token budget to force truncation while keeping valid conversation
        print("Making API call to Claude with truncation (2000 tokens)...")
        print("This should remove many older messages but keep enough for valid conversation...")
        response, tokens = manager.chat_completion(
            model="claude:claude-sonnet-4-5-20250929",
            messages=messages,
            temperature=0.7,
            input_truncation=2000,  # Larger budget - should truncate but keep valid conversation
        )
        
        print(f"\n✅ SUCCESS! No count_tokens errors!")
        print(f"   Response length: {len(response)} chars")
        print(f"   Tokens used: {tokens}")
        print(f"   Response preview: {response[:200]}...")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_openai_with_truncation():
    """Test OpenAI with actual API calls and truncation."""
    print_separator("OPENAI API TEST WITH TRUNCATION")
    
    if not openai_api_key:
        print("❌ SKIPPED: No OpenAI API key found")
        print("   Set OPENAI_API_KEY to run this test\n")
        return None
    
    try:
        # Create provider manager
        manager = ProviderManager(
            token_limiter=LangChainTokenLimiter(),
            default_input_truncation="AUTO",
            verbose=True,
        )
        
        # Add OpenAI provider
        openai = OpenAIProvider(api_key=openai_api_key)
        manager.add_provider("openai", openai)
        
        # Create long history
        messages = create_long_tool_call_history()
        print(f"Created {len(messages)} messages with multiple tool calls")
        print()
        
        # Validate messages
        validation = validate_tool_call_pairing_lc(messages)
        print("Pre-truncation validation:")
        print(f"  Valid: {validation['valid']}")
        print()
        
        # Make API call with larger budget
        print("Making API call to OpenAI with truncation (2000 tokens)...")
        print("This should remove many older messages but keep enough for valid conversation...")
        response, tokens = manager.chat_completion(
            model="openai:gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            input_truncation=2000,  # Larger budget
        )
        
        print(f"\n✅ SUCCESS! No errors!")
        print(f"   Response length: {len(response)} chars")
        print(f"   Tokens used: {tokens}")
        print(f"   Response preview: {response[:200]}...")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run real API tests."""
    print("\n" + "🔥" * 40)
    print("  REAL API TESTS WITH TOOL CALL TRUNCATION")
    print("🔥" * 40)
    
    results = {
        "Claude": test_claude_with_truncation(),
        "OpenAI": test_openai_with_truncation(),
    }
    
    print("\n" + "=" * 80)
    print("  FINAL RESULTS")
    print("=" * 80)
    
    for provider, passed in results.items():
        if passed is True:
            print(f"  ✅ {provider}: PASSED")
        elif passed is False:
            print(f"  ❌ {provider}: FAILED")
        else:
            print(f"  ⚠️  {provider}: SKIPPED")
    
    print("=" * 80 + "\n")
    
    # Exit with error if any tests failed (not skipped)
    if any(result is False for result in results.values()):
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All API tests passed or skipped!")
        sys.exit(0)


if __name__ == "__main__":
    main()
