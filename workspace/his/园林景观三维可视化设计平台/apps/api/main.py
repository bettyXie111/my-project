# -*- coding: utf-8 -*-
from __future__ import annotations

import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

try:
    from .domain.auth import authenticate, issue_token
    from .domain.csv_tools import parse_csv
    from .domain.exporter import export_all
    from .domain.errors import ApiError
    from .domain.reporting import build_markdown_report
    from .domain.router import Router, build_request, handle_api_error, json_response, text_response
    from .domain.static_files import build_manifest, build_static_response
    from .domain.store import ProjectStore
    from .domain.version_diff import diff_snapshots
except ImportError:  # run as script: `python apps/api/main.py`
    import sys

    PROJECT_ROOT_FALLBACK = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(PROJECT_ROOT_FALLBACK))
    from apps.api.domain.auth import authenticate, issue_token
    from apps.api.domain.csv_tools import parse_csv
    from apps.api.domain.exporter import export_all
    from apps.api.domain.errors import ApiError
    from apps.api.domain.reporting import build_markdown_report
    from apps.api.domain.router import Router, build_request, handle_api_error, json_response, text_response
    from apps.api.domain.static_files import build_manifest, build_static_response
    from apps.api.domain.store import ProjectStore
    from apps.api.domain.version_diff import diff_snapshots


PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "apps" / "web"
STORE = ProjectStore(PROJECT_ROOT)
ROUTER = Router()


def _read_body(handler: BaseHTTPRequestHandler) -> bytes:
    length = int(handler.headers.get("Content-Length") or "0")
    if length <= 0:
        return b""
    return handler.rfile.read(length)


def _safe_join(root: Path, rel: str) -> Path | None:
    rel = rel.lstrip("/").replace("/", os.sep)
    target = (root / rel).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


class Handler(BaseHTTPRequestHandler):
    server_version = "Garden3D/1.0"

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        if self.path.startswith("/api/"):
            return self._handle_api()

        resp = build_static_response(root=WEB_ROOT, request_path=self.path, fallback="index.html")
        self._send(resp.status, resp.headers, resp.body)

    def do_POST(self) -> None:
        if self.path.startswith("/api/"):
            return self._handle_api()
        self.send_response(405)
        self.end_headers()

    def do_PUT(self) -> None:
        if self.path.startswith("/api/"):
            return self._handle_api()
        self.send_response(405)
        self.end_headers()

    def _send(self, status: int, headers: dict[str, str], body: bytes) -> None:
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _handle_api(self) -> None:
        try:
            req = build_request(self.command, self.path, {k: str(v) for k, v in self.headers.items()}, _read_body(self))
            handler, params = ROUTER.match(req)
            status, headers, body = handler(req, params)
            self._send(status, headers, body)
        except ApiError as exc:
            status, headers, body = handle_api_error(exc)
            self._send(status, headers, body)
        except Exception as exc:
            status, headers, body = json_response(500, {"ok": False, "error": "internal_error", "message": str(exc)})
            self._send(status, headers, body)


def _require_demo_role(req, allowed: set[str]) -> None:
    auth = (req.headers.get("Authorization") or "").strip()
    if not auth.startswith("Bearer demo-"):
        # Demo mode: allow missing auth for reads.
        return
    parts = auth.replace("Bearer ", "", 1).split("-")
    role = parts[1] if len(parts) >= 2 else ""
    if role and role not in allowed:
        raise ApiError(403, "forbidden", "forbidden")


def _api_health(req, params):
    return json_response(200, {"ok": True})


def _api_login(req, params):
    ctype = (req.headers.get("Content-Type") or "").lower()
    username = ""
    password = ""
    if "application/json" in ctype:
        payload = req.json()
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "").strip()
    else:
        form = req.form()
        username = (form.get("username") or "").strip()
        password = (form.get("password") or "").strip()
    user = authenticate(username, password)
    token = issue_token(user)
    return json_response(200, {"ok": True, "token": token, "role": user.role})


def _api_sites(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_sites()})


def _api_plans(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_plans()})


def _api_versions(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_versions()})


def _api_plants(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_plants()})

def _api_create_plant(req, params):
    _require_demo_role(req, {"admin", "designer"})
    item = STORE.create_plant(req.json())
    return json_response(201, {"ok": True, "item": item})


def _api_update_plant(req, params):
    _require_demo_role(req, {"admin", "designer"})
    plant_id = params["plantId"]
    item = STORE.update_plant(plant_id, req.json())
    return json_response(200, {"ok": True, "item": item})


def _api_delete_plant(req, params):
    _require_demo_role(req, {"admin"})
    plant_id = params["plantId"]
    STORE.delete_plant(plant_id)
    return json_response(200, {"ok": True})


def _api_import_plants(req, params):
    _require_demo_role(req, {"admin", "designer"})
    payload = req.json()
    text = str(payload.get("csv") or "")
    rows = parse_csv(text)
    result = STORE.import_plants_csv(rows)
    return json_response(200, {"ok": True, "result": result})


def _api_materials(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_materials()})

def _api_create_material(req, params):
    _require_demo_role(req, {"admin", "designer"})
    item = STORE.create_material(req.json())
    return json_response(201, {"ok": True, "item": item})


def _api_update_material(req, params):
    _require_demo_role(req, {"admin", "designer"})
    item = STORE.update_material(params["materialId"], req.json())
    return json_response(200, {"ok": True, "item": item})


def _api_delete_material(req, params):
    _require_demo_role(req, {"admin"})
    STORE.delete_material(params["materialId"])
    return json_response(200, {"ok": True})


def _api_lights(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_lights()})

def _api_create_light(req, params):
    _require_demo_role(req, {"admin", "designer"})
    item = STORE.create_light(req.json())
    return json_response(201, {"ok": True, "item": item})


def _api_update_light(req, params):
    _require_demo_role(req, {"admin", "designer"})
    item = STORE.update_light(params["lightId"], req.json())
    return json_response(200, {"ok": True, "item": item})


def _api_delete_light(req, params):
    _require_demo_role(req, {"admin"})
    STORE.delete_light(params["lightId"])
    return json_response(200, {"ok": True})


def _api_issues(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_issues()})


def _api_create_issue(req, params):
    _require_demo_role(req, {"admin", "designer", "reviewer"})
    version_id = params["versionId"]
    payload = req.json()
    issue = STORE.create_issue(version_id, payload)
    return json_response(201, {"ok": True, "item": issue})


def _api_update_issue(req, params):
    _require_demo_role(req, {"admin", "designer"})
    issue_id = params["issueId"]
    payload = req.json()
    issue = STORE.update_issue(issue_id, payload)
    return json_response(200, {"ok": True, "item": issue})


def _api_pavings(req, params):
    return json_response(200, {"ok": True, "items": STORE.list_pavings()})


def _api_create_paving(req, params):
    _require_demo_role(req, {"admin", "designer"})
    plan_id = params["planId"]
    payload = req.json()
    paving = STORE.create_paving(plan_id, payload)
    return json_response(201, {"ok": True, "item": paving})


def _api_export(req, params):
    bundle = export_all(STORE)
    kind = (req.query.get("kind") or ["all"])[0]
    if kind == "plants":
        return text_response(200, bundle.plants_csv, content_type="text/csv; charset=utf-8")
    if kind == "materials":
        return text_response(200, bundle.materials_csv, content_type="text/csv; charset=utf-8")
    if kind == "lights":
        return text_response(200, bundle.lights_csv, content_type="text/csv; charset=utf-8")
    if kind == "all":
        combined = (
            "# plants\n"
            + bundle.plants_csv
            + "\n# materials\n"
            + bundle.materials_csv
            + "\n# lights\n"
            + bundle.lights_csv
        )
        return text_response(200, combined, content_type="text/plain; charset=utf-8")
    raise ApiError(400, "bad_request", "unknown export kind")

def _api_diff(req, params):
    before_id = (req.query.get("before") or [""])[0].strip()
    after_id = (req.query.get("after") or [""])[0].strip()
    if not before_id or not after_id:
        raise ApiError(400, "bad_request", "before/after are required")
    before = STORE.get_version(before_id).get("snapshot") or {}
    after = STORE.get_version(after_id).get("snapshot") or {}
    if not isinstance(before, dict) or not isinstance(after, dict):
        raise ApiError(400, "bad_request", "snapshot must be object")
    return json_response(200, {"ok": True, "diff": diff_snapshots(before, after)})


def _api_report(req, params):
    text = build_markdown_report(STORE._state)  # local-only
    return text_response(200, text, content_type="text/markdown; charset=utf-8")

def _api_web_manifest(req, params):
    return json_response(200, {"ok": True, "manifest": build_manifest(WEB_ROOT)})
ROUTER.add("GET", "/api/health", _api_health)
ROUTER.add("POST", "/api/auth/login", _api_login)
ROUTER.add("GET", "/api/sites", _api_sites)
ROUTER.add("GET", "/api/plans", _api_plans)
ROUTER.add("GET", "/api/versions", _api_versions)
ROUTER.add("GET", "/api/plants", _api_plants)
ROUTER.add("POST", "/api/plants", _api_create_plant)
ROUTER.add("PUT", "/api/plants/{plantId}", _api_update_plant)
ROUTER.add("POST", "/api/plants/{plantId}/delete", _api_delete_plant)
ROUTER.add("POST", "/api/plants/import", _api_import_plants)
ROUTER.add("GET", "/api/materials", _api_materials)
ROUTER.add("POST", "/api/materials", _api_create_material)
ROUTER.add("PUT", "/api/materials/{materialId}", _api_update_material)
ROUTER.add("POST", "/api/materials/{materialId}/delete", _api_delete_material)
ROUTER.add("GET", "/api/lights", _api_lights)
ROUTER.add("POST", "/api/lights", _api_create_light)
ROUTER.add("PUT", "/api/lights/{lightId}", _api_update_light)
ROUTER.add("POST", "/api/lights/{lightId}/delete", _api_delete_light)
ROUTER.add("GET", "/api/issues", _api_issues)
ROUTER.add("POST", "/api/versions/{versionId}/issues", _api_create_issue)
ROUTER.add("PUT", "/api/issues/{issueId}", _api_update_issue)
ROUTER.add("GET", "/api/pavings", _api_pavings)
ROUTER.add("POST", "/api/plans/{planId}/pavings", _api_create_paving)
ROUTER.add("GET", "/api/export", _api_export)
ROUTER.add("GET", "/api/versions/diff", _api_diff)
ROUTER.add("GET", "/api/report", _api_report)
ROUTER.add("GET", "/api/web/manifest", _api_web_manifest)


def main() -> None:
    port = int(os.environ.get("APP_PORT") or "8010")
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
