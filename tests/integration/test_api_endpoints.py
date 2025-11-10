"""
Integration tests for API endpoints

These tests verify that endpoints work correctly with mocked
Curb API client responses.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from curb_energy.server import app
from curb_energy.client import RestApiClient, AuthToken
from curb_energy import models


@pytest.fixture
def mock_auth_token():
    """Create a mock authentication token"""
    return AuthToken(
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        expires_in=3600,
        user_id=12345,
        token_type="bearer"
    )


@pytest.fixture
def mock_profiles():
    """Create mock profile data"""
    profile = MagicMock()
    profile.id = 123
    profile.label = "Test Home"
    profile.timezone = "America/New_York"
    profile.location = "123 Test St"
    return [profile]


@pytest.fixture
def mock_devices():
    """Create mock device data"""
    device = MagicMock()
    device.id = "device-abc123"
    device.label = "Main Panel"
    device.profile_id = 123
    return [device]


@pytest.fixture
def mock_historical_data():
    """Create mock historical energy data"""
    return {
        "measurements": [
            {"timestamp": 1699574400, "value": 850, "unit": "w"},
            {"timestamp": 1699578000, "value": 920, "unit": "w"},
            {"timestamp": 1699581600, "value": 780, "unit": "w"},
        ],
        "granularity": "1H",
        "unit": "w"
    }


@pytest.fixture
def configured_client():
    """Configure authentication before tests"""
    client = TestClient(app)

    # Configure auth
    auth_data = {
        "username": "test_user",
        "password": "test_pass",
        "client_token": "test_token",
        "client_secret": "test_secret"
    }

    response = client.post("/auth/configure", json=auth_data)
    assert response.status_code == 200

    return client


class TestProfilesEndpoint:
    """Integration tests for /profiles endpoint"""

    @patch('curb_energy.server.get_client')
    def test_get_profiles_success(self, mock_get_client, mock_profiles):
        """Test successful profile retrieval"""
        # Setup mock client
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.profiles = AsyncMock(return_value=mock_profiles)
        mock_get_client.return_value = mock_client

        # Make request
        client = TestClient(app)
        response = client.get("/profiles")

        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == 123
        assert data[0]["name"] == "Test Home"

    @patch('curb_energy.server.get_client')
    def test_get_profiles_empty_list(self, mock_get_client):
        """Test profiles endpoint with no profiles"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.profiles = AsyncMock(return_value=[])
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/profiles")

        assert response.status_code == 200
        assert response.json() == []

    @patch('curb_energy.server.get_client')
    def test_get_profiles_error(self, mock_get_client):
        """Test profiles endpoint with API error"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.profiles = AsyncMock(side_effect=Exception("API Error"))
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/profiles")

        assert response.status_code == 500
        assert "API Error" in response.json()["detail"]


class TestDevicesEndpoint:
    """Integration tests for /devices endpoint"""

    @patch('curb_energy.server.get_client')
    def test_get_devices_success(self, mock_get_client, mock_devices):
        """Test successful device retrieval"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.devices = AsyncMock(return_value=mock_devices)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/devices")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "device-abc123"
        assert data[0]["label"] == "Main Panel"

    @patch('curb_energy.server.get_client')
    def test_get_devices_empty_list(self, mock_get_client):
        """Test devices endpoint with no devices"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.devices = AsyncMock(return_value=[])
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/devices")

        assert response.status_code == 200
        assert response.json() == []


class TestTodayEnergyEndpoint:
    """Integration tests for /energy/today endpoint"""

    @patch('curb_energy.server.get_client')
    def test_get_today_energy_success(self, mock_get_client, mock_historical_data):
        """Test successful today's energy retrieval"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/energy/today?profile_id=123")

        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == 123
        assert "date" in data
        assert "data" in data
        assert data["unit"] == "w"

    @patch('curb_energy.server.get_client')
    def test_get_today_energy_with_unit(self, mock_get_client, mock_historical_data):
        """Test today's energy with custom unit"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/energy/today?profile_id=123&unit=$/hr")

        assert response.status_code == 200
        data = response.json()
        assert data["unit"] == "$/hr"

    def test_get_today_energy_missing_profile_id(self):
        """Test today's energy without profile_id"""
        client = TestClient(app)
        response = client.get("/energy/today")

        assert response.status_code == 422  # Validation error


class TestWeekEnergyEndpoint:
    """Integration tests for /energy/week endpoint"""

    @patch('curb_energy.server.get_client')
    def test_get_week_energy_success(self, mock_get_client, mock_historical_data):
        """Test successful week energy retrieval"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/energy/week?profile_id=123")

        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == 123
        assert data["period"] == "past_week"
        assert "since" in data
        assert "until" in data
        assert "data" in data


class TestHistoricalEnergyEndpoint:
    """Integration tests for /energy/historical endpoint"""

    @patch('curb_energy.server.get_client')
    def test_post_historical_data_success(self, mock_get_client, mock_historical_data):
        """Test successful historical data retrieval"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        request_data = {
            "profile_id": 123,
            "granularity": "1H",
            "unit": "w",
            "hours_back": 24
        }
        response = client.post("/energy/historical", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == 123
        assert data["granularity"] == "1H"
        assert data["unit"] == "w"

    @patch('curb_energy.server.get_client')
    def test_post_historical_data_custom_params(self, mock_get_client, mock_historical_data):
        """Test historical data with custom parameters"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        request_data = {
            "profile_id": 456,
            "granularity": "1D",
            "unit": "$/hr",
            "hours_back": 168  # 7 days
        }
        response = client.post("/energy/historical", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["profile_id"] == 456
        assert data["granularity"] == "1D"
        assert data["unit"] == "$/hr"

        # Verify the client was called with correct parameters
        mock_client.historical_data.assert_called_once()
        call_kwargs = mock_client.historical_data.call_args.kwargs
        assert call_kwargs["profile_id"] == 456
        assert call_kwargs["granularity"] == "1D"
        assert call_kwargs["unit"] == "$/hr"

    def test_post_historical_data_validation(self):
        """Test historical data endpoint validation"""
        client = TestClient(app)

        # Missing profile_id
        response = client.post("/energy/historical", json={
            "granularity": "1H"
        })
        assert response.status_code == 422

        # Invalid granularity
        response = client.post("/energy/historical", json={
            "profile_id": 123,
            "granularity": "invalid"
        })
        assert response.status_code == 200  # Validation happens at API level


class TestEndToEndScenarios:
    """Integration tests for common user scenarios"""

    @patch('curb_energy.server.get_client')
    def test_user_workflow_get_profiles_then_energy(
        self,
        mock_get_client,
        mock_profiles,
        mock_historical_data
    ):
        """Test typical user workflow: get profiles, then get energy data"""
        # Setup mock client
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.profiles = AsyncMock(return_value=mock_profiles)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)

        # Step 1: Get profiles
        response = client.get("/profiles")
        assert response.status_code == 200
        profiles = response.json()
        profile_id = profiles[0]["id"]

        # Step 2: Get today's energy for that profile
        response = client.get(f"/energy/today?profile_id={profile_id}")
        assert response.status_code == 200
        energy_data = response.json()
        assert energy_data["profile_id"] == profile_id

    @patch('curb_energy.server.get_client')
    def test_llm_workflow(
        self,
        mock_get_client,
        mock_profiles,
        mock_historical_data
    ):
        """Test LLM workflow: get tools, get profiles, get energy"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.profiles = AsyncMock(return_value=mock_profiles)
        mock_client.historical_data = AsyncMock(return_value=mock_historical_data)
        mock_get_client.return_value = mock_client

        client = TestClient(app)

        # Step 1: LLM gets available tools
        response = client.get("/llm/tools")
        assert response.status_code == 200
        tools = response.json()["tools"]
        tool_names = [t["name"] for t in tools]
        assert "get_energy_profiles" in tool_names

        # Step 2: LLM calls get_energy_profiles
        response = client.get("/profiles")
        assert response.status_code == 200
        profiles = response.json()

        # Step 3: LLM calls get_today_energy_usage
        response = client.get(f"/energy/today?profile_id={profiles[0]['id']}")
        assert response.status_code == 200


class TestErrorHandling:
    """Integration tests for error scenarios"""

    @patch('curb_energy.server.get_client')
    def test_network_error(self, mock_get_client):
        """Test handling of network errors"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.profiles = AsyncMock(side_effect=ConnectionError("Network error"))
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/profiles")

        assert response.status_code == 500
        assert "Network error" in response.json()["detail"]

    @patch('curb_energy.server.get_client')
    def test_authentication_error(self, mock_get_client):
        """Test handling of authentication errors"""
        mock_client = AsyncMock(spec=RestApiClient)
        mock_client.__aenter__ = AsyncMock(
            side_effect=Exception("Authentication failed")
        )
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_get_client.return_value = mock_client

        client = TestClient(app)
        response = client.get("/profiles")

        assert response.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
