# Testing Guide

Comprehensive guide for testing the Curb Energy library.

## Quick Start

```bash
# Install all dependencies
make install-all

# Run tests
make test

# Run with coverage
make test-coverage

# Run all quality checks and tests
make check
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose:** Test individual components in isolation

**Characteristics:**
- Fast execution (< 1 second per test)
- No external dependencies
- No network calls
- All dependencies are mocked
- Test single functions/classes

**What's tested:**
- Request/response models
- Utility functions
- Model validation
- Schema generation
- Individual endpoint logic

**Run:** `make test-unit`

**Example:**
```python
def test_auth_config_valid():
    """Test creating a valid AuthConfig"""
    config = AuthConfig(
        username="test",
        password="pass",
        client_token="token",
        client_secret="secret"
    )
    assert config.username == "test"
```

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Test how components work together

**Characteristics:**
- Moderate execution time (< 5 seconds per test)
- Mock external APIs (Curb API)
- Test HTTP endpoints with test client
- Test error handling
- Test data flow between components

**What's tested:**
- API endpoint responses
- Request validation
- Error scenarios
- Authentication flow
- Complete request/response cycles

**Run:** `make test-integration`

**Example:**
```python
@patch('curb_energy.server.get_client')
def test_get_profiles_success(mock_get_client, mock_profiles):
    """Test successful profile retrieval"""
    mock_client = AsyncMock()
    mock_client.profiles = AsyncMock(return_value=mock_profiles)
    mock_get_client.return_value = mock_client

    client = TestClient(app)
    response = client.get("/profiles")

    assert response.status_code == 200
    assert len(response.json()) == 1
```

### 3. Functional Tests (`tests/functional/`)

**Purpose:** Test the complete system end-to-end

**Characteristics:**
- Slow execution (5-30 seconds per test)
- Requires running server
- Needs valid authentication
- Makes real API calls
- Tests complete user workflows
- **Currently commented out by default**

**What's tested:**
- Complete user workflows
- Real API integration
- Server performance
- Error handling in production
- Dashboard functionality

**Setup:**
```bash
# 1. Set environment variables
export CURB_USERNAME="your_username"
export CURB_PASSWORD="your_password"
export CURB_CLIENT_TOKEN="your_token"
export CURB_CLIENT_SECRET="your_secret"
export RUN_FUNCTIONAL_TESTS="true"

# 2. Start server
make server

# 3. In another terminal
make test-functional
```

## Test Execution Strategies

### Development Workflow

```bash
# 1. Write code
# 2. Run relevant tests quickly
pytest tests/unit/test_server.py::TestMyFeature -v

# 3. Run all unit tests
make test-unit

# 4. Run integration tests
make test-integration

# 5. Before committing
make check
```

### Pre-commit Checklist

```bash
# Run everything
make check

# This runs:
# - Code formatting check (black)
# - Linting (ruff)
# - Type checking (mypy)
# - Unit tests
# - Integration tests
```

### Continuous Integration

```bash
# Run CI checks locally
make ci

# This runs:
# - Quality checks (format, lint)
# - All tests with coverage
# - Generates XML reports
```

## Coverage Requirements

### Target Coverage

- **Overall project:** > 80%
- **Core modules:** > 90%
- **Server module:** > 85%
- **Client module:** > 90%
- **New features:** 100%

### Checking Coverage

```bash
# Generate HTML report
make test-coverage

# View in browser
open htmlcov/index.html

# View in terminal
pytest --cov=curb_energy --cov-report=term-missing
```

### Coverage by Module

```bash
# Coverage for specific module
pytest --cov=curb_energy.server --cov-report=term-missing

# Coverage for specific file
pytest tests/unit/test_server.py --cov=curb_energy.server
```

## Writing Good Tests

### Test Structure (Arrange-Act-Assert)

```python
def test_something():
    # Arrange: Set up test data
    config = AuthConfig(username="test", ...)

    # Act: Execute the code being tested
    result = some_function(config)

    # Assert: Verify the outcome
    assert result.status == "success"
```

### Test Naming Convention

```python
# Good names
def test_get_profiles_returns_list_of_profiles():
def test_auth_token_expires_after_timeout():
def test_invalid_profile_id_raises_error():

# Bad names
def test_profiles():
def test_1():
def test_something():
```

### Use Fixtures for Reusable Setup

```python
@pytest.fixture
def mock_profiles():
    """Create mock profile data"""
    profile = MagicMock()
    profile.id = 123
    profile.label = "Test Home"
    return [profile]

def test_using_fixture(mock_profiles):
    """Test uses the fixture"""
    assert len(mock_profiles) == 1
```

### Parametrize for Multiple Test Cases

```python
@pytest.mark.parametrize("profile_id,expected", [
    (123, True),
    (456, True),
    (None, False),
    (-1, False),
])
def test_validate_profile_id(profile_id, expected):
    """Test profile ID validation"""
    result = is_valid_profile_id(profile_id)
    assert result == expected
```

### Test Error Conditions

```python
def test_invalid_credentials_raises_error():
    """Test that invalid credentials raise error"""
    with pytest.raises(AuthenticationError):
        authenticate(username="invalid", password="wrong")
```

### Mock External Dependencies

```python
@patch('requests.get')
def test_api_call(mock_get):
    """Test API call with mocked requests"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": "test"}

    result = fetch_data()
    assert result["data"] == "test"
```

## Test Organization

### File Structure

```python
# tests/unit/test_server.py
class TestAuthConfig:
    """Tests for AuthConfig model"""

    def test_valid_config(self):
        ...

    def test_missing_fields(self):
        ...

class TestHealthEndpoint:
    """Tests for /health endpoint"""

    def test_health_check_returns_200(self):
        ...

    def test_health_check_response_format(self):
        ...
```

### Grouping Related Tests

```python
class TestProfilesAPI:
    """All tests related to profiles API"""

    @pytest.fixture
    def mock_client(self):
        """Shared fixture for this class"""
        ...

    def test_get_profiles_success(self, mock_client):
        ...

    def test_get_profiles_empty(self, mock_client):
        ...

    def test_get_profiles_error(self, mock_client):
        ...
```

## Debugging Tests

### Run Specific Test

```bash
# Run single test file
pytest tests/unit/test_server.py

# Run single test class
pytest tests/unit/test_server.py::TestHealthEndpoint

# Run single test method
pytest tests/unit/test_server.py::TestHealthEndpoint::test_health_check

# Run tests matching pattern
pytest -k "health"
```

### Debugging Options

```bash
# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Show full traceback
pytest --tb=long

# Show print statements
pytest -s

# Increase verbosity
pytest -vv
```

### Show Test Output

```bash
# Show stdout/stderr
pytest -s

# Show captured logs
pytest --log-cli-level=DEBUG

# Show local variables on failure
pytest -l
```

## Performance Testing

### Measure Test Execution Time

```bash
# Show slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto

# Use specific number of workers
pytest -n 4
```

## Common Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'curb_energy'`

**Solution:**
```bash
# Install package in development mode
make install-all
# or
pip install -e ".[all]"
```

### FastAPI Not Found

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Install server dependencies
make install-server
# or
pip install -e ".[server]"
```

### Async Tests Failing

**Problem:** Tests with `async def` not running correctly

**Solution:**
1. Add `@pytest.mark.asyncio` decorator
2. Ensure `asyncio_mode = auto` in pytest.ini
3. Install pytest-asyncio: `pip install pytest-asyncio`

### Mock Not Working

**Problem:** Mock not being used, real function still called

**Solution:**
```python
# Make sure to patch the right location
# Patch where it's used, not where it's defined
@patch('curb_energy.server.get_client')  # ✓ Correct
# not
@patch('curb_energy.client.get_client')  # ✗ Wrong
```

## Best Practices

1. **Write tests first** (Test-Driven Development)
2. **Keep tests isolated** - each test should be independent
3. **Use descriptive names** - test name should explain what it tests
4. **Test one thing at a time** - one assertion per test when possible
5. **Mock external dependencies** - don't make real API calls in unit tests
6. **Test edge cases** - empty lists, null values, invalid inputs
7. **Test error conditions** - not just happy path
8. **Keep tests fast** - unit tests should be < 1 second
9. **Maintain high coverage** - aim for > 80%
10. **Clean up after tests** - use fixtures and teardown

## Test Maintenance

### Regular Tasks

```bash
# Update dependencies
make upgrade-deps

# Check for deprecated test patterns
ruff check tests/

# Review coverage
make test-coverage
```

### Before Releases

```bash
# Run full test suite
make test-all

# Run quality checks
make quality

# Run CI checks
make ci

# Test documentation builds
make docs
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

## Getting Help

If you have questions about testing:

1. Check this guide
2. Read `tests/README.md`
3. Look at existing test examples
4. Run `make help` for available commands
5. Check the pytest documentation
