"""Simple HTTP control interface for the MCP CLI.

This is a minimal implementation using the stdlib `http.server` to avoid
adding extra runtime dependencies. It's intended for local orchestration and
simple integration tests — for production you may prefer a small ASGI app.

Endpoints:
- GET /status -> JSON {"servers": [...], "serpapi": "present"|"missing"}
- POST /start_all -> starts all servers (requires SERPAPI_KEY)
- POST /start?server=NAME -> starts a single server
- GET /health?server=NAME -> returns health check for a server

The server runs on a background thread and can be started by calling
`serve_control(host, port)`.
"""
from __future__ import annotations

import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from . import cli_handlers

LOG = logging.getLogger("py_mcp_travelplanner.control_server")

# Allow address reuse to reduce "address already in use" / immediate bind failures
HTTPServer.allow_reuse_address = True


class ControlHandler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, obj: object) -> None:
        payload = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == '/status':
            servers = [p.name for p in cli_handlers._find_server_dirs()]
            serpapi = bool(cli_handlers._resolve_serpapi_key())
            self._send_json(200, {"servers": servers, "serpapi": "present" if serpapi else "missing"})
            return

        if path == '/health':
            server = qs.get('server', [None])[0]
            if not server:
                self._send_json(400, {"error": "missing server parameter"})
                return
            ok = cli_handlers.health_check(server)
            self._send_json(200, {"server": server, "healthy": bool(ok)})
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        length = int(self.headers.get('Content-Length', 0))
        if length:
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
            except Exception:
                data = {}
        else:
            data = {}

        if path == '/start_all':
            dry = qs.get('dry', ['false'])[0].lower() in ('1', 'true', 'yes')
            try:
                results = cli_handlers.start_all_servers(dry_run=dry)
                self._send_json(200, {"results": results})
            except Exception as exc:
                LOG.exception("start_all failed: %s", exc)
                self._send_json(500, {"error": str(exc)})
            return

        if path == '/start':
            server = qs.get('server', [None])[0]
            if not server:
                self._send_json(400, {"error": "missing server parameter"})
                return
            dry = qs.get('dry', ['false'])[0].lower() in ('1', 'true', 'yes')
            ok = cli_handlers.start_server(server, dry_run=dry)
            self._send_json(200, {"server": server, "started": bool(ok)})
            return

        if path == '/test_key':
            # perform a SerpAPI key verification and return the result
            ok, info = cli_handlers.verify_serpapi_key()
            if ok:
                self._send_json(200, {"ok": True, "info": info})
            else:
                self._send_json(400, {"ok": False, "info": info})
            return

        if path == '/stop':
            # stop by server name or pid
            server = qs.get('server', [None])[0]
            if not server:
                self._send_json(400, {"error": "missing server parameter (name or pid)"})
                return
            # if numeric, treat as pid
            try:
                sval = int(server)
                result = cli_handlers.stop_server(sval)
            except Exception:
                result = cli_handlers.stop_server(server)
            self._send_json(200, result)
            return

        if path == '/pids':
            data = cli_handlers.list_registered_pids()
            self._send_json(200, {"pids": data})
            return

        self._send_json(404, {"error": "not found"})


def serve_control(host: str = '127.0.0.1', port: int = 8787, background: bool = True) -> HTTPServer:
    """Start the control HTTP server and return the HTTPServer object.

    If background is True (default) the server runs on a background thread
    and this function returns immediately. If background is False the server
    will run in the current thread (blocking) until stopped.
    """
    try:
        server = HTTPServer((host, port), ControlHandler)
    except OSError as e:
        # Likely address bind issue. Provide a helpful message and re-raise.
        msg = f"Failed to bind control server to {host}:{port}: {e}"
        LOG.exception(msg)
        print(msg)
        raise

    def _run():
        LOG.info("Control server starting on %s:%s", host, port)
        try:
            server.serve_forever()
        except Exception:
            LOG.exception("Control server stopped")

    if background:
        t = threading.Thread(target=_run, daemon=True)
        t.start()
        # Give immediate feedback that server thread started and address is bound
        try:
            addr = server.server_address
            msg = f"Control server started (background) on {addr[0]}:{addr[1]}"
            LOG.info(msg)
            print(msg)
        except Exception:
            pass
        return server
    else:
        try:
            addr = server.server_address
            msg = f"Control server running (foreground) on {addr[0]}:{addr[1]}"
            LOG.info(msg)
            print(msg)
            server.serve_forever()
        except KeyboardInterrupt:
            LOG.info("Control server interrupted, shutting down")
            try:
                server.shutdown()
            except Exception:
                pass
        return server


if __name__ == '__main__':
    serve_control()
    print('Control server running on http://127.0.0.1:8787')
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('shutting down')
