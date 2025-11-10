# Makefile Quick Reference

## 🚀 Most Common Commands

```bash
make help              # Show all available commands
make install-all       # Install everything (first time setup)
make test              # Run tests (unit + integration)
make server            # Start the API server
make check             # Run all quality checks + tests
```

## 📦 Environment Setup

| Command | Description |
|---------|-------------|
| `make venv` | Create virtual environment |
| `make install` | Install core dependencies |
| `make install-dev` | Install dev dependencies |
| `make install-server` | Install server dependencies |
| `make install-all` | Install everything ⭐ |

## 🧪 Testing Commands

| Command | Description |
|---------|-------------|
| `make test` | Run unit + integration tests ⭐ |
| `make test-unit` | Run only unit tests (fast) |
| `make test-integration` | Run only integration tests |
| `make test-functional` | Run E2E tests (requires server) |
| `make test-client` | Run original client tests |
| `make test-all` | Run all tests except functional |
| `make test-coverage` | Run tests with coverage report ⭐ |

### Test Coverage

After running `make test-coverage`, open the HTML report:
```bash
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## ✨ Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Check code with ruff |
| `make format` | Auto-format code with black ⭐ |
| `make format-check` | Check formatting (no changes) |
| `make type-check` | Run mypy type checking |
| `make quality` | Run all quality checks |
| `make check` | Quality checks + tests ⭐ |

## 🌐 Server Commands

| Command | Description |
|---------|-------------|
| `make server` | Start server (dev mode) ⭐ |
| `make server-dev` | Start with debug logging |
| `make server-prod` | Start in production mode |
| `make server-test` | Start on port 8001 for testing |

Server will be available at:
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/docs
- OpenAPI Schema: http://localhost:8000/openapi.json

## 🔨 Build & Deploy

| Command | Description |
|---------|-------------|
| `make build` | Build distribution packages |
| `make publish` | Publish to PyPI |
| `make publish-test` | Publish to TestPyPI |
| `make docs` | Build documentation |
| `make docs-serve` | Serve docs at localhost:8080 |

## 🧹 Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Remove cache and test artifacts ⭐ |
| `make clean-pyc` | Remove Python cache files |
| `make clean-test` | Remove test artifacts |
| `make clean-build` | Remove build artifacts |
| `make clean-all` | Remove everything including venv |

## 🔄 CI/CD

| Command | Description |
|---------|-------------|
| `make ci` | Run full CI suite ⭐ |
| `make ci-test` | Run CI tests |
| `make ci-quality` | Run CI quality checks |

## 🛠️ Development Helpers

| Command | Description |
|---------|-------------|
| `make shell` | Start Python shell with package imported |
| `make notebook` | Start Jupyter notebook |
| `make info` | Show project information |
| `make status` | Show environment status |
| `make requirements` | Generate requirements.txt |
| `make upgrade-deps` | Upgrade all dependencies |

## 🐳 Docker (Optional)

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |

## 📋 Common Workflows

### First Time Setup
```bash
git clone <repo>
cd curb_energy
make install-all
make test
```

### Daily Development
```bash
# Write code
vim src/curb_energy/server.py

# Format and check
make format
make lint

# Run tests
make test

# Before commit
make check
```

### Starting Server
```bash
# Set environment variables
export CURB_USERNAME="your_username"
export CURB_PASSWORD="your_password"
export CURB_CLIENT_TOKEN="your_token"
export CURB_CLIENT_SECRET="your_secret"

# Start server
make server
```

### Running Specific Tests
```bash
# Run specific test file
pytest tests/unit/test_server.py -v

# Run specific test
pytest tests/unit/test_server.py::TestHealthEndpoint::test_health_check -v

# Run tests matching pattern
pytest -k "profile" -v
```

### Before Pushing Code
```bash
# Run all checks
make check

# Or run individually
make format      # Auto-format
make lint        # Check code quality
make type-check  # Check types
make test        # Run tests
```

### Creating a Release
```bash
# Update version in src/curb_energy/__init__.py
# Update CHANGES.rst

# Run full test suite
make test-all
make test-coverage

# Build and check
make build

# Publish (requires PyPI credentials)
make publish
```

## 💡 Tips

### Speed Up Tests
```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Watch Mode
```bash
# Install pytest-watch
make test-watch

# Tests will re-run when files change
```

### Debug Tests
```bash
# Stop on first failure
pytest -x

# Enter debugger on failure
pytest --pdb

# Show more details
pytest -vv --tb=long
```

### Check What Changed
```bash
# Show what's installed
make info

# Check environment status
make status

# Show which tests would run
pytest --collect-only
```

## 🎯 Quick Goals

| Goal | Commands |
|------|----------|
| Get started | `make install-all` → `make test` |
| Start coding | `make format` → `make lint` → `make test` |
| Run server | Set env vars → `make server` |
| Before commit | `make check` |
| Full CI locally | `make ci` |
| Deploy | `make build` → `make publish` |

## 📚 Documentation

- Full test guide: See `TESTING.md`
- Test documentation: See `tests/README.md`
- Server documentation: See `SERVER_README.md`
- Schema explanation: See `SCHEMA_EXPLANATION.md`

## 🆘 Troubleshooting

### "make: command not found"
Install GNU Make:
- macOS: `brew install make`
- Ubuntu/Debian: `sudo apt install make`
- Windows: Use WSL or install Make for Windows

### "ModuleNotFoundError"
```bash
make install-all
```

### "pytest: command not found"
```bash
source .venv/bin/activate
make install-dev
```

### Tests failing
```bash
# Clean and reinstall
make clean-all
make install-all
make test
```

### Server won't start
```bash
# Check if dependencies installed
make install-server

# Check if port 8000 is in use
lsof -i :8000

# Try different port
uvicorn curb_energy.server:app --port 8001
```

## 🎨 Color Output

The Makefile uses colors for better readability:
- 🔵 Blue: Informational messages
- 🟢 Green: Success messages
- 🟡 Yellow: Warnings
- 🔴 Red: Errors

If colors don't work in your terminal, they'll automatically fallback to plain text.

## ⭐ Essential Commands for New Users

1. **Setup:** `make install-all`
2. **Test:** `make test`
3. **Format:** `make format`
4. **Check:** `make check`
5. **Server:** `make server`
6. **Help:** `make help`

Start with these 6 commands and explore others as needed!
