"""
Unit tests for the FastAPI server module

These tests focus on testing individual components in isolation
with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Only import if FastAPI is installed
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from curb_energy.server import app, get_client, AuthConfig
from curb_energy.client import AuthToken, RestApiClient


class TestAuthConfig:
    """Test AuthConfig model validation"""

    def test_auth_config_valid(self):
        """Test creating a valid AuthConfig"""
        config = AuthConfig(
            username="test_user",
            password="test_pass",
            client_token="test_token",
            client_secret="test_secret"
        )
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.client_token == "test_token"
        assert config.client_secret == "test_secret"

    def test_auth_config_missing_field(self):
        """Test that AuthConfig requires all fields"""
        with pytest.raises(Exception):  # Pydantic ValidationError
            AuthConfig(
                username="test_user",
                password="test_pass",
                # Missing client_token and client_secret
            )


class TestHealthEndpoint:
    """Test the health check endpoint"""

    def test_health_check(self):
        """Test health check returns 200 and correct status"""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {
            "status": "healthy",
            "service": "curb-energy-api"
        }


class TestRootEndpoint:
    """Test the root dashboard endpoint"""

    def test_root_returns_html(self):
        """Test that root endpoint returns HTML dashboard"""
        client = TestClient(app)
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Curb Energy Dashboard" in response.text


class TestAuthConfigurationEndpoint:
    """Test authentication configuration endpoint"""

    def test_configure_auth(self):
        """Test configuring authentication credentials"""
        client = TestClient(app)

        auth_config = {
            "username": "test_user",
            "password": "test_pass",
            "client_token": "test_token",
            "client_secret": "test_secret"
        }

        response = client.post("/auth/configure", json=auth_config)
        assert response.status_code == 200
        assert response.json()["status"] == "configured"

    def test_configure_auth_missing_fields(self):
        """Test that auth configuration requires all fields"""
        client = TestClient(app)

        incomplete_config = {
            "username": "test_user",
            "password": "test_pass",
            # Missing client_token and client_secret
        }

        response = client.post("/auth/configure", json=incomplete_config)
        assert response.status_code == 422  # Validation error


class TestLLMToolsEndpoint:
    """Test LLM tools schema endpoint"""

    def test_llm_tools_returns_schemas(self):
        """Test that /llm/tools returns tool schemas"""
        client = TestClient(app)
        response = client.get("/llm/tools")
        assert response.status_code == 200

        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) > 0

        # Check first tool has required fields
        tool = data["tools"][0]
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool

    def test_llm_tools_has_expected_functions(self):
        """Test that all expected tool functions are present"""
        client = TestClient(app)
        response = client.get("/llm/tools")
        data = response.json()

        tool_names = [tool["name"] for tool in data["tools"]]

        expected_tools = [
            "get_energy_profiles",
            "get_energy_devices",
            "get_today_energy_usage",
            "get_week_energy_usage",
            "get_historical_energy_data"
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    def test_llm_tool_schema_structure(self):
        """Test that tool schemas have correct structure"""
        client = TestClient(app)
        response = client.get("/llm/tools")
        data = response.json()

        for tool in data["tools"]:
            # Each tool must have these fields
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool

            # Parameters must be an object with properties
            params = tool["parameters"]
            assert params["type"] == "object"
            assert "properties" in params or "required" in params


class TestRequestModels:
    """Test Pydantic request models"""

    def test_energy_data_request_defaults(self):
        """Test EnergyDataRequest with default values"""
        from curb_energy.server import EnergyDataRequest

        request = EnergyDataRequest(profile_id=123)
        assert request.profile_id == 123
        assert request.granularity == "1H"
        assert request.unit == "w"
        assert request.hours_back == 24

    def test_energy_data_request_custom_values(self):
        """Test EnergyDataRequest with custom values"""
        from curb_energy.server import EnergyDataRequest

        request = EnergyDataRequest(
            profile_id=456,
            granularity="1D",
            unit="$/hr",
            hours_back=48
        )
        assert request.profile_id == 456
        assert request.granularity == "1D"
        assert request.unit == "$/hr"
        assert request.hours_back == 48


class TestResponseModels:
    """Test Pydantic response models"""

    def test_profile_response(self):
        """Test ProfileResponse model"""
        from curb_energy.server import ProfileResponse

        profile = ProfileResponse(
            id=123,
            name="Test Profile",
            timezone="America/New_York",
            location="Test Location"
        )
        assert profile.id == 123
        assert profile.name == "Test Profile"
        assert profile.timezone == "America/New_York"

    def test_device_response(self):
        """Test DeviceResponse model"""
        from curb_energy.server import DeviceResponse

        device = DeviceResponse(
            id="device-123",
            label="Test Device",
            profile_id=456
        )
        assert device.id == "device-123"
        assert device.label == "Test Device"
        assert device.profile_id == 456


class TestCORSConfiguration:
    """Test CORS middleware configuration"""

    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses"""
        client = TestClient(app)

        response = client.get(
            "/health",
            headers={"Origin": "http://example.com"}
        )

        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight(self):
        """Test CORS preflight OPTIONS request"""
        client = TestClient(app)

        response = client.options(
            "/profiles",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET"
            }
        )

        # Should allow the request
        assert "access-control-allow-origin" in response.headers


class TestOpenAPISchema:
    """Test OpenAPI schema generation"""

    def test_openapi_json_available(self):
        """Test that OpenAPI schema is available"""
        client = TestClient(app)
        response = client.get("/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_openapi_has_endpoints(self):
        """Test that OpenAPI schema includes our endpoints"""
        client = TestClient(app)
        response = client.get("/openapi.json")
        schema = response.json()

        paths = schema["paths"]

        expected_paths = [
            "/health",
            "/profiles",
            "/devices",
            "/energy/today",
            "/energy/week",
            "/energy/historical",
            "/llm/tools"
        ]

        for path in expected_paths:
            assert path in paths, f"Missing endpoint in OpenAPI: {path}"


@pytest.mark.asyncio
class TestGetClientDependency:
    """Test the get_client dependency function"""

    @patch.dict('os.environ', {
        'CURB_USERNAME': 'test_user',
        'CURB_PASSWORD': 'test_pass',
        'CURB_CLIENT_TOKEN': 'test_token',
        'CURB_CLIENT_SECRET': 'test_secret'
    })
    async def test_get_client_from_env(self):
        """Test creating client from environment variables"""
        # Reset global state
        import curb_energy.server
        curb_energy.server._client = None
        curb_energy.server._auth_config = None

        client = get_client()
        assert isinstance(client, RestApiClient)
        assert client.auth_username == "test_user"

    async def test_get_client_without_config_raises(self):
        """Test that get_client raises without configuration"""
        # Reset global state and clear env vars
        import curb_energy.server
        curb_energy.server._client = None
        curb_energy.server._auth_config = None

        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception):  # Should raise HTTPException
                get_client()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
