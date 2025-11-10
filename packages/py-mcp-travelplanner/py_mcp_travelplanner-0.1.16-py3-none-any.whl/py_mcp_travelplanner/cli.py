"""CLI entrypoint for py_mcp_travelplanner.

This module provides a minimal command-line interface that is wired in
`pyproject.toml` as the console script entrypoint `py_mcp_travelplanner_cli`.

Commands implemented (small, safe stubs to operate in this repo):
- list: print known server folders
- start: start a server's `main.py` as a subprocess (non-blocking)
- health: simple health check that verifies main.py exists for a server

The real servers live in sibling packages (e.g. `event_server`, `flight_server`).
This CLI intentionally uses subprocess invocation to avoid import-time side-effects
when starting those modules.
"""
from __future__ import annotations

import argparse
import logging
from typing import Sequence

from .cli_handlers import list_servers, start_server, health_check, start_all_servers

LOG = logging.getLogger("py_mcp_travelplanner.cli")


def _run_mcp_server():
    """Run the MCP server with proper error handling for missing dependencies."""
    try:
        from . import mcp_server
        return mcp_server.run_mcp_server()
    except ImportError as e:
        if 'mcp' in str(e):
            LOG.error("MCP dependencies not installed. Please install with: pip install 'py_mcp_travelplanner[servers]' or uv pip install mcp fastmcp")
            print("\n❌ Error: MCP dependencies not installed")
            print("\nTo fix this, run one of:")
            print("  pip install 'py_mcp_travelplanner[servers]'")
            print("  pip install mcp fastmcp")
            print("  uv pip install mcp fastmcp")
            return 1
        raise


def _run_control_server(host: str, port: int):
    """Run the control server with proper error handling."""
    try:
        from . import control_server
        return control_server.serve_control(host=host, port=port, background=False)
    except ImportError as e:
        LOG.error("Failed to import control_server: %s", e)
        print(f"\n❌ Error: Failed to start control server: {e}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="py_mcp_travelplanner",
        description="Minimal CLI for the MCP Travel Planner project",
    )

    # global dry-run flag (applies when starting servers)
    parser.add_argument("--dry-run", action="store_true", help="Don't actually start processes; show what would run")

    subparsers = parser.add_subparsers(dest="command", required=False)

    # list
    sp_list = subparsers.add_parser("list", help="List known servers")
    sp_list.set_defaults(func=lambda args: list_servers())

    # start
    sp_start = subparsers.add_parser("start", help="Start a server's main.py as a subprocess")
    sp_start.add_argument("server", help="Server to start (e.g. event_server)")
    sp_start.add_argument("--dry-run", action="store_true", help="Don't actually start the process; just print what would run")
    sp_start.set_defaults(func=lambda args: start_server(args.server, dry_run=args.dry_run))

    # health
    sp_health = subparsers.add_parser("health", help="Simple health check for a server (main.py exists)")
    sp_health.add_argument("server", help="Server to check (e.g. event_server)")
    sp_health.set_defaults(func=lambda args: health_check(args.server))

    # start-all explicit command
    sp_start_all = subparsers.add_parser("start-all", help="Start all discovered servers")
    sp_start_all.add_argument("--dry-run", action="store_true", help="Don't actually start processes; show what would run")
    sp_start_all.set_defaults(func=lambda args: start_all_servers(dry_run=getattr(args, 'dry_run', False)))

    # serve - start HTTP control server
    sp_serve = subparsers.add_parser("serve", help="Run HTTP control server for MCP CLI")
    sp_serve.add_argument("--host", default="127.0.0.1", help="Host to bind control server")
    sp_serve.add_argument("--port", type=int, default=8787, help="Port for control server")
    sp_serve.set_defaults(func=lambda args: _run_control_server(host=args.host, port=args.port))

    # mcp - start unified MCP server
    sp_mcp = subparsers.add_parser("mcp", help="Run unified MCP server via stdio")
    sp_mcp.set_defaults(func=lambda args: _run_mcp_server())

    # Add verbosity
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase logging verbosity")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # configure logging
    level = logging.WARNING
    if getattr(args, "verbose", 0) >= 2:
        level = logging.DEBUG
    elif getattr(args, "verbose", 0) == 1:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s: %(message)s")

    # If no subcommand is provided, default to starting all servers
    if not getattr(args, "command", None):
        # prefer the explicit flag or env var logic in start_all_servers
        try:
            results = start_all_servers(dry_run=getattr(args, "dry_run", False))
        except RuntimeError as re:
            # Friendly message and non-zero exit code
            print(f"Error: {re}")
            return 2

        # print summary
        if results:
            print("Start summary:")
            for name, ok in results.items():
                print(f" - {name}: {'started' if ok else 'failed'}")
            # return non-zero if any failed
            if not all(results.values()):
                return 2
        return 0

    try:
        result = args.func(args)
        # Handlers may return True/False or int exit codes
        if isinstance(result, bool):
            return 0 if result else 2
        if isinstance(result, int):
            return result
        return 0
    except SystemExit as se:
        # argparse or handlers might call sys.exit(); translate to int
        return int(se.code or 0)
    except Exception as exc:  # pragma: no cover - high-level CLI safety
        LOG.exception("Unhandled error in CLI: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
