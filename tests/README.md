# Tests

Comprehensive test suite for the Curb Energy library.

## Test Structure

```
tests/
├── unit/               # Unit tests (fast, isolated)
│   └── test_server.py  # Server module unit tests
├── integration/        # Integration tests (mocked dependencies)
│   └── test_api_endpoints.py  # API endpoint tests
├── functional/         # Functional/E2E tests (require running server)
│   └── test_e2e.py     # End-to-end workflow tests
└── client/             # Original client library tests
    ├── test_auth_token.py
    ├── test_models.py
    ├── test_realtime_client.py
    ├── test_rest_client.py
    └── test_schema.py
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests that verify individual components:
- No external dependencies
- No network calls
- No database access
- Mock all dependencies

**Run:** `make test-unit` or `pytest tests/unit/`

### Integration Tests (`tests/integration/`)

Test interactions between components:
- Mock external APIs (Curb API)
- Test API endpoints with mocked client
- Test request/response handling
- Test error scenarios

**Run:** `make test-integration` or `pytest tests/integration/`

### Functional Tests (`tests/functional/`)

End-to-end tests with real services:
- Require running server
- Need valid authentication
- Make real API calls
- Test complete workflows
- **Currently commented out by default**

**Run:** `make test-functional` (after setup)

## Running Tests

### Quick Start

```bash
# Install dependencies
make install-all

# Run unit and integration tests (default)
make test

# Run all tests
make test-all

# Run specific test categories
make test-unit
make test-integration
make test-client

# Run with coverage report
make test-coverage
```

### Using pytest directly

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests (except functional)
pytest

# Run specific test file
pytest tests/unit/test_server.py

# Run specific test class
pytest tests/unit/test_server.py::TestHealthEndpoint

# Run specific test
pytest tests/unit/test_server.py::TestHealthEndpoint::test_health_check

# Run tests matching pattern
pytest -k "test_profile"

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=curb_energy --cov-report=html
```

### Test Markers

Tests are marked with pytest markers for categorization:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only functional tests (if enabled)
pytest -m functional

# Run tests that don't require auth
pytest -m "not requires_auth"

# Run fast tests only
pytest -m "not slow"
```

## Running Functional Tests

Functional tests are commented out by default and require:

1. **Set environment variables:**
   ```bash
   export CURB_USERNAME="your_username"
   export CURB_PASSWORD="your_password"
   export CURB_CLIENT_TOKEN="your_client_token"
   export CURB_CLIENT_SECRET="your_client_secret"
   export RUN_FUNCTIONAL_TESTS="true"
   ```

2. **Start the server:**
   ```bash
   make server
   # or
   curb-server
   ```

3. **Uncomment tests in** `tests/functional/test_e2e.py`

4. **Run functional tests:**
   ```bash
   make test-functional
   # or
   pytest tests/functional/ -v
   ```

## Test Coverage

View coverage report:

```bash
# Generate HTML coverage report
make test-coverage

# Open in browser
open htmlcov/index.html

# Terminal summary
pytest --cov=curb_energy --cov-report=term
```

## Writing Tests

### Unit Test Example

```python
# tests/unit/test_my_module.py
import pytest
from curb_energy.my_module import my_function

class TestMyFunction:
    def test_basic_case(self):
        """Test basic functionality"""
        result = my_function(42)
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case handling"""
        with pytest.raises(ValueError):
            my_function(-1)
```

### Integration Test Example

```python
# tests/integration/test_my_endpoint.py
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from curb_energy.server import app

@patch('curb_energy.server.get_client')
def test_my_endpoint(mock_get_client):
    """Test endpoint with mocked dependencies"""
    # Setup mock
    mock_client = AsyncMock()
    mock_client.some_method = AsyncMock(return_value={"data": "test"})
    mock_get_client.return_value = mock_client

    # Make request
    client = TestClient(app)
    response = client.get("/my-endpoint")

    # Verify
    assert response.status_code == 200
    assert response.json() == {"data": "test"}
```

### Async Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function"""
    result = await my_async_function()
    assert result == expected_value
```

## Test Fixtures

Common test fixtures are defined in:
- `tests/unit/conftest.py` (if exists)
- `tests/integration/conftest.py` (if exists)
- `tests/client/conftest.py` (existing)

Example fixture:

```python
# conftest.py
import pytest

@pytest.fixture
def mock_auth_token():
    """Provide mock authentication token"""
    return AuthToken(
        access_token="test_token",
        refresh_token="test_refresh",
        expires_in=3600,
        user_id=12345
    )
```

## Continuous Integration

The test suite is designed to run in CI environments:

```bash
# Run all CI checks (quality + tests)
make ci

# Just quality checks
make ci-quality

# Just tests
make ci-test
```

## Tips

### Speed up tests

```bash
# Run tests in parallel (requires pytest-xdist)
pip install pytest-xdist
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Debug failing tests

```bash
# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Show more output
pytest -vv --tb=long

# Show print statements
pytest -s
```

### Watch mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
make test-watch
# or
ptw -- -v
```

## Coverage Goals

Target coverage levels:
- **Overall:** > 80%
- **Core modules:** > 90%
- **Server module:** > 85%
- **Client module:** > 90%

Check current coverage:
```bash
make test-coverage
```

## Troubleshooting

### Tests fail with "ModuleNotFoundError"

Install package in development mode:
```bash
make install-dev
```

### Tests fail with "FastAPI not found"

Install server dependencies:
```bash
make install-server
```

### Async tests fail

Make sure `asyncio_mode = auto` is in `pytest.ini`

### Functional tests don't run

1. Check environment variables are set
2. Ensure server is running
3. Uncomment tests in `test_e2e.py`
4. Set `RUN_FUNCTIONAL_TESTS=true`

## Contributing

When adding new features:

1. **Write tests first** (TDD)
2. **Add unit tests** for new functions/classes
3. **Add integration tests** for new API endpoints
4. **Update functional tests** for new workflows
5. **Maintain coverage** above 80%
6. **Run all tests** before committing:
   ```bash
   make check
   ```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)
