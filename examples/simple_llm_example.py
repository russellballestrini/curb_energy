#!/usr/bin/env python3
"""
Simple example showing how LLM tool calling works with the Curb Energy API

This demonstrates the flow:
User → LLM → Function Call → HTTP API → Response → LLM → User
"""

import json
import requests

# ============================================================================
# PART 1: The Tool Schema (What the LLM sees)
# ============================================================================

print("=" * 70)
print("PART 1: What the LLM Sees (Tool Schema)")
print("=" * 70)

# This is what you send to the LLM
tool_schema = {
    "name": "get_today_energy_usage",
    "description": "Get today's energy usage for a specific profile",
    "parameters": {
        "type": "object",
        "properties": {
            "profile_id": {
                "type": "integer",
                "description": "The profile ID to query"
            },
            "unit": {
                "type": "string",
                "enum": ["w", "$/hr"],
                "description": "Unit: 'w' for watts or '$/hr' for dollars per hour"
            }
        },
        "required": ["profile_id"]
    }
}

print("\nTool schema sent to LLM:")
print(json.dumps(tool_schema, indent=2))

print("\n📝 The LLM reads this and understands:")
print("   - There's a function called 'get_today_energy_usage'")
print("   - It needs a profile_id (integer)")
print("   - It can optionally take a unit (w or $/hr)")
print("   - It will get today's energy usage")

# ============================================================================
# PART 2: What the LLM Returns (Function Call)
# ============================================================================

print("\n" + "=" * 70)
print("PART 2: What the LLM Returns (Function Call)")
print("=" * 70)

# User says: "What's my energy usage today?"
# LLM decides to call the function and returns this:

llm_function_call = {
    "function": "get_today_energy_usage",
    "parameters": {
        "profile_id": 12345,
        "unit": "w"
    }
}

print("\nUser asked: 'What's my energy usage today?'")
print("\nLLM returns this function call:")
print(json.dumps(llm_function_call, indent=2))

# ============================================================================
# PART 3: Your Code Translates to HTTP
# ============================================================================

print("\n" + "=" * 70)
print("PART 3: Your Code Translates Function Call → HTTP Request")
print("=" * 70)

def execute_llm_function_call(function_name, parameters):
    """
    This is your middleware that translates LLM function calls
    into HTTP API requests
    """

    # Map function names to API endpoints
    function_to_endpoint = {
        "get_energy_profiles": {
            "method": "GET",
            "url": "/profiles",
            "params_in": "none"
        },
        "get_today_energy_usage": {
            "method": "GET",
            "url": "/energy/today",
            "params_in": "query"
        },
        "get_historical_energy_data": {
            "method": "POST",
            "url": "/energy/historical",
            "params_in": "body"
        }
    }

    endpoint_info = function_to_endpoint.get(function_name)
    if not endpoint_info:
        return {"error": f"Unknown function: {function_name}"}

    api_base = "http://localhost:8000"
    url = f"{api_base}{endpoint_info['url']}"
    method = endpoint_info["method"]

    print(f"\n🔄 Translating function call to HTTP:")
    print(f"   Function: {function_name}")
    print(f"   Parameters: {parameters}")
    print(f"   ↓")
    print(f"   HTTP Method: {method}")
    print(f"   URL: {url}")

    if endpoint_info["params_in"] == "query":
        print(f"   Query params: {parameters}")
        print(f"   Full URL: {url}?profile_id={parameters.get('profile_id')}&unit={parameters.get('unit')}")
        # return requests.get(url, params=parameters)
    elif endpoint_info["params_in"] == "body":
        print(f"   JSON body: {json.dumps(parameters)}")
        # return requests.post(url, json=parameters)
    else:
        print(f"   No parameters")
        # return requests.get(url)

    return {"status": "simulated - server not running"}


# Execute the LLM's function call
result = execute_llm_function_call(
    llm_function_call["function"],
    llm_function_call["parameters"]
)

# ============================================================================
# PART 4: The OpenAPI Schema (Behind the Scenes)
# ============================================================================

print("\n" + "=" * 70)
print("PART 4: OpenAPI Schema (Behind the Scenes)")
print("=" * 70)

# FastAPI automatically generated this OpenAPI schema
openapi_schema = {
    "paths": {
        "/energy/today": {
            "get": {
                "summary": "Get Today Energy",
                "parameters": [
                    {
                        "name": "profile_id",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "integer"}
                    },
                    {
                        "name": "unit",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string", "default": "w"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    }
}

print("\nOpenAPI schema for GET /energy/today:")
print(json.dumps(openapi_schema, indent=2))

print("\n📋 This OpenAPI schema:")
print("   - Validates that profile_id is an integer")
print("   - Validates that unit is a string")
print("   - Ensures the response is valid JSON")
print("   - Generates the Swagger UI documentation")

# ============================================================================
# PART 5: The Full Flow
# ============================================================================

print("\n" + "=" * 70)
print("PART 5: The Complete Flow")
print("=" * 70)

print("""
1. 👤 USER ASKS:
   "What's my energy usage today?"

2. 🤖 LLM SEES TOOL SCHEMA:
   {
     "name": "get_today_energy_usage",
     "parameters": {"profile_id": int, "unit": str}
   }

3. 🤖 LLM DECIDES:
   "I should call get_today_energy_usage with profile_id"

4. 🤖 LLM RETURNS:
   {
     "function": "get_today_energy_usage",
     "parameters": {"profile_id": 12345, "unit": "w"}
   }

5. 🔧 YOUR CODE TRANSLATES:
   Function call → HTTP GET request
   GET http://localhost:8000/energy/today?profile_id=12345&unit=w

6. 📡 API RECEIVES REQUEST:
   OpenAPI validates parameters
   FastAPI routes to endpoint
   Python function executes

7. 📊 API RETURNS DATA:
   {
     "profile_id": 12345,
     "date": "2025-11-10",
     "unit": "w",
     "data": {...energy measurements...}
   }

8. 🔧 YOUR CODE SENDS TO LLM:
   Here's the data: {...}

9. 🤖 LLM PROCESSES DATA:
   Analyzes the measurements
   Formats into natural language

10. 👤 USER RECEIVES ANSWER:
    "Today you've used 15 kWh so far. Your usage has been around
    900 watts on average, with a peak of 1,200 watts at noon."
""")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("SUMMARY: Two Schemas, Different Purposes")
print("=" * 70)

print("""
┌─────────────────────────────────────────────────────────────────┐
│                      LLM TOOL SCHEMA                            │
│  Location: GET /llm/tools                                       │
│  Purpose: Tell LLMs what functions they can call               │
│  Format: Simplified, function-oriented                         │
│  Example: "get_today_energy_usage(profile_id=123)"            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    (LLM makes function call)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    YOUR MIDDLEWARE CODE                         │
│  Translates: Function calls → HTTP requests                    │
│  Example: get_today_energy_usage() → GET /energy/today         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                     (HTTP GET request)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      OPENAPI SCHEMA                             │
│  Location: GET /openapi.json                                    │
│  Purpose: Define HTTP API structure & validate requests        │
│  Format: Technical, HTTP-oriented                              │
│  Example: "GET /energy/today?profile_id=123"                  │
└─────────────────────────────────────────────────────────────────┘

KEY POINTS:
✓ LLM schema is AI-friendly (functions, not HTTP)
✓ OpenAPI schema is for HTTP validation & docs
✓ Your middleware bridges the two worlds
✓ LLM never needs to know about HTTP details
✓ Users get natural language answers about their energy data
""")

print("\n" + "=" * 70)
print("To see this in action:")
print("  1. Start the server: curb-server")
print("  2. View tool schemas: curl http://localhost:8000/llm/tools")
print("  3. View OpenAPI schema: curl http://localhost:8000/openapi.json")
print("  4. Use with LLM: python examples/llm_integration.py")
print("=" * 70)
