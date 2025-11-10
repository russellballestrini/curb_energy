# Curb Energy API Server

Modern FastAPI server for exposing your Curb energy monitoring data as a REST API with LLM tool calling support.

## 🚀 Quick Start

### Installation

```bash
# Install with server dependencies
pip install -e ".[server]"

# Or install everything (including dev tools)
pip install -e ".[all]"
```

### Configuration

Set up authentication using environment variables:

```bash
export CURB_USERNAME="your_curb_username"
export CURB_PASSWORD="your_curb_password"
export CURB_CLIENT_TOKEN="your_oauth_client_token"
export CURB_CLIENT_SECRET="your_oauth_client_secret"
```

> **Note:** You need to obtain OAuth client credentials from Curb. See [Curb API Authentication](http://docs.energycurb.com/authentication.html) for details.

### Start the Server

```bash
# Using the command-line tool
curb-server

# Or using Python directly
python -m uvicorn curb_energy.server:app --reload

# Or from the module
python -m curb_energy.server
```

The server will start on `http://localhost:8000`

## 📖 API Documentation

Once the server is running, access:

- **Interactive API Docs (Swagger UI):** http://localhost:8000/docs
- **API Reference (ReDoc):** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json
- **Dashboard:** http://localhost:8000

## 🔌 API Endpoints

### Authentication

```http
POST /auth/configure
```
Configure authentication credentials programmatically.

### Energy Data

```http
GET /profiles
```
Get all energy monitoring profiles (locations) for your account.

```http
GET /devices
```
Get all energy monitoring devices.

```http
GET /energy/today?profile_id=123
```
Get today's energy usage for a specific profile.

```http
GET /energy/week?profile_id=123
```
Get the past week's energy usage.

```http
POST /energy/historical
Content-Type: application/json

{
  "profile_id": 123,
  "hours_back": 48,
  "granularity": "1H",
  "unit": "w"
}
```
Get historical energy data with custom parameters.

### LLM Integration

```http
GET /llm/tools
```
Get LLM-friendly function schemas for tool calling.

## 🤖 Using with LLMs

### Anthropic Claude

```python
import anthropic
from curb_energy.server import CurbEnergyLLMTools

tools = CurbEnergyLLMTools()
client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=tools.get_tool_schemas(),
    messages=[{"role": "user", "content": "What's my energy usage today?"}]
)

# Claude will use the tools to access your energy data
```

### OpenAI GPT-4

```python
import openai
from curb_energy.server import CurbEnergyLLMTools

tools = CurbEnergyLLMTools()

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Show me my energy consumption this week"}
    ],
    functions=tools.get_tool_schemas(),
    function_call="auto"
)
```

### Example Prompts

When using LLMs with the Curb Energy API, you can ask questions like:

- "What's my current energy usage?"
- "How much electricity did I use today?"
- "Show me my power consumption for the past week"
- "What was my peak usage yesterday?"
- "How much money am I spending on electricity this month?"
- "Which devices are using the most power?"

## 🌐 Web Dashboard

A responsive web dashboard is included at `examples/dashboard.html`. To use it:

1. Start the API server
2. Open `examples/dashboard.html` in your browser
3. Configure the API URL (default: http://localhost:8000)
4. Load your profiles and view your energy data

Features:
- 📊 Real-time energy usage statistics
- 📈 Interactive charts and graphs
- 📱 Responsive design for mobile and desktop
- 🎨 Modern, clean interface

## 🔧 Advanced Configuration

### Custom Port

```bash
uvicorn curb_energy.server:app --host 0.0.0.0 --port 8080
```

### CORS Configuration

By default, CORS is enabled for all origins. In production, restrict this by modifying `server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify your domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production Deployment

For production use:

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn curb_energy.server:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
```

## 📦 Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip install -e ".[server]"

ENV CURB_USERNAME=""
ENV CURB_PASSWORD=""
ENV CURB_CLIENT_TOKEN=""
ENV CURB_CLIENT_SECRET=""

EXPOSE 8000

CMD ["curb-server"]
```

Build and run:

```bash
docker build -t curb-energy-api .
docker run -p 8000:8000 \
    -e CURB_USERNAME=your_username \
    -e CURB_PASSWORD=your_password \
    -e CURB_CLIENT_TOKEN=your_token \
    -e CURB_CLIENT_SECRET=your_secret \
    curb-energy-api
```

## 🔍 API Usage Examples

### Python

```python
import requests

# Get profiles
response = requests.get("http://localhost:8000/profiles")
profiles = response.json()

# Get today's energy usage
response = requests.get(
    "http://localhost:8000/energy/today",
    params={"profile_id": profiles[0]["id"]}
)
data = response.json()
print(data)
```

### JavaScript

```javascript
// Fetch profiles
fetch('http://localhost:8000/profiles')
    .then(response => response.json())
    .then(profiles => {
        console.log('My profiles:', profiles);

        // Get today's energy for first profile
        return fetch(`http://localhost:8000/energy/today?profile_id=${profiles[0].id}`);
    })
    .then(response => response.json())
    .then(data => {
        console.log('Today\'s energy:', data);
    });
```

### cURL

```bash
# Get profiles
curl http://localhost:8000/profiles

# Get today's energy
curl "http://localhost:8000/energy/today?profile_id=123"

# Get historical data
curl -X POST http://localhost:8000/energy/historical \
    -H "Content-Type: application/json" \
    -d '{"profile_id": 123, "hours_back": 24, "granularity": "1H"}'
```

## 🛠️ Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=curb_energy --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

## 📚 Resources

- [Curb Energy Official Docs](http://docs.energycurb.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Anthropic Claude Tool Calling](https://docs.anthropic.com/claude/docs/tool-use)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

Apache License 2.0 - see LICENSE file for details.
