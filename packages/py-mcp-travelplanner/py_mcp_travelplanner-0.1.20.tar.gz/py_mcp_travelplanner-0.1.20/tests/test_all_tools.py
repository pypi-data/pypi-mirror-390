#!/usr/bin/env python3
"""Comprehensive test of all MCP tools to verify they are callable."""
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
async def test_all_tools(setup_serpapi_key):
    print("=" * 80)
    print("Testing ALL MCP Tools - Verifying They Are Callable")
    print("=" * 80)
    
    await mcp_server._initialize_service_registry()
    
    print(f"\nTotal tools registered: {len(mcp_server._TOOL_REGISTRY)}")
    print(f"Services: {list(mcp_server._SERVICE_REGISTRY.keys())}\n")
    
    # Group tools by service
    by_service = {}
    for tool_name, tool_info in mcp_server._TOOL_REGISTRY.items():
        service = tool_info['service']
        if service not in by_service:
            by_service[service] = []
        by_service[service].append(tool_name)
    
    for service, tools in sorted(by_service.items()):
        print(f"\n{service}: {len(tools)} tools")
        for tool in sorted(tools):
            print(f"  ✓ {tool}")
    
    # Test a sample from each service
    print("\n" + "=" * 80)
    print("Testing Sample Tools from Each Service")
    print("=" * 80)
    
    test_cases = [
        ('event.search_events', {
            'query': 'concerts in New York',
            'location': 'New York, NY'
        }),
        ('finance.get_exchange_rates', {
            'base_currency': 'USD'
        }),
        ('flight.search_flights', {
            'departure_id': 'LAX',
            'arrival_id': 'JFK',
            'outbound_date': '2025-12-15',
            'trip_type': 2,
            'adults': 1
        }),
        ('geocoder.geocode', {
            'location': 'New York, NY'
        }),
        ('hotel.search_hotels', {
            'location': 'Paris',
            'check_in_date': '2025-12-20',
            'check_out_date': '2025-12-25',
            'adults': 2
        }),
    ]
    
    results = []
    for tool_name, args in test_cases:
        print(f"\nTesting: {tool_name}")
        try:
            result_blocks = await mcp_server.call_tool(tool_name, args)
            result_text = result_blocks[0].text if result_blocks else ""
            
            if 'error' in result_text.lower():
                status = "⚠ ERROR"
                preview = result_text[:200]
            else:
                status = "✓ SUCCESS"
                preview = result_text[:150]
            
            print(f"  {status}")
            print(f"  Result length: {len(result_text)} chars")
            print(f"  Preview: {preview}...")
            results.append((tool_name, status))
            
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
            results.append((tool_name, f"✗ EXCEPTION: {e}"))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for tool, status in results:
        print(f"{status:12} - {tool}")
    
    success_count = sum(1 for _, s in results if '✓' in s)
    print(f"\n{success_count}/{len(results)} tools working correctly")
    print("=" * 80)

    # Assert that all tools are callable
    assert success_count == len(results), f"Only {success_count}/{len(results)} tools working"

