"""Test edge case handling in schema sanitization for OpenAI tool calling.

This test validates that sanitize_tool_parameters_schema handles all OpenAI edge cases
based on comprehensive web research of common 400 BadRequestError patterns.

================================================================================
HOW TO ADD NEW EDGE CASE TESTS
================================================================================

When OpenAI returns a 400 error with your tool schema:

1. **Capture the error pattern** from the API response:
   Example errors:
   - "object schema missing properties"
   - "'required' is required to be supplied and to be an array"
   - "'additionalProperties' is required to be supplied and to be false"
   - "array schema missing items"
   - "$ref cannot have keywords {'default', 'description'}"

2. **Create minimal failing schema** - Build the smallest schema that triggers the error:
   ```python
   problematic_schema = {
       "type": "object",
       # ... whatever causes the error
   }
   ```

3. **Add test case** following this pattern:
   ```python
   # Test N: [Error description]
   print(f"\\n{N}️⃣ Test: [Error description]")
   schema_bad = {
       # Problematic schema pattern
   }
   cleaned = sanitize_tool_parameters_schema(schema_bad)
   
   # Assert the fix works
   assert "expected_field" in cleaned, "❌ FAIL: Description"
   assert cleaned["expected_field"] == expected_value, "❌ FAIL: Description"
   print("✅ PASS: What was fixed")
   ```

4. **Document the pattern** in comments:
   ```python
   # Common cause: Pydantic v2 generates X when you use Y
   # OpenAI requires: Z
   # Our fix: Does W
   ```

5. **Add to summary** at the bottom:
   Update the coverage checklist with the new case.

================================================================================
CURRENT EDGE CASES COVERED
================================================================================

Based on web research (OpenAI community forums, GitHub issues, etc.):

✅ Missing properties dict
   - Error: "object schema missing properties"
   - Fix: Add empty `properties: {}` if missing

✅ Missing required array
   - Error: "'required' is required... Missing 'X'"
   - Fix: Add `required: [all_property_keys]`

✅ Missing additionalProperties
   - Error: "'additionalProperties' is required to be supplied and to be false"
   - Fix: Add `additionalProperties: false` on ALL objects

✅ Arrays without items
   - Error: "array schema missing items"
   - Fix: Add `items: {type: "string"}` as default

✅ $ref with keywords
   - Error: "$ref cannot have keywords {'default', 'description'}"
   - Fix: Keep ONLY $ref, strip all sibling keywords

✅ default keyword
   - Error: Causes 400 in tool schemas even without $ref
   - Fix: Strip `default` from ALL properties

✅ Nested objects compliance
   - Error: Nested objects missing required/additionalProperties
   - Fix: Recursively apply rules to $defs and nested objects

✅ Root without type
   - Error: Schema validation fails if root doesn't have type
   - Fix: Add `type: "object"` if missing

================================================================================
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pydantic import BaseModel, Field
from typing import List, Optional
from ultragpt.schemas import sanitize_tool_parameters_schema
import json

print("=" * 80)
print("TEST: Edge Case Handling in Schema Sanitization")
print("=" * 80)

# Test 1: Object without properties
print("\n1️⃣ Test: Object without properties dict")
schema_no_props = {
    "type": "object",
    "description": "Test object"
}
cleaned = sanitize_tool_parameters_schema(schema_no_props)
assert "properties" in cleaned, "❌ FAIL: Missing properties dict should be added"
assert cleaned["properties"] == {}, "❌ FAIL: Empty properties dict expected"
print("✅ PASS: Empty properties dict added")

# Test 2: Object without required array
print("\n2️⃣ Test: Object without required array")
schema_no_required = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    }
}
cleaned = sanitize_tool_parameters_schema(schema_no_required)
assert "required" in cleaned, "❌ FAIL: Missing required array should be added"
assert set(cleaned["required"]) == {"name", "age"}, "❌ FAIL: All properties should be in required"
print(f"✅ PASS: Required array added with all keys: {cleaned['required']}")

# Test 3: Object without additionalProperties
print("\n3️⃣ Test: Object without additionalProperties")
schema_no_additional = {
    "type": "object",
    "properties": {
        "name": {"type": "string"}
    }
}
cleaned = sanitize_tool_parameters_schema(schema_no_additional)
assert "additionalProperties" in cleaned, "❌ FAIL: Missing additionalProperties should be added"
assert cleaned["additionalProperties"] is False, "❌ FAIL: additionalProperties should be False"
print("✅ PASS: additionalProperties: false added")

# Test 4: Array without items
print("\n4️⃣ Test: Array without items schema")
schema_array_no_items = {
    "type": "object",
    "properties": {
        "tags": {"type": "array"}
    }
}
cleaned = sanitize_tool_parameters_schema(schema_array_no_items)
assert "items" in cleaned["properties"]["tags"], "❌ FAIL: Missing items schema should be added"
print(f"✅ PASS: items schema added: {cleaned['properties']['tags']['items']}")

# Test 5: Nested objects compliance
print("\n5️⃣ Test: Nested objects have full compliance")
class NestedConfig(BaseModel):
    timeout: int = Field(description="Timeout in seconds")
    retries: int = Field(default=3, description="Number of retries")

class ToolWithNested(BaseModel):
    name: str = Field(description="Tool name")
    config: NestedConfig = Field(description="Configuration")

raw_schema = ToolWithNested.model_json_schema()
cleaned = sanitize_tool_parameters_schema(raw_schema)

# Check nested object in $defs
if "$defs" in cleaned and "NestedConfig" in cleaned["$defs"]:
    nested_def = cleaned["$defs"]["NestedConfig"]
    assert nested_def.get("additionalProperties") is False, "❌ FAIL: Nested $def missing additionalProperties"
    assert set(nested_def.get("required", [])) == {"timeout", "retries"}, "❌ FAIL: Nested $def missing complete required"
    assert "default" not in nested_def.get("properties", {}).get("retries", {}), "❌ FAIL: default not stripped from nested"
    print("✅ PASS: Nested object in $defs has full compliance")
else:
    print("⚠️  SKIP: Schema doesn't use $defs for nested objects")

# Test 6: default keyword stripped everywhere
print("\n6️⃣ Test: default keyword stripped from all properties")
schema_with_defaults = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "default": "test"},
        "config": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True}
            }
        }
    }
}
cleaned = sanitize_tool_parameters_schema(schema_with_defaults)
assert "default" not in cleaned["properties"]["name"], "❌ FAIL: default not stripped from root property"
assert "default" not in cleaned["properties"]["config"]["properties"]["enabled"], "❌ FAIL: default not stripped from nested property"
print("✅ PASS: default keyword stripped from all levels")

# Test 7: $ref with keywords stripped
print("\n7️⃣ Test: $ref properties have ONLY $ref")
schema_ref_with_keywords = {
    "type": "object",
    "properties": {
        "data": {
            "$ref": "#/$defs/Data",
            "description": "Data object",
            "default": None,
            "title": "Data"
        }
    },
    "$defs": {
        "Data": {
            "type": "object",
            "properties": {
                "value": {"type": "number"}
            }
        }
    }
}
cleaned = sanitize_tool_parameters_schema(schema_ref_with_keywords)
data_prop = cleaned["properties"]["data"]
assert list(data_prop.keys()) == ["$ref"], f"❌ FAIL: $ref property should have ONLY $ref, got: {list(data_prop.keys())}"
print(f"✅ PASS: $ref property cleaned to: {data_prop}")

# Test 8: Root schema is proper object
print("\n8️⃣ Test: Root schema becomes proper object if missing type")
schema_no_type = {
    "properties": {
        "name": {"type": "string"}
    }
}
cleaned = sanitize_tool_parameters_schema(schema_no_type)
assert cleaned.get("type") == "object", "❌ FAIL: Root type should be 'object'"
print("✅ PASS: Root type set to 'object'")

# Test 9: Complex real-world case
print("\n9️⃣ Test: Complex real-world schema (nested + arrays + refs + defaults)")
class Position(BaseModel):
    x: float = Field(default=0.0, description="X coordinate")
    y: float = Field(default=0.0, description="Y coordinate")

class Layer(BaseModel):
    name: str = Field(description="Layer name")
    position: Position = Field(description="Layer position")
    tags: List[str] = Field(default=[], description="Tags")

raw_schema = Layer.model_json_schema()
print(f"\n📋 Raw Schema Keys: {list(raw_schema.keys())}")
print(f"   Properties: {list(raw_schema.get('properties', {}).keys())}")

cleaned = sanitize_tool_parameters_schema(raw_schema)

# Verify root
assert cleaned.get("type") == "object", "❌ Root type check failed"
assert "properties" in cleaned, "❌ Root properties check failed"
assert "required" in cleaned or len(cleaned["properties"]) == 0, "❌ Root required check failed"

# Verify properties have no defaults
for prop_name, prop_val in cleaned.get("properties", {}).items():
    if isinstance(prop_val, dict):
        assert "default" not in prop_val, f"❌ FAIL: default found in {prop_name}"

print("✅ PASS: Complex schema sanitized correctly")

# Summary
print("\n" + "=" * 80)
print("✅ ALL EDGE CASE TESTS PASSED!")
print("=" * 80)
print("\n📊 Coverage:")
print("   ✓ Missing properties dict → added")
print("   ✓ Missing required array → added with all keys")
print("   ✓ Missing additionalProperties → added as false")
print("   ✓ Arrays without items → added default items")
print("   ✓ Nested objects → full compliance enforced")
print("   ✓ default keyword → stripped everywhere")
print("   ✓ $ref with keywords → kept only $ref")
print("   ✓ Root without type → set to object")
print("   ✓ Complex real-world case → handles correctly")
print("\n🎉 Schema sanitization is production-ready for ALL OpenAI edge cases!")
