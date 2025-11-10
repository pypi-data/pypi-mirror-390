# MCP Travel Planner

**A unified MCP (Model Context Protocol) server providing a single entry point to comprehensive travel planning services.**

This project implements ONE unified MCP server that orchestrates multiple travel-related backend services (flights, hotels, weather, geocoding, events, finance). MCP clients like Claude Desktop connect to a single server interface and access all travel planning capabilities through it.

## Key Features

- **Single MCP Server Entry Point**: One unified server (`mcp_server.py`) for all travel services
- **Service Orchestration**: Manages multiple backend services through one interface  
- **MCP Tools**: Expose travel planning capabilities via Model Context Protocol
- **Claude Desktop Integration**: Ready-to-use configuration for Claude Desktop
- **Modular Backend**: Each service runs independently but is coordinated by the unified server
- **Runtime Configuration**: Multi-source config with env vars, .env, and YAML support

## Quick Start

**Ready-to-use MCP configuration examples** are provided in the `examples/` directory:

- **`claude_desktop_config_uv_testpypi.json`** - Run from Test PyPI with UV (no installation)
- **`claude_desktop_config_uv_pypi.json`** - Run from PyPI with UV (stable release)
- **`claude_desktop_config_template.json`** - Standard Python installation

See [`examples/QUICK_REFERENCE.md`](examples/QUICK_REFERENCE.md) for copy-paste configs and [`examples/MCP_CONFIG_README.md`](examples/MCP_CONFIG_README.md) for complete documentation.

## Configuration

The project uses a **multi-source runtime configuration system** with proper precedence:

1. **Environment variables** (highest priority)
2. **.env file**
3. **runtime_config.yaml**
4. **Default values** (lowest priority)

See [`docs/CONFIG_README.md`](docs/CONFIG_README.md) for complete configuration documentation.

## Architecture

```
MCP Client (Claude Desktop) 
        ↓ (stdio)
Unified MCP Server (single entry point)
        ↓ (orchestrates)
Backend Services (flight, hotel, weather, geocoder, finance, events)
```

## Status

- Prototype / Proof-of-Concept. Intended for local development, experimentation, and as a reference implementation for orchestration patterns.

## Key Concepts

- Modular microservice-style servers implemented as small Python scripts under `py_mcp_travelplanner/`.
- Each service lives in its own folder (for example `flight_server/`, `hotel_server/`, `weather_server/`) with a `main.py` or server entrypoint.
- A small CLI and control server are provided for orchestration and to demonstrate inter-service interactions.

## Contents

- `py_mcp_travelplanner/` — main package containing CLI, control server and per-service folders.
  - `flight_server/`, `hotel_server/`, `weather_server/`, `geocoder_server/`, `event_server/`, `finance_server/` — example service implementations.
- `requirements.txt` — pinned runtime/dev dependencies used by the project.
- `tests/` — pytest-based unit tests and lifecycle tests.
- `examples/` — MCP configuration examples for Claude Desktop and other clients.

## Quick Start (Local Development)

### Prerequisites

- Linux / macOS / Windows with WSL
- Python 3.12.1 or later is recommended for development

### Recommended: Create and use a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Install dependencies

**Option A — pip (quick)**

```bash
pip install -r requirements.txt
```

**Option B — poetry (if you prefer pyproject/poetry workflows)**

```bash
poetry install
```

### Running services

Each server folder contains a runnable entrypoint (usually `main.py`). From the repository root you can start any server directly with Python. For example:

```bash
# run the flight server
python py_mcp_travelplanner/flight_server/main.py

# run the weather server
python py_mcp_travelplanner/weather_server/main.py

# run the control server (if present)
python py_mcp_travelplanner/control_server.py
```

**Note:** Some servers may expect environment variables or API keys; check the server's README under the corresponding server folder for provider-specific setup.

## Unified MCP Server — Access All Services Through One Interface

The **unified MCP server** (`py_mcp_travelplanner/mcp_server.py`) provides a single entry point to all travel planning services. Instead of running and configuring multiple separate MCP servers, you can use ONE server that automatically discovers and integrates all available subservices.

### Key Benefits

- **Single Connection**: MCP clients connect to one server instead of six
- **Auto-Discovery**: Automatically finds and loads all available services
- **Namespaced Tools**: Clear tool organization (e.g., `event.search_events`, `flight.search_flights`)
- **Service Management**: Start, stop, and monitor subservices through MCP tools
- **Unified Interface**: Consistent access patterns across all travel services

### Running the Unified Server

```bash
# Run the unified MCP server
python -m py_mcp_travelplanner.mcp_server

# Or via CLI
py-mcp-travel unified
```

### Available Services & Tools

The unified server integrates:

| Service | Tools | Description |
|---------|-------|-------------|
| **event** | `search_events`, `get_event_details`, `list_events` | Event search and discovery |
| **flight** | `search_flights`, `get_flight_details`, `list_flights` | Flight search and booking |
| **hotel** | `search_hotels`, `get_hotel_details`, `list_hotels` | Hotel search and reservations |
| **weather** | `get_weather`, `get_forecast` | Weather forecasts |
| **geocoder** | `geocode`, `reverse_geocode` | Location geocoding |
| **finance** | `get_exchange_rates`, `convert_currency` | Currency exchange |

### Management Tools

- `list_services` - Show all integrated services and their tools
- `get_service_manifest` - Get detailed JSON manifest of all services
- `get_status` - Overall system status
- `start_server` / `stop_server` - Manage individual subservices
- `health_check` - Check service health

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "travel_planner_local": {
      "command": "python",
      "args": ["-m", "py_mcp_travelplanner.mcp_server"],
      "env": {
        "SERPAPI_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Example Usage

Once connected, use namespaced tool names:

```python
# Search for events in New York
event.search_events({
  "query": "concerts",
  "location": "New York",
  "date_filter": "week"
})

# Search for flights
flight.search_flights({
  "departure_id": "JFK",
  "arrival_id": "LAX",
  "outbound_date": "2025-06-15"
})

# Get weather forecast
weather.get_forecast({
  "location": "New York",
  "days": 7
})
```

### Documentation

For complete details about the unified server architecture, see **[docs/UNIFIED_SERVER.md](docs/UNIFIED_SERVER.md)**.

### CLI

# run the weather server
python py_mcp_travelplanner/weather_server/main.py

# run the control server (if present)
python py_mcp_travelplanner/control_server.py
```

**Note:** Some servers may expect environment variables or API keys; check the server's README under the corresponding server folder for provider-specific setup.

### CLI

A simple CLI is available under `py_mcp_travelplanner/cli.py` and `py_mcp_travelplanner/cli_handlers.py`. You can run the CLI script to access helper commands used in development:

```bash
python -m py_mcp_travelplanner.cli
```

(If the package isn't installed as a module, run the file directly: `python py_mcp_travelplanner/cli.py`.)

## Unified MCP Server — Single Entry Point Architecture

This project provides **ONE unified MCP server** that acts as a single entry point to all travel planner services. The server is located at `py_mcp_travelplanner/mcp_server.py` and orchestrates all backend services (flights, hotels, weather, geocoding, events, finance) through a single Model Context Protocol interface.

### Architecture Overview

- **Single MCP Server**: One unified server exposing all travel planning capabilities
- **Service Orchestration**: The MCP server manages and coordinates multiple backend services
- **Unified Interface**: MCP clients connect to one server and access all travel services through it

## MCP Server Configuration

### For Claude Desktop and MCP Clients

Ready-to-use configuration files are provided in the `examples/` directory:

**Option 1: UV with Test PyPI** (recommended for testing)
```json
{
  "mcpServers": {
    "py_mcp_travelplanner_testpypi": {
      "command": "uv",
      "args": [
        "run",
        "--index",
        "https://test.pypi.org/simple",
        "--with",
        "py_mcp_travelplanner",
        "--no-project",
        "--",
        "py_mcp_travelplanner_cli"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

**Option 2: UV with PyPI** (stable release)
```json
{
  "mcpServers": {
    "py_mcp_travelplanner": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "py_mcp_travelplanner",
        "--no-project",
        "--",
        "py_mcp_travelplanner_cli"
      ],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

**Option 3: Local Installation**
```json
{
  "mcpServers": {
    "py_mcp_travelplanner": {
      "command": "python",
      "args": ["-m", "py_mcp_travelplanner.mcp_server"],
      "env": {
        "SERPAPI_KEY": "your_serpapi_key_here"
      }
    }
  }
}
```

**Configuration locations by OS:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

See [`examples/MCP_CONFIG_README.md`](examples/MCP_CONFIG_README.md) for complete setup instructions.

### Environment Variables

Set these in the MCP config `env` section or in your shell:

**Required:**
- `SERPAPI_KEY` - Your SerpAPI key (get from https://serpapi.com/)

**Optional (with defaults):**
- `LOG_LEVEL` - `DEBUG`, `INFO`, `WARNING`, `ERROR` (default: `INFO`)
- `CONTROL_SERVER_PORT` - Server port (default: `8787`)
- `DEBUG_MODE` - Enable debug mode: `true`/`false` (default: `false`)
- `DRY_RUN` - Test mode without side effects: `true`/`false` (default: `false`)

See [`docs/CONFIG_README.md`](docs/CONFIG_README.md) for all configuration options.

### What the unified MCP server exposes

- **Tools**: `list_servers`, `start_server`, `start_all_servers`, `stop_server`, `health_check`, `get_status`, `list_pids`, `verify_serpapi_key`
- **Services**: event_server, finance_server, flight_server, geocoder_server, hotel_server, weather_server
- Each tool accepts a JSON-like arguments object and returns TextContent responses

## Running the MCP Server

### Method 1: With Claude Desktop (Recommended)

1. **Get a SERPAPI key** from https://serpapi.com/ (free tier: 100 searches/month)

2. **Choose a configuration** from `examples/`:
   - For testing: `claude_desktop_config_uv_testpypi.json`
   - For production: `claude_desktop_config_uv_pypi.json`
   - For local dev: `claude_desktop_config_template.json`

3. **Copy to Claude Desktop config location** (see paths above)

4. **Edit the config** and replace `your_serpapi_key_here` with your actual key

5. **Restart Claude Desktop**

The travel planner tools will now be available in your Claude conversations!

### Method 2: Direct Execution (for testing)

```bash
# Start the unified MCP server
python -m py_mcp_travelplanner.mcp_server

# Or use the CLI helper
python -m py_mcp_travelplanner.cli mcp
```

## Available MCP Tools

When connected to the unified MCP server, you'll have access to these tools:

- **list_servers**: List all available travel service backends
- **start_server**: Start a specific service (event, flight, hotel, weather, etc.)
- **start_all_servers**: Start all services at once
- **stop_server**: Stop a running service by name or PID
- **health_check**: Verify a service is healthy and ready
- **get_status**: Get overall system status and running services
- **list_pids**: List all running service process IDs
- **verify_serpapi_key**: Test if SERPAPI_KEY is configured correctly

### Tool call JSON examples (conceptual)

When calling a tool via an MCP client you will call the tool by name and pass the corresponding arguments object. The exact outer envelope depends on the MCP client library you use; below are the argument payloads for the most common operations:

- Start a server (dry run):
```json
{ "server": "flight_server", "dry_run": true }
```

- Start a server (actual start):
```json
{ "server": "flight_server", "dry_run": false }
```

- Start all servers (dry run):
```json
{ "dry_run": true }
```

- Stop a server (by name):
```json
{ "server": "flight_server", "timeout": 5.0 }
```

- Stop a server (by PID):
```json
{ "server": 12345, "timeout": 5.0 }
```

- Health check:
```json
{ "server": "flight_server" }
```

- Get overall status (no arguments):
```json
{}
```

### Expected responses

The server returns an array of TextContent objects (the `mcp` library encodes this). When using an MCP client, you should inspect the returned text field(s). For example a `get_status` call may return a single element whose `text` contains a human-readable status summary.

## HTTP Control Server (Concrete, Scriptable)

For convenience there is a small HTTP control server (`py_mcp_travelplanner/control_server.py`) that wraps a subset of the MCP server functionality and exposes simple HTTP endpoints. This is recommended for quick scripting and interactive use.

### Start the control server (background)

```bash
python py_mcp_travelplanner/control_server.py
# or, using the CLI helper
python -m py_mcp_travelplanner.cli serve --host 127.0.0.1 --port 8787
```

### Useful curl examples

- Get status (discovered servers + SERPAPI presence):
```bash
curl -s http://127.0.0.1:8787/status | jq
```

- Health check for a server:
```bash
curl -s "http://127.0.0.1:8787/health?server=flight_server" | jq
```

- Start a single server (dry run):
```bash
curl -X POST "http://127.0.0.1:8787/start?server=flight_server&dry=true" | jq
```

- Start all servers (actual start):
```bash
curl -X POST "http://127.0.0.1:8787/start_all?dry=false" | jq
```

- Stop a server by name:
```bash
curl -X POST "http://127.0.0.1:8787/stop?server=flight_server" | jq
```

- List registered PIDs:
```bash
curl -s http://127.0.0.1:8787/pids | jq
```

- Verify SERPAPI_KEY (performs a test request using the configured key):
```bash
curl -X POST http://127.0.0.1:8787/test_key | jq
```

### Python example

```python
import requests

BASE = "http://127.0.0.1:8787"

# get status
print(requests.get(f"{BASE}/status").json())

# start flight server (dry-run)
print(requests.post(f"{BASE}/start?server=flight_server&dry=true").json())

# start all
print(requests.post(f"{BASE}/start_all?dry=false").json())

# verify serpapi
print(requests.post(f"{BASE}/test_key").json())
```

## Advanced Usage: Multi-Server Orchestration & HTTP API

### Running Individual Servers (stdio or HTTP)

Each backend server (weather, event, hotel, flight, finance, geocoder) can be started with either stdio (default) or HTTP transport, and exposes a manifest for tool discovery:

```bash
# Start weather server with HTTP API
python -m py_mcp_travelplanner.weather_server.main --transport http --host 127.0.0.1 --port 8791

# Start event server with stdio (default)
python -m py_mcp_travelplanner.event_server.main

# Print tool manifest/schema for debugging
python -m py_mcp_travelplanner.weather_server.main --manifest
```

### Unified Launcher Script

You can launch all servers from a single config file (YAML or JSON) using the provided script:

```bash
python scripts/run_mcp_from_config.py --config runtime_config.yaml
```

Example config (runtime_config.yaml):
```yaml
servers:
  weather:
    enabled: true
    transport: http
    host: 127.0.0.1
    port: 8791
  event:
    enabled: true
    transport: http
    host: 127.0.0.1
    port: 8796
  hotel:
    enabled: true
    transport: http
    host: 127.0.0.1
    port: 8795
  flight:
    enabled: true
    transport: http
    host: 127.0.0.1
    port: 8793
  finance:
    enabled: true
    transport: http
    host: 127.0.0.1
    port: 8792
  geocoder:
    enabled: true
    transport: http
    host: 127.0.0.1
    port: 8794
SERPAPI_KEY: "your_serpapi_key_here"
```

This will launch all enabled servers with the specified transport and ports. Press Ctrl+C to stop all servers.

### Integration Testing: HTTP Endpoints & Manifest

You can test HTTP endpoints and manifest output for any server:

```bash
# Test weather server HTTP endpoint
curl http://127.0.0.1:8791/manifest

# Or print manifest to stdout
python -m py_mcp_travelplanner.weather_server.main --manifest
```

You can also write integration tests in pytest to verify HTTP endpoints and manifest output. See the 'tests/' folder for examples.

## Tests

Run the test suite with pytest:

```bash
# Run all tests
pytest -q

# Run MCP server tests specifically
pytest tests/test_mcp_server.py -v

# Run with coverage
pytest --cov=py_mcp_travelplanner --cov-report=html
```

**Test Coverage**:
- **MCP Server Tests**: 25 tests covering all 8 tools, initialization, and workflows
- **Config Tests**: 28 tests covering runtime configuration system
- **Total**: 58 tests passing

## Development Notes (Important)

### 1) Consolidate pyproject files

The repository currently contains service-level metadata and possibly extra `pyproject.toml` files inside server folders. For a single-source-of-truth dependency management approach, consolidate those service-level `pyproject.toml` contents into the root `pyproject.toml` and remove or archive the per-server `pyproject.toml` files. This simplifies CI, local dependency installation, and version pinning.

### 2) Harmonize shared dependencies (requests example)

Several service folders may declare their own `requests` version. To avoid mismatched runtime behavior, pin `requests` at the root `pyproject.toml` (or `requirements.txt`) to a single compatible version range and update any server-specific files to rely on the root manifest.

### 3) Python compatibility and dependency constraints

Some dependencies in the ecosystem (for example `openapi-pydantic`) declare compatibility for Python versions `<4.0,>=3.8`. To remain compatible with such packages while still using modern Python, set the project Python requirement to a range that excludes Python 4.0. For example in `pyproject.toml` set:

```toml
python = ">=3.12.1,<4.0"
```

This avoids dependency resolution errors if someone installs or runs the project on Python 4.x while the dependencies do not declare support for it.

### 4) Harmonize dependency versions across the monorepo

When merging per-server manifests, ensure shared libraries (requests, aiohttp, pydantic, etc.) are pinned consistently. Run a dependency resolver (pip-tools, poetry) and test local execution after changes.

## Troubleshooting

- If a server fails to start due to missing environment variables or API keys, check the server folder README for provider-specific instructions.
- If you hit dependency resolution errors, run `pip check` or `poetry lock` to see conflicts and adjust the root manifest accordingly.

## Contributing

- Fork the repository, create a feature branch, and open a pull request against the main branch.
- Keep changes focused: if you're changing dependencies, update `pyproject.toml`/`requirements.txt` and add a short rationale in the PR summary.
- Run tests locally and ensure linting passes before opening a PR.

## License

See the `LICENSE` file in the repository root.

## Acknowledgements

This repository is a learning / POC project showcasing modular service layouts, simple orchestration, and packaging considerations for small multi-service Python projects.

## Contact

For questions or help, open an issue in this repository with details about your environment and the problem you're encountering.
