import os
import pathlib
import textwrap
import subprocess

import pytest

from py_mcp_travelplanner import cli_handlers as ch


def test_load_env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text(textwrap.dedent("""
        # comment
        SERPAPI_KEY = "abc123"
        OTHER=val
    """))
    data = ch._load_env_file(p)
    assert data["SERPAPI_KEY"] == "abc123"
    assert data["OTHER"] == "val"


def _make_server_dir(tmp_path, name):
    d = tmp_path / name
    d.mkdir()
    (d / "main.py").write_text('# dummy')
    return d


def test_start_all_requires_serpapi(monkeypatch, tmp_path):
    # create fake server dirs under a fake repo root
    s1 = _make_server_dir(tmp_path, "s1")
    s2 = _make_server_dir(tmp_path, "s2")
    monkeypatch.setattr(ch, 'SERVERS_DIR', tmp_path)

    # ensure SERPAPI_KEY not found by monkeypatching resolver
    monkeypatch.setattr(ch, '_resolve_serpapi_key', lambda: None)

    with pytest.raises(RuntimeError):
        ch.start_all_servers(dry_run=True)


def test_start_all_with_serpapi_dryrun(monkeypatch, tmp_path):
    s1 = _make_server_dir(tmp_path, "s1")
    s2 = _make_server_dir(tmp_path, "s2")
    monkeypatch.setattr(ch, 'SERVERS_DIR', tmp_path)

    # pretend resolver returns a token
    monkeypatch.setattr(ch, '_resolve_serpapi_key', lambda: 'token-xyz')

    results = ch.start_all_servers(dry_run=True)
    assert set(results.keys()) == {"s1", "s2"}
    assert all(results.values())

    # ensure that start_server will use env overrides when actually launching
    # (dry-run doesn't spawn; we verify the function returns True in dry-run)
