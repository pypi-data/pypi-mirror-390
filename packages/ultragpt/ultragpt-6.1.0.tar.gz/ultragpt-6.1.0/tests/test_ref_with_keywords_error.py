"""Test to reproduce OpenAI 400 error: $ref cannot have keywords {'default', 'description'}

This test helps reproduce and validate fixes for the specific error where Pydantic generates
schemas with $ref alongside other keywords, which OpenAI rejects.

================================================================================
HOW TO ADD NEW ERROR REPRODUCTION TESTS
================================================================================

When you encounter a new OpenAI schema validation error:

1. **Copy the error message** - Get the exact error from OpenAI API:
   Example: "Invalid schema for function 'xyz': $ref cannot have keywords {'default', 'description'}"

2. **Identify the problematic pattern** - Look at what schema pattern causes it:
   - Is it $ref with keywords?
   - Is it missing required/additionalProperties?
   - Is it anyOf/oneOf/allOf?
   - Is it arrays without items?

3. **Create minimal Pydantic models** - Build the SMALLEST model that reproduces it:
   ```python
   class ProblematicModel(BaseModel):
       # The field that causes the error
       field: Optional[NestedModel] = Field(default=None, description="...")
   ```

4. **Generate and inspect schema** - Check what Pydantic generates:
   ```python
   raw_schema = ProblematicModel.model_json_schema()
   print(json.dumps(raw_schema, indent=2))
   ```

5. **Create reproduction function** - Add a test function like below:
   ```python
   def test_new_error_case():
       print("\\n" + "="*80)
       print("TEST: Reproducing [ERROR NAME]")
       print("="*80)
       
       # Show raw schema
       raw_schema = ProblematicModel.model_json_schema()
       print(f"\\n📋 Raw Schema:\\n{json.dumps(raw_schema, indent=2)}")
       
       # Attempt to use with UltraGPT (should fail before fix, pass after)
       # ... test code ...
   ```

6. **Add to edge case tests** - Also add to test_schema_edge_cases.py:
   ```python
   def test_new_edge_case():
       schema = {...problem pattern...}
       cleaned = sanitize_tool_parameters_schema(schema)
       assert ..., "Should fix the problem"
   ```

7. **Document in memory** - Save the pattern for future reference:
   ```python
   mcp_infinite-code_memory_add(
       title="OpenAI Error: [error name]",
       content="Pattern: ... Fix: ...",
       tags=["openai", "schema", "error"]
   )
   ```

================================================================================
CURRENT TEST: $ref with keywords
================================================================================
This test reproduces the error where Optional[NestedModel] generates:
{
  "anyOf": [{"$ref": "#/$defs/NestedModel"}, {"type": "null"}],
  "default": null,
  "description": "..."
}

OpenAI rejects this because $ref cannot have sibling keywords.
"""

import os
import sys
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional
import json

# Add UltraGPT to path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from ultragpt import UltraGPT
from dotenv import load_dotenv

load_dotenv()

# Define nested schema that will cause $ref issues
class AnimationKeyframe(BaseModel):
    """A keyframe in an animation timeline"""
    time: float = Field(..., description="Time in seconds")
    value: float = Field(..., description="Value at this time")

class ClipAnimation(BaseModel):
    """Animation configuration for a clip property"""
    keyframes: list[AnimationKeyframe] = Field(..., description="Animation keyframes")
    interpolation: str = Field(default="linear", description="Interpolation method")

class UpdateClipParams(BaseModel):
    """Parameters for update_clip_position tool - this will generate $ref with keywords"""
    clip_id: str = Field(..., description="ID of the clip to update")
    animation: Optional[ClipAnimation] = Field(
        default=None,
        description="Animation configuration for position/scale/rotation"
    )

def test_ref_with_keywords_error():
    """
    This test reproduces the exact error from production:
    "Invalid schema for function 'update_clip_position': 
     context=('properties', 'animation'), $ref cannot have keywords {'default', 'description'}."
    """
    
    print("="*80)
    print("TEST: Reproducing $ref cannot have keywords error")
    print("="*80)
    
    # Get the raw Pydantic schema - this will have $refs
    raw_schema = UpdateClipParams.model_json_schema()
    
    print("\n📋 Raw Pydantic Schema (with $refs):")
    import json
    print(json.dumps(raw_schema, indent=2))
    
    # Check if animation property has the problematic pattern
    animation_prop = raw_schema.get("properties", {}).get("animation", {})
    
    print("\n🔍 Animation property schema:")
    print(json.dumps(animation_prop, indent=2))
    
    has_ref = "$ref" in animation_prop or "anyOf" in animation_prop
    has_keywords = any(k in animation_prop for k in ["default", "description"])
    
    if has_ref and has_keywords:
        print("\n❌ PROBLEM DETECTED!")
        print("   Animation property has both $ref/anyOf AND keywords (default/description)")
        print("   This will cause: '$ref cannot have keywords' error")
        
        if "anyOf" in animation_prop:
            print("\n   anyOf content:")
            for item in animation_prop.get("anyOf", []):
                if "$ref" in item:
                    print(f"     - Has $ref: {item.get('$ref')}")
                    
        if "default" in animation_prop:
            print(f"   - Has 'default': {animation_prop['default']}")
        if "description" in animation_prop:
            print(f"   - Has 'description': {animation_prop['description']}")
    else:
        print("\n✓ No immediate $ref+keywords issue detected in raw schema")
    
    # Now try to use it with UltraGPT (this should fail with the 400 error)
    print("\n" + "="*80)
    print("Attempting to use this tool with UltraGPT...")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found - cannot test with real API")
        return
    
    try:
        ultragpt = UltraGPT(api_key=api_key, verbose=True)
        
        # Create a tool with this problematic schema - pass the raw schema dict
        tool_with_ref_issue = {
            "name": "update_clip_position",
            "description": "Update clip position with animation",
            "parameters_schema": raw_schema,  # Pass raw dict, not Pydantic model
            "usage_guide": "Use to update clip position",
            "when_to_use": "When user wants to animate a clip"
        }
        
        messages = [{"role": "user", "content": "Animate the clip to move from left to right"}]
        
        print("\n📤 Sending tool call request...")
        response, tokens, details = ultragpt.tool_call(
            messages=messages,
            user_tools=[tool_with_ref_issue],
            model="gpt-4o-mini",
            allow_multiple=False
        )
        
        print("\n✅ SUCCESS - Tool call completed without error!")
        print(f"Response: {response}")
        
    except Exception as e:
        error_msg = str(e)
        if "$ref cannot have keywords" in error_msg or "invalid_function_parameters" in error_msg:
            print("\n🎯 REPRODUCED THE ERROR!")
            print(f"Error: {error_msg}")
            return True
        else:
            print(f"\n❌ Different error occurred: {error_msg}")
            raise
    
    return False

if __name__ == "__main__":
    test_ref_with_keywords_error()
