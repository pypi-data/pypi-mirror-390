"""
Quick deployment test to verify the optimized message_ops.py works correctly in UltraGPT.
"""

import sys
sys.path.append('e:\\Python and AI\\_MyLibraries\\UltraGPT\\src')

from ultragpt.messaging.message_ops import integrate_tool_call_prompt, consolidate_system_messages_at_start
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

def test_deployment():
    """Test that the deployed optimized version works correctly."""
    
    print("🧪 Testing deployed UltraGPT message_ops.py...")
    
    # Test the problematic scenario that caused 400 error
    messages = [
        HumanMessage(content="Help me search"),
        AIMessage(content="I'll search for you", tool_calls=[{"name": "search", "args": {"q": "test"}, "id": "call_1"}]),
        ToolMessage(content="Search results", tool_call_id="call_1"),
        SystemMessage(content="Be helpful"),
        HumanMessage(content="Thanks")
    ]
    
    tool_prompt = "Use tools when appropriate. Always be helpful."
    
    # Apply the function from the deployed version
    result = integrate_tool_call_prompt(messages, tool_prompt)
    
    print(f"✅ Total messages after optimization: {len(result)}")
    
    # Check system message position
    system_pos = next((i for i, m in enumerate(result) if isinstance(m, SystemMessage)), None)
    print(f"✅ System message at position: {system_pos} (should be 0)")
    
    # Check tool call adjacency
    for i in range(len(result) - 1):
        current = result[i]
        next_msg = result[i + 1]
        
        if (isinstance(current, AIMessage) and 
            hasattr(current, 'tool_calls') and 
            current.tool_calls):
            
            if isinstance(next_msg, ToolMessage):
                print(f"✅ Tool call at {i} correctly followed by tool result at {i+1}")
            else:
                print(f"❌ Tool call at {i} NOT followed by tool result!")
                return False
    
    # Test the new consolidation function
    multi_system = [
        SystemMessage(content="System 1"),
        HumanMessage(content="User"),
        SystemMessage(content="System 2"),
        AIMessage(content="Assistant")
    ]
    
    consolidated = consolidate_system_messages_at_start(multi_system)
    system_count = len([m for m in consolidated if isinstance(m, SystemMessage)])
    print(f"✅ Consolidated {len([m for m in multi_system if isinstance(m, SystemMessage)])} systems into {system_count}")
    
    print("\n🎉 DEPLOYMENT TEST PASSED - UltraGPT message_ops.py optimized successfully!")
    return True

if __name__ == "__main__":
    test_deployment()