# -*- coding: utf-8 -*-
from __future__ import annotations

"""
API self-check (local).

This script is intentionally simple and dependency-free. It can be used to:
- verify the built-in server starts;
- verify key endpoints return expected shapes;
- run a short smoke cycle before screenshot capture.

Note: The gated pipeline uses `scripts/run_tests.py` and `scripts/build_materials.py`.
This script is optional but useful during maintenance.
"""

import json
import socket
import time
import urllib.error
import urllib.request
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from subprocess import Popen
import sys
import os


def _find_free_port(start: int = 8010) -> int:
    for port in range(start, start + 50):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("no free port found")


def _get(url: str, timeout: float = 3.0) -> tuple[int, str, str]:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ct = resp.headers.get("content-type", "")
        return resp.status, ct, data.decode("utf-8", errors="replace")


def _post_json(url: str, payload: dict, timeout: float = 3.0) -> tuple[int, str, str]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        ct = resp.headers.get("content-type", "")
        return resp.status, ct, data.decode("utf-8", errors="replace")


def _wait_ready(base_url: str, *, seconds: float = 10.0) -> None:
    deadline = time.time() + seconds
    last_err = None
    while time.time() < deadline:
        try:
            status, _, _ = _get(base_url + "/api/health", timeout=1.5)
            if status == 200:
                return
        except Exception as exc:
            last_err = exc
        time.sleep(0.3)
    raise RuntimeError(f"server not ready: {last_err}")


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def _assert_json_ok(text: str) -> dict:
    obj = json.loads(text)
    if not isinstance(obj, dict) or obj.get("ok") is not True:
        raise AssertionError("response not ok")
    return obj


def run_checks(base_url: str) -> list[Check]:
    results: list[Check] = []

    def do(name: str, fn) -> None:
        try:
            detail = fn()
            results.append(Check(name=name, ok=True, detail=detail))
        except Exception as exc:
            results.append(Check(name=name, ok=False, detail=str(exc)))

    do("health", lambda: str(_get(base_url + "/api/health")[0]))
    do("plants", lambda: str(len(_assert_json_ok(_get(base_url + "/api/plants")[2]).get("items", []))))
    do("materials", lambda: str(len(_assert_json_ok(_get(base_url + "/api/materials")[2]).get("items", []))))
    do("issues", lambda: str(len(_assert_json_ok(_get(base_url + "/api/issues")[2]).get("items", []))))
    do("report", lambda: "ok" if "关键指标" in _get(base_url + "/api/report")[2] else "missing")
    do("manifest", lambda: "ok" if "manifest" in _get(base_url + "/api/web/manifest")[2] else "missing")

    def login_and_export() -> str:
        _, _, t = _post_json(base_url + "/api/auth/login", {"username": "admin", "password": "admin123"})
        obj = _assert_json_ok(t)
        token = obj.get("token", "")
        if not token:
            raise AssertionError("missing token")
        status, _, csv_text = _get(base_url + "/api/export?kind=plants")
        if status != 200 or "编号" not in csv_text:
            raise AssertionError("export not ok")
        return "ok"

    do("login+export", login_and_export)
    return results


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    port = _find_free_port()
    env = os.environ.copy()
    env["APP_PORT"] = str(port)
    server = Popen([sys.executable, "apps/api/main.py"], cwd=project_root, env=env)
    base_url = f"http://127.0.0.1:{port}"
    try:
        _wait_ready(base_url)
        results = run_checks(base_url)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except Exception:
            server.kill()

    failed = [r for r in results if not r.ok]
    for r in results:
        flag = "PASS" if r.ok else "FAIL"
        print(f"[{flag}] {r.name}: {r.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

