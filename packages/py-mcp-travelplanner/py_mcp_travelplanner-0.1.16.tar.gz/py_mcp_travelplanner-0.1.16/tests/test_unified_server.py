"""Test the unified MCP server integration."""
import pytest
from py_mcp_travelplanner import mcp_server


def test_discover_subservices():
    """Test that subservices can be discovered."""
    services = mcp_server._discover_subservices()

    # Should find at least the known servers
    assert isinstance(services, list)
    assert len(services) > 0

    # Check for expected services
    expected_services = {'event_server', 'flight_server', 'hotel_server', 'weather_server', 'geocoder_server', 'finance_server'}
    found_services = set(services)

    # At least some of the expected services should be found
    assert len(expected_services & found_services) >= 3, f"Expected to find services from {expected_services}, got {found_services}"


@pytest.mark.asyncio
async def test_initialize_service_registry():
    """Test that service registry initialization works."""
    # Clear registries first
    mcp_server._SERVICE_REGISTRY.clear()
    mcp_server._TOOL_REGISTRY.clear()

    await mcp_server._initialize_service_registry()

    # Should have discovered and registered services
    assert len(mcp_server._SERVICE_REGISTRY) > 0, "Should have loaded at least one service"
    assert len(mcp_server._TOOL_REGISTRY) > 0, "Should have registered at least one tool"

    # Check that tools are properly namespaced
    for tool_name in mcp_server._TOOL_REGISTRY.keys():
        assert '.' in tool_name, f"Tool {tool_name} should be namespaced with format 'service.tool_name'"


@pytest.mark.asyncio
async def test_service_registry_has_valid_structure():
    """Test that registered tools have the expected structure."""
    await mcp_server._initialize_service_registry()

    for tool_name, tool_info in mcp_server._TOOL_REGISTRY.items():
        # Each tool should have required fields
        assert 'service' in tool_info
        assert 'original_name' in tool_info
        assert 'namespaced_name' in tool_info
        assert 'description' in tool_info
        assert 'schema' in tool_info
        assert 'mcp_instance' in tool_info

        # Namespaced name should match the key
        assert tool_info['namespaced_name'] == tool_name


@pytest.mark.asyncio
async def test_list_tools_includes_subservices():
    """Test that list_tools returns both control and subservice tools."""
    tools = await mcp_server.list_tools()

    assert len(tools) > 10, "Should have at least 10 control tools plus subservice tools"

    # Check for control tools
    control_tool_names = {t.name for t in tools}
    assert 'list_servers' in control_tool_names
    assert 'list_services' in control_tool_names
    assert 'get_service_manifest' in control_tool_names
    assert 'get_status' in control_tool_names

    # Check for at least one namespaced subservice tool (format: service.tool_name)
    namespaced_tools = [t.name for t in tools if '.' in t.name]
    assert len(namespaced_tools) > 0, "Should have at least one subservice tool with namespace"


@pytest.mark.asyncio
async def test_list_services_tool():
    """Test the list_services tool."""
    result = await mcp_server.call_tool("list_services", {})

    assert len(result) == 1
    assert result[0].type == "text"

    text = result[0].text
    assert "Integrated Services" in text
    assert "tools" in text.lower()


@pytest.mark.asyncio
async def test_get_service_manifest_tool():
    """Test the get_service_manifest tool."""
    result = await mcp_server.call_tool("get_service_manifest", {})

    assert len(result) == 1
    assert result[0].type == "text"

    import json
    manifest = json.loads(result[0].text)

    assert "unified_server" in manifest
    assert manifest["unified_server"] == "py_mcp_travelplanner_unified"
    assert "total_services" in manifest
    assert "total_tools" in manifest
    assert "services" in manifest
    assert isinstance(manifest["services"], dict)


@pytest.mark.asyncio
async def test_get_status_includes_integration_info():
    """Test that get_status shows integrated services."""
    result = await mcp_server.call_tool("get_status", {})

    assert len(result) == 1
    text = result[0].text

    assert "Integrated services:" in text
    assert "Available tools:" in text
    assert "subservice tools" in text


@pytest.mark.asyncio
async def test_tool_registry_persistence():
    """Test that the tool registry persists across calls."""
    # Initialize once
    await mcp_server._initialize_service_registry()
    initial_count = len(mcp_server._TOOL_REGISTRY)

    # Call again - should not reinitialize
    await mcp_server._initialize_service_registry()
    second_count = len(mcp_server._TOOL_REGISTRY)

    assert initial_count == second_count, "Registry should not be reinitialized"
    assert initial_count > 0, "Registry should have tools"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

