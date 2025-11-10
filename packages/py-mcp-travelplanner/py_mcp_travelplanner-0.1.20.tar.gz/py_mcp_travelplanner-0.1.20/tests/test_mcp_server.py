"""Tests for the unified MCP server.

This test suite covers:
- Tool listing and registration
- Tool call handling for all available tools
- Server initialization and configuration
- Error handling and edge cases
"""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Configure pytest-asyncio to auto mode
pytestmark = pytest.mark.asyncio(loop_scope="function")

# Import the MCP server module
from py_mcp_travelplanner import mcp_server


class TestMCPServerTools:
    """Test suite for MCP server tool registration and listing."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Verify that list_tools returns all 8 expected tools."""
        tools = await mcp_server.list_tools()
        
        assert len(tools) == 8, f"Expected 8 tools, got {len(tools)}"
        
        tool_names = {tool.name for tool in tools}
        expected_tools = {
            "list_servers",
            "start_server",
            "start_all_servers",
            "stop_server",
            "health_check",
            "get_status",
            "list_pids",
            "verify_serpapi_key"
        }
        
        assert tool_names == expected_tools, f"Tool mismatch: {tool_names} vs {expected_tools}"

    @pytest.mark.asyncio
    async def test_list_servers_tool_schema(self):
        """Verify list_servers tool has correct schema."""
        tools = await mcp_server.list_tools()
        list_servers_tool = next(t for t in tools if t.name == "list_servers")
        
        assert list_servers_tool.description == "List all discovered travel planner servers"
        assert list_servers_tool.inputSchema["type"] == "object"
        assert list_servers_tool.inputSchema["required"] == []

    @pytest.mark.asyncio
    async def test_start_server_tool_schema(self):
        """Verify start_server tool has correct schema."""
        tools = await mcp_server.list_tools()
        start_server_tool = next(t for t in tools if t.name == "start_server")
        
        assert "Start a specific travel planner server" in start_server_tool.description
        assert "server" in start_server_tool.inputSchema["properties"]
        assert "dry_run" in start_server_tool.inputSchema["properties"]
        assert start_server_tool.inputSchema["required"] == ["server"]


class TestMCPServerToolCalls:
    """Test suite for MCP server tool call handling."""

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.list_servers')
    async def test_call_tool_list_servers(self, mock_list_servers):
        """Test list_servers tool call."""
        mock_list_servers.return_value = ["event_server", "flight_server", "hotel_server"]
        
        result = await mcp_server.call_tool("list_servers", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "event_server" in result[0].text
        assert "flight_server" in result[0].text
        assert "hotel_server" in result[0].text
        mock_list_servers.assert_called_once()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.start_server')
    @patch('py_mcp_travelplanner.cli_handlers._resolve_serpapi_key')
    async def test_call_tool_start_server_success(self, mock_resolve_key, mock_start_server):
        """Test start_server tool call with successful start."""
        mock_resolve_key.return_value = "test_api_key"
        mock_start_server.return_value = True
        
        result = await mcp_server.call_tool("start_server", {
            "server": "flight_server",
            "dry_run": False
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "flight_server" in result[0].text
        assert "True" in result[0].text or "started" in result[0].text.lower()
        mock_start_server.assert_called_once()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.start_server')
    async def test_call_tool_start_server_dry_run(self, mock_start_server):
        """Test start_server tool call with dry_run."""
        mock_start_server.return_value = True
        
        result = await mcp_server.call_tool("start_server", {
            "server": "weather_server",
            "dry_run": True
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "would be started" in result[0].text or "dry" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.start_all_servers')
    async def test_call_tool_start_all_servers(self, mock_start_all):
        """Test start_all_servers tool call."""
        mock_start_all.return_value = {
            "event_server": True,
            "flight_server": True,
            "hotel_server": True
        }
        
        result = await mcp_server.call_tool("start_all_servers", {"dry_run": False})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "event_server" in result[0].text
        assert "started" in result[0].text.lower()
        mock_start_all.assert_called_once_with(dry_run=False)

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.start_all_servers')
    async def test_call_tool_start_all_servers_with_error(self, mock_start_all):
        """Test start_all_servers tool call when an error occurs."""
        mock_start_all.side_effect = RuntimeError("SERPAPI_KEY not found")
        
        result = await mcp_server.call_tool("start_all_servers", {"dry_run": False})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error" in result[0].text or "error" in result[0].text.lower()
        assert "SERPAPI_KEY" in result[0].text

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.stop_server')
    async def test_call_tool_stop_server_by_name(self, mock_stop_server):
        """Test stop_server tool call with server name."""
        mock_stop_server.return_value = {"ok": True, "pid": 12345}
        
        result = await mcp_server.call_tool("stop_server", {
            "server": "flight_server",
            "timeout": 5.0
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "flight_server" in result[0].text
        assert "ok=True" in result[0].text or "12345" in result[0].text
        mock_stop_server.assert_called_once()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.stop_server')
    async def test_call_tool_stop_server_by_pid(self, mock_stop_server):
        """Test stop_server tool call with PID."""
        mock_stop_server.return_value = {"ok": True, "pid": 99999}
        
        result = await mcp_server.call_tool("stop_server", {
            "server": "99999",
            "timeout": 10.0
        })
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "99999" in result[0].text
        mock_stop_server.assert_called_once()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.health_check')
    async def test_call_tool_health_check_healthy(self, mock_health_check):
        """Test health_check tool call for healthy server."""
        mock_health_check.return_value = True
        
        result = await mcp_server.call_tool("health_check", {"server": "hotel_server"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "hotel_server" in result[0].text
        assert "healthy" in result[0].text.lower()
        mock_health_check.assert_called_once_with("hotel_server")

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.health_check')
    async def test_call_tool_health_check_unhealthy(self, mock_health_check):
        """Test health_check tool call for unhealthy server."""
        mock_health_check.return_value = False
        
        result = await mcp_server.call_tool("health_check", {"server": "broken_server"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "broken_server" in result[0].text
        assert "unhealthy" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers._find_server_dirs')
    @patch('py_mcp_travelplanner.cli_handlers._resolve_serpapi_key')
    @patch('py_mcp_travelplanner.cli_handlers.list_registered_pids')
    async def test_call_tool_get_status(self, mock_list_pids, mock_resolve_key, mock_find_dirs):
        """Test get_status tool call."""
        # Mock server directories
        mock_server_dir = Mock()
        mock_server_dir.name = "flight_server"
        mock_find_dirs.return_value = [mock_server_dir]
        
        mock_resolve_key.return_value = "test_key"
        mock_list_pids.return_value = {"flight_server": {"pid": 12345}}
        
        result = await mcp_server.call_tool("get_status", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Status:" in result[0].text
        assert "flight_server" in result[0].text
        assert "SERPAPI_KEY: present" in result[0].text

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.list_registered_pids')
    async def test_call_tool_list_pids_with_servers(self, mock_list_pids):
        """Test list_pids tool call when servers are running."""
        mock_list_pids.return_value = {
            "flight_server": {"pid": 12345, "started_at": "2025-10-31T10:00:00"},
            "hotel_server": {"pid": 12346, "started_at": "2025-10-31T10:00:05"}
        }
        
        result = await mcp_server.call_tool("list_pids", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "flight_server" in result[0].text
        assert "12345" in result[0].text
        assert "hotel_server" in result[0].text
        assert "12346" in result[0].text

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.list_registered_pids')
    async def test_call_tool_list_pids_no_servers(self, mock_list_pids):
        """Test list_pids tool call when no servers are running."""
        mock_list_pids.return_value = {}
        
        result = await mcp_server.call_tool("list_pids", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "No registered" in result[0].text or "no" in result[0].text.lower()

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.verify_serpapi_key')
    async def test_call_tool_verify_serpapi_key_success(self, mock_verify):
        """Test verify_serpapi_key tool call with valid key."""
        mock_verify.return_value = (True, {"http_status": 200, "keys": ["results", "search_metadata"]})
        
        result = await mcp_server.call_tool("verify_serpapi_key", {"timeout": 10.0})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "SUCCESS" in result[0].text
        assert "200" in result[0].text
        mock_verify.assert_called_once_with(timeout=10.0)

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.verify_serpapi_key')
    async def test_call_tool_verify_serpapi_key_failure(self, mock_verify):
        """Test verify_serpapi_key tool call with invalid key."""
        mock_verify.return_value = (False, {"error": "Invalid API key"})
        
        result = await mcp_server.call_tool("verify_serpapi_key", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "FAILED" in result[0].text
        assert "Invalid API key" in result[0].text

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test calling an unknown tool returns appropriate error."""
        result = await mcp_server.call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Unknown tool" in result[0].text or "unknown" in result[0].text.lower()


class TestMCPServerInitialization:
    """Test suite for MCP server initialization and configuration."""

    def test_server_name(self):
        """Verify the server has correct name."""
        assert mcp_server.mcp.name == "py_mcp_travelplanner_unified"

    def test_logger_configured(self):
        """Verify logger is configured correctly."""
        assert mcp_server.LOG.name == "py_mcp_travelplanner.mcp_server"


class TestMCPServerEdgeCases:
    """Test suite for edge cases and error conditions."""

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.start_server')
    async def test_start_server_with_missing_server_param(self, mock_start_server):
        """Test start_server handles missing required parameter gracefully."""
        # This should ideally be caught by schema validation, but test the handler
        mock_start_server.return_value = False
        
        # Call with empty server name
        result = await mcp_server.call_tool("start_server", {"server": "", "dry_run": False})
        
        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.get_registered_pid')
    @patch('py_mcp_travelplanner.cli_handlers.start_server')
    @patch('py_mcp_travelplanner.cli_handlers._resolve_serpapi_key')
    async def test_start_server_shows_pid_on_success(self, mock_resolve_key, mock_start_server, mock_get_pid):
        """Test that start_server includes PID in response when available."""
        mock_resolve_key.return_value = "test_key"
        mock_start_server.return_value = True
        mock_get_pid.return_value = 98765
        
        result = await mcp_server.call_tool("start_server", {
            "server": "geocoder_server",
            "dry_run": False
        })
        
        assert len(result) == 1
        assert "98765" in result[0].text or "PID" in result[0].text

    @pytest.mark.asyncio
    @patch('py_mcp_travelplanner.cli_handlers.stop_server')
    async def test_stop_server_with_error_in_result(self, mock_stop_server):
        """Test stop_server handles error in result dict."""
        mock_stop_server.return_value = {
            "ok": False,
            "pid": None,
            "error": "Server not found"
        }
        
        result = await mcp_server.call_tool("stop_server", {
            "server": "nonexistent_server",
            "timeout": 5.0
        })
        
        assert len(result) == 1
        assert "error" in result[0].text.lower()
        assert "Server not found" in result[0].text


class TestMCPServerIntegration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_full_workflow_list_then_start(self):
        """Test a complete workflow: list servers, then start one."""
        with patch('py_mcp_travelplanner.cli_handlers.list_servers') as mock_list, \
             patch('py_mcp_travelplanner.cli_handlers.start_server') as mock_start, \
             patch('py_mcp_travelplanner.cli_handlers._resolve_serpapi_key') as mock_key:
            
            mock_list.return_value = ["event_server", "flight_server"]
            mock_start.return_value = True
            mock_key.return_value = "test_key"
            
            # First list servers
            list_result = await mcp_server.call_tool("list_servers", {})
            assert "event_server" in list_result[0].text
            
            # Then start one
            start_result = await mcp_server.call_tool("start_server", {
                "server": "event_server",
                "dry_run": False
            })
            assert "started" in start_result[0].text.lower() or "True" in start_result[0].text

    @pytest.mark.asyncio
    async def test_full_workflow_start_check_stop(self):
        """Test workflow: start server, check health, stop server."""
        with patch('py_mcp_travelplanner.cli_handlers.start_server') as mock_start, \
             patch('py_mcp_travelplanner.cli_handlers.health_check') as mock_health, \
             patch('py_mcp_travelplanner.cli_handlers.stop_server') as mock_stop, \
             patch('py_mcp_travelplanner.cli_handlers._resolve_serpapi_key') as mock_key:
            
            mock_start.return_value = True
            mock_health.return_value = True
            mock_stop.return_value = {"ok": True, "pid": 12345}
            mock_key.return_value = "test_key"
            
            # Start
            start_result = await mcp_server.call_tool("start_server", {
                "server": "weather_server",
                "dry_run": False
            })
            assert "True" in start_result[0].text or "started" in start_result[0].text.lower()
            
            # Check health
            health_result = await mcp_server.call_tool("health_check", {
                "server": "weather_server"
            })
            assert "healthy" in health_result[0].text.lower()
            
            # Stop
            stop_result = await mcp_server.call_tool("stop_server", {
                "server": "weather_server",
                "timeout": 5.0
            })
            assert "ok=True" in stop_result[0].text or "12345" in stop_result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

