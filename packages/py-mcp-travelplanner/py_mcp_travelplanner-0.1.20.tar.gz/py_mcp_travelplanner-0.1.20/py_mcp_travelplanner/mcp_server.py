"""Unified MCP Server for py_mcp_travelplanner.

This server exposes a unified interface to ALL travel planner services
via the Model Context Protocol. It dynamically discovers and integrates
all subservices (event, flight, hotel, weather, geocoder, finance) and
exposes their tools through a single MCP interface.

The server also provides control tools to start, stop, check health,
and manage the individual travel planner servers.
"""
from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import cli_handlers

LOG = logging.getLogger("py_mcp_travelplanner.mcp_server")

# Create MCP server instance
mcp = Server("py_mcp_travelplanner_unified")

# Registry to track discovered services and their tools
_SERVICE_REGISTRY: Dict[str, Any] = {}
_TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {}


def _discover_subservices() -> List[str]:
    """Discover all available subservice modules.

    Returns:
        List of subservice names (e.g., ['event_server', 'flight_server', ...])
    """
    servers = cli_handlers.list_servers()
    LOG.info(f"Discovered {len(servers)} subservices: {servers}")
    return servers


def _load_subservice_mcp(service_name: str) -> Any:
    """Dynamically import and return the MCP instance from a subservice.

    Args:
        service_name: Name of the service (e.g., 'event_server')

    Returns:
        The FastMCP instance from the service, or None if not found
    """
    if service_name in _SERVICE_REGISTRY:
        return _SERVICE_REGISTRY[service_name]

    try:
        # Try to import the service's main MCP server module
        # Pattern: py_mcp_travelplanner.event_server.event_server (contains 'mcp' instance)
        base_name = service_name.replace('_server', '')
        module_path = f"py_mcp_travelplanner.{service_name}.{base_name}_server"

        LOG.debug(f"Attempting to import {module_path}")
        module = importlib.import_module(module_path)

        if hasattr(module, 'mcp'):
            mcp_instance = module.mcp
            _SERVICE_REGISTRY[service_name] = mcp_instance
            LOG.info(f"Successfully loaded {service_name} MCP instance")
            return mcp_instance
        else:
            LOG.warning(f"Module {module_path} does not have 'mcp' attribute")
            return None

    except Exception as e:
        LOG.warning(f"Failed to load subservice {service_name}: {e}")
        return None


async def _extract_tools_from_subservice(service_name: str, mcp_instance: Any) -> List[Dict[str, Any]]:
    """Extract tool definitions from a subservice MCP instance.

    Args:
        service_name: Name of the service for namespacing
        mcp_instance: The FastMCP instance

    Returns:
        List of tool metadata dicts
    """
    tools = []

    def _normalize_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure array properties have 'items' definitions to satisfy MCP validators.
        If missing, inject a permissive items schema of type 'string'.
        (We choose 'string' as a safe fallback; specific tools can refine further.)"""
        if not isinstance(schema, dict):
            return schema
        if schema.get('type') == 'object':
            props = schema.get('properties', {})
            if isinstance(props, dict):
                for pname, pschema in props.items():
                    if isinstance(pschema, dict) and pschema.get('type') == 'array':
                        if 'items' not in pschema:
                            pschema['items'] = {'type': 'string'}
                        else:
                            items = pschema['items']
                            if isinstance(items, dict) and 'type' not in items and '$ref' not in items:
                                items['type'] = 'string'
        return schema

    try:
        # FastMCP instances have an async list_tools() method
        if hasattr(mcp_instance, 'list_tools'):
            service_tools = await mcp_instance.list_tools()

            for tool in service_tools:
                # Add namespace prefix to avoid collisions
                original_name = tool.name
                namespaced_name = f"{service_name.replace('_server', '')}.{original_name}"

                normalized_schema = _normalize_schema(tool.inputSchema or {})

                tools.append({
                    'service': service_name,
                    'original_name': original_name,
                    'namespaced_name': namespaced_name,
                    'description': tool.description or '',
                    'schema': normalized_schema,
                    'mcp_instance': mcp_instance
                })

                LOG.debug(f"Registered tool: {namespaced_name}")

    except Exception as e:
        LOG.error(f"Failed to extract tools from {service_name}: {e}")

    return tools


async def _initialize_service_registry():
    """Discover and register all subservices and their tools."""
    global _TOOL_REGISTRY

    if _TOOL_REGISTRY:
        # Already initialized
        return

    LOG.info("Initializing unified service registry...")

    services = _discover_subservices()

    for service_name in services:
        mcp_instance = _load_subservice_mcp(service_name)

        if mcp_instance:
            tools = await _extract_tools_from_subservice(service_name, mcp_instance)

            for tool_info in tools:
                _TOOL_REGISTRY[tool_info['namespaced_name']] = tool_info

    LOG.info(f"Initialized {len(_TOOL_REGISTRY)} tools from {len(_SERVICE_REGISTRY)} services")


@mcp.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools for managing travel planner servers and subservice tools."""

    # Initialize service registry on first call
    await _initialize_service_registry()

    # Control/Management tools
    control_tools = [
        Tool(
            name="list_servers",
            description="List all discovered travel planner servers",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_services",
            description="List all integrated subservices and their available tools",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_service_manifest",
            description="Get detailed manifest of all services and their tools",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Optional: specific service name to get manifest for"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="start_server",
            description="Start a specific travel planner server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Name of the server to start (e.g., event_server, flight_server)"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, only show what would be started without actually starting",
                        "default": False
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="start_all_servers",
            description="Start all discovered travel planner servers (requires SERPAPI_KEY)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, only show what would be started without actually starting",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="stop_server",
            description="Stop a running server by name or PID",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Server name or numeric PID to stop"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in seconds to wait for graceful shutdown",
                        "default": 5.0
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="health_check",
            description="Check health of a specific server (verifies main.py exists and is readable)",
            inputSchema={
                "type": "object",
                "properties": {
                    "server": {
                        "type": "string",
                        "description": "Name of the server to check"
                    }
                },
                "required": ["server"]
            }
        ),
        Tool(
            name="get_status",
            description="Get overall status including discovered servers and SERPAPI_KEY presence",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="list_pids",
            description="List all registered server PIDs",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="verify_serpapi_key",
            description="Verify that the SERPAPI_KEY is valid by making a test query",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in seconds for the verification request",
                        "default": 10.0
                    }
                },
                "required": []
            }
        )
    ]

    # Add all subservice tools with namespaced names
    subservice_tools = []
    for tool_name, tool_info in _TOOL_REGISTRY.items():
        subservice_tools.append(
            Tool(
                name=tool_name,
                description=f"[{tool_info['service']}] {tool_info['description']}",
                inputSchema=tool_info['schema']
            )
        )

    LOG.info(f"Listing {len(control_tools)} control tools and {len(subservice_tools)} subservice tools")

    return control_tools + subservice_tools


@mcp.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls for server management and subservice tools."""

    # Control/Management tools
    if name == "list_servers":
        servers = cli_handlers.list_servers()
        return [TextContent(
            type="text",
            text=f"Discovered servers: {', '.join(servers) if servers else 'None'}"
        )]

    elif name == "list_services":
        await _initialize_service_registry()

        services_info = []
        for service_name, mcp_instance in _SERVICE_REGISTRY.items():
            service_tools = [t for t in _TOOL_REGISTRY.values() if t['service'] == service_name]
            tool_names = [t['original_name'] for t in service_tools]
            services_info.append(f"  - {service_name}: {len(tool_names)} tools ({', '.join(tool_names)})")

        text = f"Integrated Services ({len(_SERVICE_REGISTRY)}):\n" + "\n".join(services_info)
        return [TextContent(type="text", text=text)]

    elif name == "get_service_manifest":
        await _initialize_service_registry()

        service_filter = arguments.get("service")

        manifest = {
            "unified_server": "py_mcp_travelplanner_unified",
            "total_services": len(_SERVICE_REGISTRY),
            "total_tools": len(_TOOL_REGISTRY),
            "services": {}
        }

        for service_name, mcp_instance in _SERVICE_REGISTRY.items():
            if service_filter and service_filter != service_name:
                continue

            service_tools = [t for t in _TOOL_REGISTRY.values() if t['service'] == service_name]

            manifest["services"][service_name] = {
                "tool_count": len(service_tools),
                "tools": [
                    {
                        "name": t['namespaced_name'],
                        "original_name": t['original_name'],
                        "description": t['description']
                    }
                    for t in service_tools
                ]
            }

        import json
        return [TextContent(type="text", text=json.dumps(manifest, indent=2))]

    elif name == "start_server":
        server = arguments["server"]
        dry_run = arguments.get("dry_run", False)
        env_overrides = None

        # Try to get SERPAPI_KEY for server environment
        serpapi_key = cli_handlers._resolve_serpapi_key()
        if serpapi_key:
            env_overrides = {"SERPAPI_KEY": serpapi_key}

        ok = cli_handlers.start_server(server, dry_run=dry_run, env_overrides=env_overrides)
        result = f"Server '{server}' {'would be started' if dry_run else 'started'}: {ok}"

        if ok and not dry_run:
            pid = cli_handlers.get_registered_pid(server)
            result += f" (PID: {pid})" if pid else ""

        return [TextContent(type="text", text=result)]

    elif name == "start_all_servers":
        dry_run = arguments.get("dry_run", False)
        try:
            results = cli_handlers.start_all_servers(dry_run=dry_run)
            summary = "\n".join([f"  - {name}: {'started' if ok else 'failed'}" for name, ok in results.items()])
            text = f"Start all servers {'(dry-run)' if dry_run else ''}:\n{summary}"
            return [TextContent(type="text", text=text)]
        except RuntimeError as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    elif name == "stop_server":
        server = arguments["server"]
        timeout = arguments.get("timeout", 5.0)

        # Try to parse as PID
        try:
            server_val = int(server)
        except ValueError:
            server_val = server

        result = cli_handlers.stop_server(server_val, timeout=timeout)
        text = f"Stop server '{server}': ok={result.get('ok')}, pid={result.get('pid')}"
        if "error" in result:
            text += f", error={result['error']}"

        return [TextContent(type="text", text=text)]

    elif name == "health_check":
        server = arguments["server"]
        ok = cli_handlers.health_check(server)
        return [TextContent(type="text", text=f"Health check '{server}': {'healthy' if ok else 'unhealthy'}")]

    elif name == "get_status":
        await _initialize_service_registry()

        servers = [p.name for p in cli_handlers._find_server_dirs()]
        serpapi = cli_handlers._resolve_serpapi_key()
        pids = cli_handlers.list_registered_pids()

        status_text = f"""Status:
  Discovered servers: {len(servers)} ({', '.join(servers) if servers else 'none'})
  Integrated services: {len(_SERVICE_REGISTRY)}
  Available tools: {len(_TOOL_REGISTRY)} subservice tools + 10 control tools
  SERPAPI_KEY: {'present' if serpapi else 'missing'}
  Running servers: {len(pids)} ({', '.join(pids.keys()) if pids else 'none'})"""

        return [TextContent(type="text", text=status_text)]

    elif name == "list_pids":
        pids = cli_handlers.list_registered_pids()
        if not pids:
            return [TextContent(type="text", text="No registered server PIDs")]

        pid_text = "Registered PIDs:\n"
        for name, info in pids.items():
            pid_text += f"  - {name}: PID={info.get('pid')}, started={info.get('started_at')}\n"

        return [TextContent(type="text", text=pid_text)]

    elif name == "verify_serpapi_key":
        timeout = arguments.get("timeout", 10.0)
        ok, info = cli_handlers.verify_serpapi_key(timeout=timeout)

        if ok:
            text = f"SERPAPI_KEY verification: SUCCESS\n  HTTP status: {info.get('http_status')}\n  Response keys: {info.get('keys')}"
        else:
            text = f"SERPAPI_KEY verification: FAILED\n  Error: {info.get('error', 'unknown')}"

        return [TextContent(type="text", text=text)]

    # Subservice tool delegation
    elif name in _TOOL_REGISTRY:
        tool_info = _TOOL_REGISTRY[name]
        mcp_instance = tool_info['mcp_instance']
        original_name = tool_info['original_name']

        try:
            # Delegate to the subservice's MCP instance
            # FastMCP instances have a call_tool method we can invoke
            if hasattr(mcp_instance, '_tool_manager') and hasattr(mcp_instance._tool_manager, '_tools'):
                # Get the actual tool function (may be a FastMCP Tool wrapper) from FastMCP
                tool_obj = mcp_instance._tool_manager._tools.get(original_name)

                if tool_obj:
                    LOG.info(f"Delegating {name} -> {tool_info['service']}.{original_name}")

                    result = None
                    try:
                        if callable(tool_obj):
                            # Older versions or direct function references
                            result = tool_obj(**arguments)
                            if hasattr(result, '__await__'):
                                result = await result
                        elif hasattr(tool_obj, 'run'):
                            # FastMCP Tool wrapper exposes async run(arguments_dict)
                            run_result = tool_obj.run(arguments)
                            if hasattr(run_result, '__await__'):
                                result = await run_result
                            else:
                                result = run_result
                        else:
                            return [TextContent(type="text", text=f"Unsupported tool wrapper type for {name}: {type(tool_obj)}")]
                    except TypeError as e:
                        # Retry using .run if direct call failed due to signature mismatch
                        if hasattr(tool_obj, 'run'):
                            LOG.debug(f"Direct call failed for {name} ({e}); retrying with .run()")
                            run_result = tool_obj.run(arguments)
                            result = await run_result if hasattr(run_result, '__await__') else run_result
                        else:
                            raise

                    # Convert result to TextContent
                    import json
                    if isinstance(result, dict):
                        result_text = json.dumps(result, indent=2)
                    else:
                        result_text = str(result)

                    return [TextContent(type="text", text=result_text)]
                else:
                    return [TextContent(type="text", text=f"Tool function not found: {original_name}")]
            else:
                return [TextContent(type="text", text=f"Cannot delegate to {tool_info['service']}: unsupported MCP instance")]

        except Exception as e:
            LOG.exception(f"Error calling subservice tool {name}: {e}")
            return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def serve_mcp():
    """Run the unified MCP server via stdio."""
    LOG.info("Starting unified MCP server...")
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())


def run_mcp_server():
    """Synchronous entry point for running the MCP server."""
    import asyncio
    asyncio.run(serve_mcp())


if __name__ == "__main__":
    run_mcp_server()
