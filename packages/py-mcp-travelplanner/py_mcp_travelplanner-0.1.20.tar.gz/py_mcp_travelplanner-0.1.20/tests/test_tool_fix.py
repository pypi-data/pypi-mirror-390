#!/usr/bin/env python3
"""Test script to verify tool delegation fix."""
import asyncio
import os
import pytest

from py_mcp_travelplanner import mcp_server


@pytest.fixture(scope="module")
def setup_serpapi_key():
    """Ensure SERPAPI_KEY is available from environment or .env file."""
    # Check if SERPAPI_KEY is already set, otherwise skip test
    if not os.environ.get('SERPAPI_KEY'):
        pytest.skip("SERPAPI_KEY not found in environment. Please set it in .env file.")
    yield


@pytest.mark.asyncio
async def test_tool_delegation(setup_serpapi_key):
    print("=" * 80)
    print("Testing Tool Delegation Fix")
    print("=" * 80)

    print("\n1. Initializing service registry...")
    await mcp_server._initialize_service_registry()
    print(f"   ✓ Registry has {len(mcp_server._TOOL_REGISTRY)} tools")
    print(f"   ✓ Services: {list(mcp_server._SERVICE_REGISTRY.keys())}")

    # Test flight.search_flights
    if 'flight.search_flights' in mcp_server._TOOL_REGISTRY:
        print("\n2. Testing flight.search_flights tool...")

        args = {
            'departure_id': 'LAX',
            'arrival_id': 'JFK',
            'outbound_date': '2025-12-01',
            'trip_type': 2,  # One way
            'adults': 1
        }

        try:
            result_blocks = await mcp_server.call_tool('flight.search_flights', args)
            print(f"   ✓ Result blocks: {len(result_blocks)}")

            for i, block in enumerate(result_blocks):
                print(f"\n   Block {i+1}:")
                print(f"   - Type: {block.type}")
                print(f"   - Text length: {len(block.text)} chars")
                print(f"   - Preview: {block.text[:200]}...")

                # Check if it's an error or success
                if 'error' in block.text.lower():
                    print("   ⚠ Contains error message")
                else:
                    print("   ✓ Appears successful")

        except Exception as e:
            print(f"   ✗ ERROR calling tool: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n   ✗ ERROR: flight.search_flights not found in registry!")
        print(f"   Available tools: {list(mcp_server._TOOL_REGISTRY.keys())[:10]}")

    # Test other tools
    print("\n3. Testing other subservice tools...")
    test_tools = [
        ('hotel.search_hotels', {
            'location': 'New York',
            'check_in_date': '2025-12-01',
            'check_out_date': '2025-12-05',
            'adults': 2
        }),
    ]

    for tool_name, tool_args in test_tools:
        if tool_name in mcp_server._TOOL_REGISTRY:
            print(f"\n   Testing {tool_name}...")
            try:
                result = await mcp_server.call_tool(tool_name, tool_args)
                print(f"   ✓ {tool_name}: {len(result)} blocks, {len(result[0].text)} chars")
                if 'error' in result[0].text.lower():
                    print(f"   ⚠ Response: {result[0].text[:150]}")
                else:
                    print(f"   ✓ Success!")
            except Exception as e:
                print(f"   ✗ ERROR: {e}")
        else:
            print(f"   ⚠ {tool_name} not in registry")

    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


