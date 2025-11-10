import asyncio
import pytest

from py_mcp_travelplanner.mcp_server import _initialize_service_registry, _TOOL_REGISTRY

@pytest.mark.asyncio
async def test_tool_array_properties_have_items():
    """Ensure every tool schema with array-typed properties defines 'items'.

    This guards against the MCP validation error: 'tool parameters array type must have items'.
    """
    await _initialize_service_registry()

    failures = []
    for tool_name, info in _TOOL_REGISTRY.items():
        schema = info.get('schema', {})
        if schema.get('type') != 'object':
            continue
        properties = schema.get('properties', {})
        for prop, prop_schema in properties.items():
            if not isinstance(prop_schema, dict):
                continue
            if prop_schema.get('type') == 'array':
                if 'items' not in prop_schema:
                    failures.append(f"{tool_name}.{prop} missing 'items' definition")
                else:
                    items = prop_schema['items']
                    if isinstance(items, dict):
                        if 'type' not in items and '$ref' not in items:
                            failures.append(f"{tool_name}.{prop} items missing 'type' or '$ref'")
                    else:
                        failures.append(f"{tool_name}.{prop} items is not a dict")
    assert not failures, 'Array properties missing items schema:\n' + '\n'.join(failures)

