"""
FastAPI server for exposing Curb Energy data as a REST API with LLM tool calling support
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

try:
    from fastapi import FastAPI, HTTPException, Depends, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, HTMLResponse
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    raise ImportError(
        "FastAPI dependencies not installed. "
        "Install with: pip install 'curb_energy[server]'"
    )

from curb_energy.client import RestApiClient, AuthToken
from curb_energy import models

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class AuthConfig(BaseModel):
    """Authentication configuration for Curb API"""
    username: str = Field(..., description="Curb account username")
    password: str = Field(..., description="Curb account password")
    client_token: str = Field(..., description="OAuth client token")
    client_secret: str = Field(..., description="OAuth client secret")


class EnergyDataRequest(BaseModel):
    """Request model for historical energy data"""
    profile_id: int = Field(..., description="Profile ID to query")
    granularity: str = Field(
        default="1H",
        description="Data granularity: 1T (per minute), 1H (per hour), 1D (per day)"
    )
    unit: str = Field(
        default="w",
        description="Unit of measurement: w (watts) or $/hr (dollars per hour)"
    )
    hours_back: int = Field(
        default=24,
        description="Number of hours of historical data to retrieve"
    )


class ProfileResponse(BaseModel):
    """Response model for profile information"""
    id: int
    name: str
    timezone: Optional[str] = None
    location: Optional[str] = None


class DeviceResponse(BaseModel):
    """Response model for device information"""
    id: str
    label: Optional[str] = None
    profile_id: Optional[int] = None


class MeasurementResponse(BaseModel):
    """Response model for energy measurements"""
    timestamp: int
    values: Dict[str, float]
    unit: str
    granularity: str


# Global client instance
_client: Optional[RestApiClient] = None
_auth_config: Optional[AuthConfig] = None


def get_client() -> RestApiClient:
    """Dependency to get or create the API client"""
    global _client, _auth_config

    if _client is None:
        if _auth_config is None:
            # Try to get from environment variables
            username = os.getenv("CURB_USERNAME")
            password = os.getenv("CURB_PASSWORD")
            client_token = os.getenv("CURB_CLIENT_TOKEN")
            client_secret = os.getenv("CURB_CLIENT_SECRET")

            if not all([username, password, client_token, client_secret]):
                raise HTTPException(
                    status_code=401,
                    detail="Authentication not configured. Use /auth/configure or set environment variables."
                )

            _auth_config = AuthConfig(
                username=username,
                password=password,
                client_token=client_token,
                client_secret=client_secret
            )

        _client = RestApiClient(
            username=_auth_config.username,
            password=_auth_config.password,
            client_token=_auth_config.client_token,
            client_secret=_auth_config.client_secret
        )

    return _client


# Create FastAPI app
app = FastAPI(
    title="Curb Energy API Server",
    description="REST API server for Curb Energy monitoring data with LLM tool calling support",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for web embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with dashboard"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Curb Energy Dashboard</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .endpoint {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #61affe; color: white; }
            .post { background: #49cc90; color: white; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            a {
                color: #667eea;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>⚡ Curb Energy API Server</h1>
            <p>Modern REST API for your energy monitoring data</p>
        </div>

        <div class="card">
            <h2>🚀 Quick Start</h2>
            <p>This server exposes your Curb energy data through a RESTful API that can be:</p>
            <ul>
                <li>📊 Used to build custom dashboards and visualizations</li>
                <li>🤖 Queried by LLMs for conversational energy insights</li>
                <li>🔗 Integrated into your own applications</li>
                <li>📈 Used for analytics and monitoring</li>
            </ul>
        </div>

        <div class="card">
            <h2>📚 API Documentation</h2>
            <p>
                <a href="/docs">📖 Interactive API Docs (Swagger UI)</a> -
                Try out the API directly in your browser
            </p>
            <p>
                <a href="/redoc">📘 API Reference (ReDoc)</a> -
                Clean, readable API documentation
            </p>
            <p>
                <a href="/openapi.json">🔧 OpenAPI Schema</a> -
                For LLM tool calling and code generation
            </p>
        </div>

        <div class="card">
            <h2>🔌 API Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/profiles</code>
                    <p>Get all energy profiles associated with your account</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/devices</code>
                    <p>Get all monitoring devices on your account</p>
                </div>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/energy/historical</code>
                    <p>Get historical energy data with flexible time ranges</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/energy/today</code>
                    <p>Quick access to today's energy usage</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/energy/week</code>
                    <p>Get the past week's energy data</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/llm/tools</code>
                    <p>LLM-friendly function schemas for tool calling</p>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🤖 LLM Integration</h2>
            <p>This API is designed to work seamlessly with LLMs. Example prompts:</p>
            <ul>
                <li>"What's my energy usage today?"</li>
                <li>"Show me my electricity consumption for the past week"</li>
                <li>"Which devices are using the most power?"</li>
                <li>"How much money am I spending on electricity this month?"</li>
            </ul>
            <p>Get the tool schemas at <a href="/llm/tools">/llm/tools</a></p>
        </div>

        <div class="card">
            <h2>🔐 Authentication</h2>
            <p>Configure authentication using environment variables:</p>
            <code style="display: block; padding: 10px; margin: 10px 0;">
                export CURB_USERNAME="your_username"<br>
                export CURB_PASSWORD="your_password"<br>
                export CURB_CLIENT_TOKEN="your_client_token"<br>
                export CURB_CLIENT_SECRET="your_client_secret"
            </code>
            <p>Or use the <code>POST /auth/configure</code> endpoint</p>
        </div>
    </body>
    </html>
    """


@app.post("/auth/configure")
async def configure_auth(config: AuthConfig):
    """Configure authentication credentials"""
    global _auth_config, _client

    _auth_config = config
    _client = None  # Reset client to force recreation with new credentials

    return {"status": "configured", "message": "Authentication configured successfully"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "curb-energy-api"}


@app.get("/profiles", response_model=List[ProfileResponse])
async def get_profiles(client: RestApiClient = Depends(get_client)):
    """
    Get all energy profiles associated with the authenticated user.

    A profile represents a location or property with energy monitoring.
    """
    try:
        async with client:
            profiles = await client.profiles()
            return [
                ProfileResponse(
                    id=p.id,
                    name=p.label if hasattr(p, 'label') else f"Profile {p.id}",
                    timezone=p.timezone if hasattr(p, 'timezone') else None,
                    location=p.location if hasattr(p, 'location') else None
                )
                for p in profiles
            ]
    except Exception as e:
        logger.error(f"Error fetching profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/devices", response_model=List[DeviceResponse])
async def get_devices(client: RestApiClient = Depends(get_client)):
    """
    Get all monitoring devices associated with the authenticated user.

    Devices are the physical Curb energy monitors installed at your properties.
    """
    try:
        async with client:
            devices = await client.devices()
            return [
                DeviceResponse(
                    id=str(d.id) if hasattr(d, 'id') else "unknown",
                    label=d.label if hasattr(d, 'label') else None,
                    profile_id=d.profile_id if hasattr(d, 'profile_id') else None
                )
                for d in devices
            ]
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/energy/historical")
async def get_historical_data(
    request: EnergyDataRequest,
    client: RestApiClient = Depends(get_client)
):
    """
    Get historical energy data for a specific profile.

    Parameters:
    - profile_id: The profile to query
    - granularity: 1T (per minute), 1H (per hour), or 1D (per day)
    - unit: w (watts) or $/hr (dollars per hour)
    - hours_back: Number of hours of historical data
    """
    try:
        # Calculate time range
        until = int(datetime.now().timestamp())
        since = int((datetime.now() - timedelta(hours=request.hours_back)).timestamp())

        async with client:
            data = await client.historical_data(
                profile_id=request.profile_id,
                granularity=request.granularity,
                unit=request.unit,
                since=since,
                until=until
            )

            return {
                "profile_id": request.profile_id,
                "granularity": request.granularity,
                "unit": request.unit,
                "since": since,
                "until": until,
                "data": data
            }
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/energy/today")
async def get_today_energy(
    profile_id: int = Query(..., description="Profile ID to query"),
    unit: str = Query(default="w", description="Unit: w (watts) or $/hr"),
    client: RestApiClient = Depends(get_client)
):
    """
    Get today's energy usage for a profile.
    Convenient shortcut for common queries.
    """
    try:
        # Get data from midnight today
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        since = int(midnight.timestamp())
        until = int(now.timestamp())

        async with client:
            data = await client.historical_data(
                profile_id=profile_id,
                granularity="1H",
                unit=unit,
                since=since,
                until=until
            )

            return {
                "profile_id": profile_id,
                "date": now.strftime("%Y-%m-%d"),
                "unit": unit,
                "data": data
            }
    except Exception as e:
        logger.error(f"Error fetching today's data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/energy/week")
async def get_week_energy(
    profile_id: int = Query(..., description="Profile ID to query"),
    unit: str = Query(default="w", description="Unit: w (watts) or $/hr"),
    client: RestApiClient = Depends(get_client)
):
    """
    Get the past week's energy usage for a profile.
    Convenient shortcut for common queries.
    """
    try:
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        since = int(week_ago.timestamp())
        until = int(now.timestamp())

        async with client:
            data = await client.historical_data(
                profile_id=profile_id,
                granularity="1H",
                unit=unit,
                since=since,
                until=until
            )

            return {
                "profile_id": profile_id,
                "period": "past_week",
                "since": since,
                "until": until,
                "unit": unit,
                "data": data
            }
    except Exception as e:
        logger.error(f"Error fetching week data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/llm/tools")
async def get_llm_tools():
    """
    Get LLM-friendly function schemas for tool calling.

    This endpoint returns function definitions that can be used by LLMs
    (like Claude, GPT-4, etc.) to query your energy data conversationally.
    """
    tools = [
        {
            "name": "get_energy_profiles",
            "description": "Get all energy monitoring profiles (locations) for the user. Use this to find profile IDs needed for other queries.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_energy_devices",
            "description": "Get all energy monitoring devices installed at the user's properties.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
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
        },
        {
            "name": "get_week_energy_usage",
            "description": "Get the past week's energy usage for a specific profile. Returns hourly data for the last 7 days.",
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
                        "description": "Unit of measurement: 'w' for watts or '$/hr' for dollars per hour",
                        "default": "w"
                    }
                },
                "required": ["profile_id"]
            }
        },
        {
            "name": "get_historical_energy_data",
            "description": "Get historical energy data with custom time range and granularity. Most flexible option for specific queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile_id": {
                        "type": "integer",
                        "description": "The profile ID to query"
                    },
                    "hours_back": {
                        "type": "integer",
                        "description": "Number of hours of historical data to retrieve",
                        "default": 24
                    },
                    "granularity": {
                        "type": "string",
                        "enum": ["1T", "1H", "1D"],
                        "description": "Data granularity: '1T' (per minute), '1H' (per hour), '1D' (per day)",
                        "default": "1H"
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
    ]

    return {
        "tools": tools,
        "api_base_url": "/",
        "endpoint_mapping": {
            "get_energy_profiles": "GET /profiles",
            "get_energy_devices": "GET /devices",
            "get_today_energy_usage": "GET /energy/today",
            "get_week_energy_usage": "GET /energy/week",
            "get_historical_energy_data": "POST /energy/historical"
        }
    }


def main():
    """Main entry point for running the server"""
    uvicorn.run(
        "curb_energy.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
