"""
Additional comprehensive schema tests for OpenAI streaming with complex nested structures
Tests nested objects, lists, enums, optional fields, and deeply nested hierarchies
"""

import sys
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from src.ultragpt import UltraGPT

# Load environment variables
load_dotenv()

# Initialize
ultragpt = UltraGPT(
    api_key=os.getenv("OPENAI_API_KEY"),
    verbose=False
)

print("=" * 70)
print("COMPREHENSIVE SCHEMA STREAMING TESTS")
print("=" * 70)

# ============================================================
# TEST 1: Nested objects
# ============================================================
print("\n" + "=" * 70)
print("TEST 1: Nested Objects Schema")
print("=" * 70)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City name")
    country: str = Field(description="Country name")
    zip_code: str = Field(description="Postal code")

class Person(BaseModel):
    name: str = Field(description="Full name")
    age: int = Field(description="Age in years")
    address: Address = Field(description="Home address")
    email: str = Field(description="Email address")

messages = [
    {"role": "user", "content": "Create a person profile for John Doe, age 30, living at 123 Main St, New York, USA, 10001, email john@example.com"}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        schema=Person,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=500
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ TEST 1 [PASS] - Nested objects work!")
except Exception as e:
    print(f"❌ TEST 1 [FAIL]: {e}")
    sys.exit(1)

# ============================================================
# TEST 2: Lists of nested objects
# ============================================================
print("\n" + "=" * 70)
print("TEST 2: Lists of Nested Objects")
print("=" * 70)

class Product(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Price in USD")
    quantity: int = Field(description="Quantity in stock")

class ShoppingCart(BaseModel):
    user_id: str = Field(description="User identifier")
    items: List[Product] = Field(description="List of products in cart")
    total_cost: float = Field(description="Total cost in USD")

messages = [
    {"role": "user", "content": "Create a shopping cart for user 'user123' with 3 items: Apple ($2.5, qty 5), Banana ($1.2, qty 10), Orange ($3.0, qty 3). Calculate total."}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        schema=ShoppingCart,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=800
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ Items count: {len(response['items'])}")
    print(f"✅ TEST 2 [PASS] - Lists of nested objects work!")
except Exception as e:
    print(f"❌ TEST 2 [FAIL]: {e}")
    sys.exit(1)

# ============================================================
# TEST 3: Optional fields and enums
# ============================================================
print("\n" + "=" * 70)
print("TEST 3: Optional Fields and Enums")
print("=" * 70)

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Status(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(BaseModel):
    title: str = Field(description="Task title")
    description: str = Field(description="Task description")
    priority: Priority = Field(description="Task priority level")
    status: Status = Field(description="Current status")
    assignee: Optional[str] = Field(None, description="Person assigned (optional)")
    tags: Optional[List[str]] = Field(None, description="Optional tags")

messages = [
    {"role": "user", "content": "Create a task: 'Fix login bug', description 'Users cannot login with special characters', priority HIGH, status IN_PROGRESS, assignee 'Alice', tags ['bug', 'security']"}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        schema=Task,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=500
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ Priority: {response['priority']}")
    print(f"✅ Status: {response['status']}")
    print(f"✅ TEST 3 [PASS] - Enums and optional fields work!")
except Exception as e:
    print(f"❌ TEST 3 [FAIL]: {e}")
    sys.exit(1)

# ============================================================
# TEST 4: Deeply nested hierarchy
# ============================================================
print("\n" + "=" * 70)
print("TEST 4: Deeply Nested Hierarchy")
print("=" * 70)

class Metadata(BaseModel):
    created_by: str = Field(description="Creator name")
    created_at: str = Field(description="Creation timestamp")
    version: int = Field(description="Version number")

class Comment(BaseModel):
    author: str = Field(description="Comment author")
    text: str = Field(description="Comment text")
    timestamp: str = Field(description="Comment timestamp")

class Section(BaseModel):
    title: str = Field(description="Section title")
    content: str = Field(description="Section content")
    comments: List[Comment] = Field(description="List of comments")

class Article(BaseModel):
    title: str = Field(description="Article title")
    author: str = Field(description="Article author")
    sections: List[Section] = Field(description="List of sections")
    metadata: Metadata = Field(description="Article metadata")
    tags: List[str] = Field(description="Article tags")

messages = [
    {"role": "user", "content": """Create an article:
    Title: 'Introduction to AI', 
    Author: 'Dr. Smith',
    2 sections: 
      1. 'What is AI' with content 'AI is artificial intelligence', 1 comment by 'Bob': 'Great intro!' at '2024-01-01',
      2. 'Applications' with content 'AI is used everywhere', 1 comment by 'Alice': 'Very informative' at '2024-01-02',
    Metadata: created by 'Admin', at '2024-01-01 10:00', version 1,
    Tags: ['AI', 'Technology', 'Education']
    """}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        schema=Article,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=1500
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ Sections count: {len(response['sections'])}")
    print(f"✅ Comments in section 1: {len(response['sections'][0]['comments'])}")
    print(f"✅ TEST 4 [PASS] - Deeply nested hierarchy works!")
except Exception as e:
    print(f"❌ TEST 4 [FAIL]: {e}")
    sys.exit(1)

# ============================================================
# TEST 5: Complex mixed types
# ============================================================
print("\n" + "=" * 70)
print("TEST 5: Complex Mixed Types")
print("=" * 70)

class Coordinates(BaseModel):
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")

class Location(BaseModel):
    name: str = Field(description="Location name")
    coordinates: Coordinates = Field(description="GPS coordinates")

class WeatherCondition(str, Enum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"

class WeatherReport(BaseModel):
    location: Location = Field(description="Weather location")
    temperature: float = Field(description="Temperature in Celsius")
    condition: WeatherCondition = Field(description="Weather condition")
    humidity: int = Field(description="Humidity percentage")
    wind_speed: float = Field(description="Wind speed in km/h")
    forecast: List[str] = Field(description="3-day forecast")
    alerts: Optional[List[str]] = Field(None, description="Weather alerts")

messages = [
    {"role": "user", "content": """Create weather report:
    Location: 'New York' at coordinates 40.7128 N, -74.0060 W,
    Temperature: 22.5 C,
    Condition: SUNNY,
    Humidity: 65%,
    Wind speed: 15.5 km/h,
    Forecast: ['Sunny tomorrow', 'Cloudy day after', 'Rain expected'],
    Alerts: ['High UV index']
    """}
]

try:
    response, tokens, details = ultragpt.chat(
        messages=messages,
        schema=WeatherReport,
        model="openai:gpt-4o-mini",
        temperature=0.7,
        max_tokens=800
    )
    print(f"✅ Response: {response}")
    print(f"✅ Tokens: {tokens}")
    print(f"✅ Location: {response['location']['name']}")
    print(f"✅ Coordinates: {response['location']['coordinates']}")
    print(f"✅ Condition: {response['condition']}")
    print(f"✅ TEST 5 [PASS] - Complex mixed types work!")
except Exception as e:
    print(f"❌ TEST 5 [FAIL]: {e}")
    sys.exit(1)

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("🎉 ALL COMPREHENSIVE SCHEMA TESTS PASSED!")
print("=" * 70)
print("Summary:")
print("  1) Nested objects              ✅ [PASS]")
print("  2) Lists of nested objects     ✅ [PASS]")
print("  3) Enums and optional fields   ✅ [PASS]")
print("  4) Deeply nested hierarchy     ✅ [PASS]")
print("  5) Complex mixed types         ✅ [PASS]")
print("=" * 70)
print("Streaming with text_format handles all complex schemas correctly!")
print("=" * 70)
