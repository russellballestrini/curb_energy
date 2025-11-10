"""
Functional/End-to-End tests for the complete system

These tests verify the full stack with a real running server.
They are commented out by default and require:
- A running Curb Energy API server
- Valid authentication credentials
- Network access to the Curb API

To run these tests:
1. Set environment variables for authentication
2. Start the server: curb-server
3. Uncomment the tests below
4. Run: pytest tests/functional/ -v
"""

import pytest
import requests
import os
import time

# Skip all functional tests by default
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_FUNCTIONAL_TESTS") != "true",
    reason="Functional tests require RUN_FUNCTIONAL_TESTS=true"
)


@pytest.fixture(scope="module")
def api_base_url():
    """Get API base URL from environment or use default"""
    return os.getenv("CURB_API_URL", "http://localhost:8000")


@pytest.fixture(scope="module")
def auth_config():
    """Get authentication configuration from environment"""
    return {
        "username": os.getenv("CURB_USERNAME"),
        "password": os.getenv("CURB_PASSWORD"),
        "client_token": os.getenv("CURB_CLIENT_TOKEN"),
        "client_secret": os.getenv("CURB_CLIENT_SECRET"),
    }


@pytest.fixture(scope="module")
def configured_session(api_base_url, auth_config):
    """Configure a session with authentication"""
    session = requests.Session()

    # Configure authentication
    response = session.post(
        f"{api_base_url}/auth/configure",
        json=auth_config
    )
    assert response.status_code == 200

    return session


# =============================================================================
# COMMENTED OUT FUNCTIONAL TESTS
# Uncomment these when you want to run full E2E tests
# =============================================================================

"""
class TestServerHealth:
    def test_server_is_running(self, api_base_url):
        '''Test that the server is running and responsive'''
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_dashboard_loads(self, api_base_url):
        '''Test that the dashboard HTML loads'''
        response = requests.get(api_base_url)
        assert response.status_code == 200
        assert "Curb Energy Dashboard" in response.text

    def test_api_docs_available(self, api_base_url):
        '''Test that API documentation is accessible'''
        response = requests.get(f"{api_base_url}/docs")
        assert response.status_code == 200

    def test_openapi_schema_available(self, api_base_url):
        '''Test that OpenAPI schema is available'''
        response = requests.get(f"{api_base_url}/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema


class TestRealAuthentication:
    '''Test authentication with real credentials'''

    def test_configure_authentication(self, api_base_url, auth_config):
        '''Test configuring authentication with real credentials'''
        # Skip if credentials not set
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = requests.post(
            f"{api_base_url}/auth/configure",
            json=auth_config
        )
        assert response.status_code == 200
        assert response.json()["status"] == "configured"


class TestRealProfilesAPI:
    '''Test profiles API with real data'''

    def test_get_real_profiles(self, configured_session, api_base_url, auth_config):
        '''Test retrieving real profiles from Curb API'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = configured_session.get(f"{api_base_url}/profiles")
        assert response.status_code == 200

        profiles = response.json()
        assert isinstance(profiles, list)

        # If user has profiles, verify structure
        if len(profiles) > 0:
            profile = profiles[0]
            assert "id" in profile
            assert "name" in profile

    def test_get_real_devices(self, configured_session, api_base_url, auth_config):
        '''Test retrieving real devices from Curb API'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = configured_session.get(f"{api_base_url}/devices")
        assert response.status_code == 200

        devices = response.json()
        assert isinstance(devices, list)


class TestRealEnergyData:
    '''Test energy data endpoints with real data'''

    @pytest.fixture
    def profile_id(self, configured_session, api_base_url, auth_config):
        '''Get a real profile ID for testing'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = configured_session.get(f"{api_base_url}/profiles")
        profiles = response.json()

        if len(profiles) == 0:
            pytest.skip("No profiles available for testing")

        return profiles[0]["id"]

    def test_get_today_energy_real(
        self,
        configured_session,
        api_base_url,
        profile_id,
        auth_config
    ):
        '''Test getting today's energy data with real profile'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = configured_session.get(
            f"{api_base_url}/energy/today",
            params={"profile_id": profile_id}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["profile_id"] == profile_id
        assert "date" in data
        assert "data" in data

    def test_get_week_energy_real(
        self,
        configured_session,
        api_base_url,
        profile_id,
        auth_config
    ):
        '''Test getting week's energy data with real profile'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = configured_session.get(
            f"{api_base_url}/energy/week",
            params={"profile_id": profile_id}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["profile_id"] == profile_id
        assert data["period"] == "past_week"

    def test_get_historical_data_real(
        self,
        configured_session,
        api_base_url,
        profile_id,
        auth_config
    ):
        '''Test getting historical data with real profile'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        request_data = {
            "profile_id": profile_id,
            "hours_back": 24,
            "granularity": "1H",
            "unit": "w"
        }

        response = configured_session.post(
            f"{api_base_url}/energy/historical",
            json=request_data
        )
        assert response.status_code == 200

        data = response.json()
        assert data["profile_id"] == profile_id


class TestRealWorldWorkflow:
    '''Test complete real-world user workflows'''

    def test_llm_workflow_real(
        self,
        configured_session,
        api_base_url,
        auth_config
    ):
        '''Test a complete LLM interaction workflow with real data'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        # Step 1: LLM gets available tools
        response = configured_session.get(f"{api_base_url}/llm/tools")
        assert response.status_code == 200
        tools = response.json()["tools"]

        # Verify expected tools are available
        tool_names = [t["name"] for t in tools]
        assert "get_energy_profiles" in tool_names
        assert "get_today_energy_usage" in tool_names

        # Step 2: LLM gets profiles (simulating function call)
        response = configured_session.get(f"{api_base_url}/profiles")
        assert response.status_code == 200
        profiles = response.json()

        if len(profiles) == 0:
            pytest.skip("No profiles available")

        profile_id = profiles[0]["id"]

        # Step 3: LLM gets today's energy (simulating function call)
        response = configured_session.get(
            f"{api_base_url}/energy/today",
            params={"profile_id": profile_id}
        )
        assert response.status_code == 200
        energy_data = response.json()

        # Verify we got meaningful data
        assert energy_data["profile_id"] == profile_id
        assert "data" in energy_data

    def test_dashboard_workflow_real(
        self,
        configured_session,
        api_base_url,
        auth_config
    ):
        '''Test a complete dashboard user workflow with real data'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        # Step 1: Load dashboard
        response = configured_session.get(api_base_url)
        assert response.status_code == 200

        # Step 2: Get profiles for dropdown
        response = configured_session.get(f"{api_base_url}/profiles")
        assert response.status_code == 200
        profiles = response.json()

        if len(profiles) == 0:
            pytest.skip("No profiles available")

        # Step 3: Get today's data for first profile
        profile_id = profiles[0]["id"]
        response = configured_session.get(
            f"{api_base_url}/energy/today",
            params={"profile_id": profile_id}
        )
        assert response.status_code == 200

        # Step 4: Get week's data for comparison
        response = configured_session.get(
            f"{api_base_url}/energy/week",
            params={"profile_id": profile_id}
        )
        assert response.status_code == 200


class TestPerformance:
    '''Test API performance with real data'''

    def test_response_time_profiles(
        self,
        configured_session,
        api_base_url,
        auth_config
    ):
        '''Test that profile endpoint responds quickly'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        start = time.time()
        response = configured_session.get(f"{api_base_url}/profiles")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 5.0, f"Response took {elapsed}s, expected < 5s"

    def test_concurrent_requests(
        self,
        configured_session,
        api_base_url,
        auth_config
    ):
        '''Test handling multiple concurrent requests'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        import concurrent.futures

        def make_request():
            return configured_session.get(f"{api_base_url}/profiles")

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should succeed
        for response in results:
            assert response.status_code == 200


class TestErrorScenarios:
    '''Test error handling with real server'''

    def test_invalid_profile_id(
        self,
        configured_session,
        api_base_url,
        auth_config
    ):
        '''Test handling of invalid profile ID'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        response = configured_session.get(
            f"{api_base_url}/energy/today",
            params={"profile_id": 99999999}
        )
        # Should get error or empty data, not crash
        assert response.status_code in [200, 404, 500]

    def test_invalid_parameters(
        self,
        configured_session,
        api_base_url,
        auth_config
    ):
        '''Test handling of invalid parameters'''
        if not all(auth_config.values()):
            pytest.skip("Authentication credentials not set")

        # Missing required profile_id
        response = configured_session.get(f"{api_base_url}/energy/today")
        assert response.status_code == 422  # Validation error
"""


# =============================================================================
# HELPER FUNCTIONS FOR FUNCTIONAL TESTS
# =============================================================================

def wait_for_server(base_url, timeout=30, interval=1):
    """
    Wait for server to be ready

    Args:
        base_url: The base URL of the server
        timeout: Maximum time to wait in seconds
        interval: Time between checks in seconds

    Returns:
        True if server is ready, False otherwise
    """
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)
    return False


def is_server_running(base_url):
    """
    Check if server is currently running

    Args:
        base_url: The base URL of the server

    Returns:
        True if server is running, False otherwise
    """
    try:
        response = requests.get(f"{base_url}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# =============================================================================
# INSTRUCTIONS FOR RUNNING FUNCTIONAL TESTS
# =============================================================================

"""
To enable and run functional tests:

1. Set environment variables:
   export CURB_USERNAME="your_username"
   export CURB_PASSWORD="your_password"
   export CURB_CLIENT_TOKEN="your_client_token"
   export CURB_CLIENT_SECRET="your_client_secret"
   export RUN_FUNCTIONAL_TESTS="true"

2. Start the server in one terminal:
   curb-server

3. Run functional tests in another terminal:
   pytest tests/functional/ -v

4. Or run all tests including functional:
   make test-functional

Note: Functional tests will:
- Make real API calls to the Curb Energy API
- Require valid authentication credentials
- Take longer to run than unit/integration tests
- May incur API rate limits
- Require network connectivity
"""


if __name__ == "__main__":
    print(__doc__)
