"""Handlers used by the CLI.

This module provides small utility functions that operate safely inside the
repository without importing server packages that may have side-effects.

Functions:
- list_servers() -> list[str]
- start_server(server: str, dry_run: bool = False) -> bool
- health_check(server: str) -> bool

Behavior is conservative: it only interacts with the filesystem and
spawns subprocesses pointing at `main.py` under the server folder.
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
import signal
import subprocess
import sys
import time
from typing import List, Optional

from .config import get_config

# Try to import optional dotenv support
try:
    from dotenv import dotenv_values
    _DOTENV_AVAILABLE = True
except ImportError:
    dotenv_values = None  # type: ignore
    _DOTENV_AVAILABLE = False

LOG = logging.getLogger("py_mcp_travelplanner.cli_handlers")

# Discover servers at the repository root (one level above this package).
# For example, top-level folders like `event_server/` and `flight_server/`.
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVERS_DIR = REPO_ROOT


def _find_server_dirs() -> List[pathlib.Path]:
    """Return candidate server directories (look for folders with a main.py).

    This is intentionally permissive: any child dir with a `main.py` file is
    considered a server.
    """
    candidates: set[pathlib.Path] = set()

    # 1) look directly under the configured SERVERS_DIR (repo root)
    try:
        for child in SERVERS_DIR.iterdir():
            if child.is_dir():
                main_py = child / "main.py"
                if main_py.exists():
                    candidates.add(child)
    except Exception:
        LOG.debug("Failed to iterate SERVERS_DIR=%s", SERVERS_DIR, exc_info=True)

    # 2) also look under the package directory (py_mcp_travelplanner/*)
    # Only do this extra search if SERVERS_DIR is the default REPO_ROOT. If the
    # caller (for example tests) has overridden SERVERS_DIR, prefer that.
    if SERVERS_DIR == REPO_ROOT:
        package_dir = pathlib.Path(__file__).resolve().parent
        try:
            for child in package_dir.iterdir():
                if child.is_dir():
                    main_py = child / "main.py"
                    if main_py.exists():
                        candidates.add(child)
        except Exception:
            LOG.debug("Failed to iterate package_dir=%s", package_dir, exc_info=True)

    return sorted(candidates, key=lambda p: p.name)


def list_servers() -> List[str]:
    """Print and return the list of discovered server package directories."""
    servers = [p.name for p in _find_server_dirs()]
    if not servers:
        print("No server directories with main.py found.")
        return []
    print("Available servers:")
    for s in servers:
        print(f" - {s}")
    return servers


def _server_main_path(server: str) -> pathlib.Path:
    # Try SERVERS_DIR first (repo root), then package dir (py_mcp_travelplanner/<server>/main.py)
    candidate1 = SERVERS_DIR / server / "main.py"
    if candidate1.exists():
        return candidate1
    package_dir = pathlib.Path(__file__).resolve().parent
    candidate2 = package_dir / server / "main.py"
    return candidate2


def start_server(server: str, dry_run: bool = False, env_overrides: dict | None = None) -> bool:
    """Start the server's main.py in a detached subprocess.

    Returns True if the process was launched (or would have been in dry-run).
    Returns False for missing server or failed start.
    """
    main_path = _server_main_path(server)
    if not main_path.exists():
        print(f"Server '{server}' not found (expected {main_path}).")
        return False

    cmd = [sys.executable, str(main_path)]
    print(f"Starting {server}: {' '.join(cmd)}")

    if dry_run:
        return True

    try:
        # On Unix, start in a new process group so it can be managed independently.
        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)
        proc = subprocess.Popen(cmd, cwd=str(main_path.parent), env=env, start_new_session=True)
        print(f"Started process PID={proc.pid}")
        # Register pid for later stop
        try:
            register_pid(server, proc.pid)
        except Exception:
            LOG.exception("Failed to register pid for %s", server)
        return True
    except Exception as exc:  # pragma: no cover - runtime spawn failure
        LOG.exception("Failed to start server %s: %s", server, exc)
        print(f"Failed to start server: {exc}")
        return False


def health_check(server: str) -> bool:
    """A minimal health check: verify main.py exists and is readable.

    Longer health checks could try to HTTP ping a known port, but this
    keeps dependencies low and is safe to run.
    """
    main_path = _server_main_path(server)
    if not main_path.exists():
        print(f"Server '{server}' not found (expected {main_path}).")
        return False
    if not os.access(main_path, os.R_OK):
        print(f"Server '{server}' main.py is not readable: {main_path}")
        return False
    print(f"Server '{server}' main.py exists and is readable: {main_path}")
    return True


def _load_env_file(path: pathlib.Path) -> dict:
    """Load a .env file into a dict using python-dotenv for robust parsing.

    Falls back to a simple parser if python-dotenv is not available.
    """
    result: dict = {}
    if not path.exists():
        return result
    if _DOTENV_AVAILABLE and dotenv_values is not None:
        try:
            values = dotenv_values(str(path))
            # dotenv_values returns a dict-like object; convert to dict
            return dict(values or {})
        except Exception:
            LOG.exception("python-dotenv failed to parse %s", path)
            return {}

    # Fallback (shouldn't normally be used if python-dotenv is installed)
    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                result[k.strip()] = v.strip().strip('"')
    except Exception:
        LOG.exception("Failed to read env file: %s", path)
    return result


def _resolve_serpapi_key() -> str | None:
    """Resolve SERPAPI_KEY from config (which loads from env, .env, yaml).

    Returns the API key or None if not found.
    """
    from .config import get_api_key
    return get_api_key('SERPAPI_KEY')


def verify_serpapi_key(timeout: float = 10.0) -> tuple[bool, dict]:
    """Attempt a tiny SerpAPI query to verify the provided SERPAPI_KEY.

    Returns (ok: bool, info: dict). The info dict contains keys:
      - http_status (int) if request made
      - error (str) on known API error
      - keys (list) top-level JSON keys on success
      - raw_sample (str) truncated JSON/text for debugging (no key included)
    """
    serpapi = _resolve_serpapi_key()
    if not serpapi:
        return False, {"error": "SERPAPI_KEY not found"}

    try:
        import requests

        url = 'https://serpapi.com/search.json'
        params = {'q': 'example', 'engine': 'google', 'api_key': serpapi}
        r = requests.get(url, params=params, timeout=timeout)
        info: dict = {"http_status": r.status_code}
        try:
            data = r.json()
            if isinstance(data, dict) and 'error' in data:
                info['error'] = data.get('error')
                return False, info
            info['keys'] = list(data.keys()) if isinstance(data, dict) else []
            # attach a truncated sample for debugging
            info['raw_sample'] = str(data)[:1000]
            return True, info
        except Exception:
            info['raw_text'] = r.text[:1000]
            return False, info
    except Exception as exc:
        return False, {"error": str(exc)}


def start_all_servers(dry_run: bool = False) -> dict:
    """Start all discovered servers.

    This function requires `SERPAPI_KEY` to be set in the environment or in
    a `.env` file (package or repo root). If the key is missing, it aborts by
    raising a RuntimeError.

    Returns a dict mapping server name -> bool indicating success.
    """
    servers = [p.name for p in _find_server_dirs()]
    if not servers:
        raise RuntimeError('No servers found to start.')

    serpapi = _resolve_serpapi_key()
    if not serpapi:
        raise RuntimeError('SERPAPI_KEY not found in environment or .env; aborting start.')

    results = {}
    env_overrides = {'SERPAPI_KEY': serpapi}
    for s in servers:
        ok = start_server(s, dry_run=dry_run, env_overrides=env_overrides)
        results[s] = ok
        if ok and not dry_run:
            # make sure pid was registered (start_server does registration itself)
            pass
    return results


def stop_server(server: str | int, timeout: float = 5.0) -> dict:
    """Stop a server by name or pid. Returns dict with keys: ok, pid, error (optional).

    Attempts graceful SIGTERM then SIGKILL after timeout.
    """
    pid = None
    if isinstance(server, int):
        pid = server
    else:
        pid = get_registered_pid(server)

    if not pid:
        return {"ok": False, "error": "no pid found for server", "pid": None}

    try:
        # Try graceful
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        # process not found
        unregister_pid(server if isinstance(server, str) else str(pid))
        return {"ok": False, "error": "process not found", "pid": pid}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "pid": pid}

    # wait up to timeout for process to exit
    waited = 0.0
    interval = 0.1
    while waited < timeout:
        try:
            os.kill(pid, 0)
            # still alive
            time.sleep(interval)
            waited += interval
        except ProcessLookupError:
            # exited
            if isinstance(server, str):
                unregister_pid(server)
            else:
                unregister_pid(str(pid))
            return {"ok": True, "pid": pid}

    # still alive -> force kill
    try:
        os.kill(pid, signal.SIGKILL)
    except Exception as exc:
        return {"ok": False, "error": f"failed to kill: {exc}", "pid": pid}

    # unregister any registered name that matches the pid (or the provided name)
    try:
        d = _load_pid_store()
        to_remove = []
        if isinstance(server, str):
            to_remove.append(server)
        else:
            # remove entries where pid matches
            for name, entry in d.items():
                try:
                    if int(entry.get('pid')) == int(pid):
                        to_remove.append(name)
                except Exception:
                    continue
        for name in to_remove:
            if name in d:
                del d[name]
        _save_pid_store(d)
    except Exception:
        LOG.exception('Failed to unregister pid store entry for %s', pid)
    return {"ok": True, "pid": pid}


def _pid_store_path() -> pathlib.Path:
    """Path to the pid store file in the repo root."""
    return REPO_ROOT / '.mcp_pids.json'


def _load_pid_store() -> dict:
    p = _pid_store_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        LOG.exception('Failed to read pid store %s', p)
        return {}


def _save_pid_store(d: dict) -> None:
    p = _pid_store_path()
    try:
        p.write_text(json.dumps(d))
    except Exception:
        LOG.exception('Failed to write pid store %s', p)


def register_pid(server: str, pid: int) -> None:
    d = _load_pid_store()
    d[server] = {'pid': pid, 'started_at': time.time()}
    _save_pid_store(d)


def unregister_pid(server: str) -> None:
    d = _load_pid_store()
    if server in d:
        del d[server]
        _save_pid_store(d)


def get_registered_pid(server: str) -> int | None:
    d = _load_pid_store()
    entry = d.get(server)
    return int(entry['pid']) if entry and 'pid' in entry else None


def list_registered_pids() -> dict:
    return _load_pid_store()
