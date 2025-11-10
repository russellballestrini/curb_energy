# Schema Comparison: OpenAPI vs LLM Tool Calling

This document shows the difference between the two schemas and how they work together.

## Scenario: Get Today's Energy Usage

Let's compare how the same functionality is described in both schemas.

---

## 1. OpenAPI Schema (FastAPI Auto-generates)

**Endpoint:** `GET /energy/today?profile_id={id}&unit={unit}`

**OpenAPI Description:**
```json
{
  "openapi": "3.1.0",
  "paths": {
    "/energy/today": {
      "get": {
        "summary": "Get Today Energy",
        "description": "Get today's energy usage for a profile.\nConvenient shortcut for common queries.",
        "operationId": "get_today_energy_energy_today_get",
        "parameters": [
          {
            "name": "profile_id",
            "in": "query",
            "required": true,
            "schema": {
              "type": "integer",
              "title": "Profile Id",
              "description": "Profile ID to query"
            }
          },
          {
            "name": "unit",
            "in": "query",
            "required": false,
            "schema": {
              "type": "string",
              "default": "w",
              "title": "Unit",
              "description": "Unit: w (watts) or $/hr"
            }
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "profile_id": {"type": "integer"},
                    "date": {"type": "string"},
                    "unit": {"type": "string"},
                    "data": {"type": "object"}
                  }
                }
              }
            }
          },
          "422": {
            "description": "Validation Error"
          }
        }
      }
    }
  }
}
```

**What this tells you:**
- There's a GET endpoint at `/energy/today`
- It takes query parameters: `profile_id` (required) and `unit` (optional)
- It returns a 200 status with JSON data
- The parameters go in the URL query string
- You need to make an HTTP GET request

---

## 2. LLM Tool Schema (Custom endpoint: /llm/tools)

**Function:** `get_today_energy_usage`

**LLM Tool Description:**
```json
{
  "name": "get_today_energy_usage",
  "description": "Get today's energy usage for a specific profile. Returns hourly data from midnight until now.",
  "parameters": {
    "type": "object",
    "properties": {
      "profile_id": {
        "type": "integer",
        "description": "The profile ID to query (get from get_energy_profiles)"
      },
      "unit": {
        "type": "string",
        "enum": ["w", "$/hr"],
        "description": "Unit of measurement: 'w' for watts or '$/hr' for dollars per hour",
        "default": "w"
      }
    },
    "required": ["profile_id"]
  }
}
```

**What this tells the LLM:**
- There's a function called `get_today_energy_usage`
- It gets today's energy data (plain language description)
- It needs a `profile_id` (which you can get from `get_energy_profiles`)
- You can optionally specify the unit
- No HTTP details - just "call this function with these parameters"

---

## How They Work Together

### Example Conversation

**User says:** "How much electricity did I use today?"

### Step 1: LLM Reads Tool Schema

The LLM sees:
```json
{
  "name": "get_today_energy_usage",
  "description": "Get today's energy usage...",
  "parameters": { "profile_id": ... }
}
```

LLM thinks: "I need a profile_id first, let me call get_energy_profiles"

### Step 2: LLM Calls First Function

```json
{
  "tool_use": {
    "name": "get_energy_profiles",
    "parameters": {}
  }
}
```

### Step 3: Your Code Translates to HTTP

Your middleware sees the function call and maps it:

```python
# Function call from LLM
function_name = "get_energy_profiles"
parameters = {}

# Your code translates this to:
url = "http://localhost:8000/profiles"
response = requests.get(url)
```

### Step 4: API Returns Data (Using OpenAPI spec for validation)

```json
[
  {
    "id": 12345,
    "name": "My Home",
    "timezone": "America/New_York"
  }
]
```

### Step 5: LLM Calls Second Function

Now the LLM has a profile_id, it calls:

```json
{
  "tool_use": {
    "name": "get_today_energy_usage",
    "parameters": {
      "profile_id": 12345,
      "unit": "w"
    }
  }
}
```

### Step 6: Your Code Translates Again

```python
# Function call from LLM
function_name = "get_today_energy_usage"
parameters = {"profile_id": 12345, "unit": "w"}

# Your code translates this to:
url = "http://localhost:8000/energy/today"
params = {"profile_id": 12345, "unit": "w"}
response = requests.get(url, params=params)
```

### Step 7: API Returns Energy Data

```json
{
  "profile_id": 12345,
  "date": "2025-11-10",
  "unit": "w",
  "data": {
    "measurements": [
      {"timestamp": 1699574400, "value": 850},
      {"timestamp": 1699578000, "value": 920},
      ...
    ]
  }
}
```

### Step 8: LLM Responds to User

"Today at your home, you've used about 15 kWh so far. Your usage has been steady around 900 watts, with a peak of 1,200 watts during lunchtime."

---

## Code Example: The Translation Layer

Here's how the `examples/llm_integration.py` translates function calls to HTTP:

```python
class CurbEnergyLLMTools:
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]):
        """Translate LLM function call to HTTP request"""

        # Map function names to HTTP endpoints
        endpoint_map = {
            "get_energy_profiles": ("GET", "/profiles", {}),
            "get_energy_devices": ("GET", "/devices", {}),
            "get_today_energy_usage": ("GET", "/energy/today", parameters),
            "get_week_energy_usage": ("GET", "/energy/week", parameters),
            "get_historical_energy_data": ("POST", "/energy/historical", parameters),
        }

        method, endpoint, params = endpoint_map[tool_name]
        url = f"{self.api_base_url}{endpoint}"

        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, json=params)

        return response.json()
```

---

## Quick Reference Table

| Aspect | OpenAPI Schema | LLM Tool Schema |
|--------|----------------|-----------------|
| **Purpose** | Describe HTTP API | Describe functions for AI |
| **Audience** | Developers, API clients | LLMs, AI agents |
| **Language** | Technical HTTP details | Plain English |
| **Focus** | How to make requests | What tasks to accomplish |
| **Format** | OpenAPI 3.0/3.1 | JSON Schema (simplified) |
| **Location** | `/openapi.json` | `/llm/tools` |
| **Contains** | Endpoints, methods, responses | Functions, parameters, descriptions |
| **Used by** | Swagger UI, API tools | Claude, GPT-4, LLMs |
| **Example** | `GET /energy/today?profile_id=123` | `get_today_energy_usage(profile_id=123)` |

---

## Why Both?

**OpenAPI is for machines and developers:**
- Generates API documentation
- Validates requests/responses
- Creates client libraries
- Tests API endpoints

**LLM Tool Schema is for AI:**
- Easier for LLMs to understand
- Function-oriented (not HTTP-oriented)
- Task-focused descriptions
- Guides LLM decision-making

**Together they enable:**
- LLM understands *what functions exist*
- Your code translates *function calls to HTTP*
- OpenAPI validates *HTTP requests work correctly*
- User gets natural language responses

---

## Try It Yourself

1. **Start the server:**
   ```bash
   curb-server
   ```

2. **View OpenAPI schema:**
   ```bash
   curl http://localhost:8000/openapi.json | jq
   ```

3. **View LLM tool schema:**
   ```bash
   curl http://localhost:8000/llm/tools | jq
   ```

4. **Compare them!**

5. **Use the LLM integration example:**
   ```bash
   python examples/llm_integration.py
   ```

---

## Bottom Line

- **OpenAPI** = "Here's my REST API with all the HTTP details"
- **LLM Tools** = "Here are functions you can call to help users"
- **Your middleware** = Translates between function calls and HTTP requests
- **The LLM never needs to know about HTTP** - it just calls functions!

This makes it much easier for LLMs to use your API because they think in terms of "functions to call" not "HTTP requests to make".
