import pytest
import requests
import subprocess
import time
import os
from pathlib import Path

# Integration test for HTTP manifest endpoint of weather_server
@pytest.mark.integration
def test_weather_server_http_manifest(tmp_path):
    # Start the weather server with HTTP transport on a test port
    port = 18991
    env = os.environ.copy()
    server_path = Path(__file__).parent.parent / 'py_mcp_travelplanner' / 'weather_server' / 'main.py'
    proc = subprocess.Popen([
        'python', str(server_path),
        '--transport', 'http',
        '--host', '127.0.0.1',
        '--port', str(port)
    ], env=env)
    try:
        # Wait for server to start
        time.sleep(2)
        resp = requests.get(f'http://127.0.0.1:{port}/manifest', timeout=5)
        assert resp.status_code == 200
        manifest = resp.json()
        assert 'tools' in manifest or 'name' in manifest  # Accepts both list or dict style
    finally:
        proc.terminate()
        proc.wait(timeout=5)

