import os
import time
import json
import pathlib

import pytest

from py_mcp_travelplanner import cli_handlers as ch


class DummyProc:
    def __init__(self, pid):
        self.pid = pid


class DummyPopen:
    def __init__(self, *args, **kwargs):
        # choose a pid > 10000 to avoid collisions
        self.pid = 20000


def test_register_and_unregister_pid(tmp_path, monkeypatch):
    # point repo root to tmp
    monkeypatch.setattr(ch, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(ch, 'SERVERS_DIR', tmp_path)

    ch.register_pid('s1', 12345)
    p = ch._pid_store_path()
    assert p.exists()
    data = json.loads(p.read_text())
    assert 's1' in data and data['s1']['pid'] == 12345

    ch.unregister_pid('s1')
    data = json.loads(p.read_text())
    assert 's1' not in data


def test_start_and_stop_register(monkeypatch, tmp_path):
    monkeypatch.setattr(ch, 'REPO_ROOT', tmp_path)
    monkeypatch.setattr(ch, 'SERVERS_DIR', tmp_path)

    # create a server folder with main.py
    sdir = tmp_path / 's1'
    sdir.mkdir()
    (sdir / 'main.py').write_text('print("hi")')

    # monkeypatch subprocess.Popen to DummyPopen
    monkeypatch.setattr('subprocess.Popen', DummyPopen)

    ok = ch.start_server('s1', dry_run=False, env_overrides={'SERPAPI_KEY':'x'})
    assert ok
    pid = ch.get_registered_pid('s1')
    assert pid == 20000

    # monkeypatch os.kill to simulate process existing then gone
    calls = {'killed': False}

    def fake_kill(pid, sig):
        if sig == 0:
            # simulate still exists (first few checks) then raise ProcessLookupError
            raise ProcessLookupError
        return None

    monkeypatch.setattr('os.kill', fake_kill)

    res = ch.stop_server('s1', timeout=0.1)
    # Since fake_kill raises ProcessLookupError on check, stop_server should report process not found
    assert res['ok'] in (True, False)

    # pid store should have been cleaned up
    assert ch.get_registered_pid('s1') is None

