#!/usr/bin/env python3
"""
Example: Using Curb Energy API with LLM Tool Calling

This example demonstrates how to integrate the Curb Energy API with LLMs
for conversational access to your energy data.

Usage:
    1. Start the Curb Energy API server:
       curb-server

    2. Run this script to see how LLMs can query your energy data:
       python llm_integration.py
"""

import json
import requests
from typing import Dict, Any, List


class CurbEnergyLLMTools:
    """
    Wrapper class that provides LLM-friendly tool calling interface
    for Curb Energy API
    """

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.tools = self._load_tool_schemas()

    def _load_tool_schemas(self) -> List[Dict[str, Any]]:
        """Load tool schemas from the API"""
        response = requests.get(f"{self.api_base_url}/llm/tools")
        response.raise_for_status()
        return response.json()["tools"]

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Get tool schemas in the format expected by LLMs

        Returns:
            List of tool definitions with name, description, and parameters
        """
        return self.tools

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call from an LLM

        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool

        Returns:
            Result from the API
        """
        # Map tool names to API endpoints
        endpoint_map = {
            "get_energy_profiles": ("GET", "/profiles", {}),
            "get_energy_devices": ("GET", "/devices", {}),
            "get_today_energy_usage": ("GET", f"/energy/today", parameters),
            "get_week_energy_usage": ("GET", f"/energy/week", parameters),
            "get_historical_energy_data": ("POST", "/energy/historical", parameters),
        }

        if tool_name not in endpoint_map:
            return {"error": f"Unknown tool: {tool_name}"}

        method, endpoint, params = endpoint_map[tool_name]
        url = f"{self.api_base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, json=params)

            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}


def example_anthropic_claude():
    """
    Example: Using with Anthropic Claude API

    This shows how to integrate with Claude's tool calling feature.
    You'll need to install: pip install anthropic
    """
    print("\n=== Example: Anthropic Claude Integration ===\n")

    tools = CurbEnergyLLMTools()

    print("Tool schemas that would be sent to Claude:")
    print(json.dumps(tools.get_tool_schemas(), indent=2))

    print("\n" + "="*60)
    print("\nExample conversation:")
    print("\nUser: What's my energy usage today?")
    print("\nClaude would:")
    print("1. Use get_energy_profiles tool to find your profile ID")
    print("2. Use get_today_energy_usage with that profile ID")
    print("3. Analyze the data and respond conversationally")

    # Simulate tool execution
    print("\n" + "="*60)
    print("\nSimulated tool execution:")

    # First, get profiles
    print("\n1. Calling get_energy_profiles...")
    result = tools.execute_tool("get_energy_profiles", {})
    print(f"Result: {json.dumps(result, indent=2)[:200]}...")

    # Note: In a real scenario, you'd extract the profile_id from the result
    # and use it in subsequent calls


def example_openai_gpt():
    """
    Example: Using with OpenAI GPT API

    This shows how to integrate with GPT's function calling feature.
    You'll need to install: pip install openai
    """
    print("\n=== Example: OpenAI GPT Integration ===\n")

    tools = CurbEnergyLLMTools()

    # Convert to OpenAI function format
    openai_functions = []
    for tool in tools.get_tool_schemas():
        openai_functions.append({
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        })

    print("Function definitions for OpenAI:")
    print(json.dumps(openai_functions, indent=2))

    print("\n" + "="*60)
    print("\nExample usage with OpenAI SDK:")
    print("""
    import openai

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "What's my energy usage today?"}
        ],
        functions=openai_functions,
        function_call="auto"
    )

    # GPT will decide which function to call
    if response.choices[0].message.get("function_call"):
        function_name = response.choices[0].message["function_call"]["name"]
        arguments = json.loads(response.choices[0].message["function_call"]["arguments"])

        # Execute the function
        result = tools.execute_tool(function_name, arguments)

        # Send result back to GPT for natural language response
        ...
    """)


def example_custom_llm():
    """
    Example: Using with any LLM via prompt engineering

    This shows how to use the API without native tool calling support
    """
    print("\n=== Example: Generic LLM Integration (Prompt Engineering) ===\n")

    tools = CurbEnergyLLMTools()

    # Create a system prompt with tool descriptions
    system_prompt = """You are an energy monitoring assistant with access to the following tools:

"""

    for tool in tools.get_tool_schemas():
        system_prompt += f"\nTool: {tool['name']}\n"
        system_prompt += f"Description: {tool['description']}\n"
        system_prompt += f"Parameters: {json.dumps(tool['parameters'], indent=2)}\n"

    system_prompt += """
To use a tool, respond with:
TOOL_CALL: <tool_name>
PARAMETERS: <json_parameters>
"""

    print("System prompt for LLMs without native tool calling:")
    print(system_prompt)

    print("\n" + "="*60)
    print("\nExample interaction:")
    print("\nUser: Show me my energy usage for the past week")
    print("\nLLM Response:")
    print("TOOL_CALL: get_week_energy_usage")
    print('PARAMETERS: {"profile_id": 12345, "unit": "w"}')

    print("\nYour code would then:")
    print("1. Parse the TOOL_CALL and PARAMETERS from LLM response")
    print("2. Execute tools.execute_tool('get_week_energy_usage', {...})")
    print("3. Send results back to LLM for interpretation")


def example_direct_api_usage():
    """
    Example: Direct API usage without LLM

    Shows how to use the API programmatically
    """
    print("\n=== Example: Direct API Usage ===\n")

    tools = CurbEnergyLLMTools()

    print("1. Get all profiles:")
    profiles = tools.execute_tool("get_energy_profiles", {})
    print(json.dumps(profiles, indent=2)[:300] + "...")

    print("\n2. Get devices:")
    devices = tools.execute_tool("get_energy_devices", {})
    print(json.dumps(devices, indent=2)[:300] + "...")

    print("\n3. Get today's energy (requires profile_id):")
    print("   tools.execute_tool('get_today_energy_usage', {'profile_id': 12345})")

    print("\n4. Get historical data:")
    print("   tools.execute_tool('get_historical_energy_data', {")
    print("       'profile_id': 12345,")
    print("       'hours_back': 48,")
    print("       'granularity': '1H',")
    print("       'unit': 'w'")
    print("   })")


def main():
    """Main function demonstrating various integration patterns"""
    print("="*60)
    print("Curb Energy API - LLM Integration Examples")
    print("="*60)

    print("\nThis script demonstrates different ways to integrate")
    print("the Curb Energy API with LLMs and other applications.")

    print("\n" + "="*60)

    # Run examples
    try:
        example_anthropic_claude()
        example_openai_gpt()
        example_custom_llm()
        example_direct_api_usage()

        print("\n" + "="*60)
        print("\n✅ Examples completed!")
        print("\nNext steps:")
        print("1. Start your Curb Energy API server: curb-server")
        print("2. Configure authentication (see README)")
        print("3. Try these integrations with your preferred LLM")
        print("4. Check out the dashboard: http://localhost:8000")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the Curb Energy API server is running:")
        print("  curb-server")


if __name__ == "__main__":
    main()
