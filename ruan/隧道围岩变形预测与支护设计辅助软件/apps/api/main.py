from __future__ import annotations

import json
import mimetypes
import os
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from analytics import build_alerts, dashboard_snapshot, generate_recommendation, predict_section, risk_level, risk_score
from repository import ProjectRepository


ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "apps" / "web"
DATA_PATH = ROOT / "apps" / "api" / "data" / "demo_dataset.json"
CONTRACT_PATH = ROOT / "packages" / "shared-contracts" / "api_contract.json"
RULEBOOK_PATH = ROOT / "packages" / "shared-contracts" / "support_rulebook.json"
PORT = int(os.environ.get("APP_PORT", "8010"))
SESSIONS: dict[str, dict[str, str]] = {}
REPOSITORY = ProjectRepository(DATA_PATH)


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class TunnelAssistantHandler(BaseHTTPRequestHandler):
    server_version = "TunnelAssistant/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self.handle_api_get(parsed)
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "message": "unsupported"})
            return
        self.handle_api_post(parsed)

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return

    def parse_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def current_user(self) -> dict | None:
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth.replace("Bearer ", "", 1)
        return SESSIONS.get(token)

    def require_user(self) -> dict | None:
        user = self.current_user()
        if user is None:
            json_response(self, HTTPStatus.UNAUTHORIZED, {"ok": False, "message": "未登录或令牌失效。"})
            return None
        return user

    def serve_static(self, raw_path: str) -> None:
        if raw_path in {"/", ""}:
            target = WEB_ROOT / "index.html"
        elif raw_path == "/assets/styles.css":
            target = WEB_ROOT / "styles.css"
        elif raw_path == "/assets/app.js":
            target = WEB_ROOT / "app.js"
        else:
            target = WEB_ROOT / raw_path.lstrip("/")
        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        mime, _ = mimetypes.guess_type(str(target))
        content = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{mime or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def handle_api_get(self, parsed) -> None:
        user = None
        if parsed.path not in {"/api/health", "/api/contracts"}:
            user = self.require_user()
            if user is None:
                return
        if parsed.path == "/api/health":
            json_response(self, HTTPStatus.OK, {"ok": True, "service": "tunnel-assistant", "port": PORT})
            return
        if parsed.path == "/api/session":
            json_response(self, HTTPStatus.OK, {"ok": True, "user": user})
            return
        if parsed.path == "/api/dashboard":
            dataset = REPOSITORY.load()
            payload = dashboard_snapshot(dataset)
            payload["auditTrail"] = dataset["auditTrail"][-5:]
            json_response(self, HTTPStatus.OK, {"ok": True, "data": payload})
            return
        if parsed.path == "/api/sections":
            params = parse_qs(parsed.query)
            keyword = params.get("keyword", [""])[0]
            risk = params.get("risk", [""])[0]
            sections = REPOSITORY.search_sections(keyword=keyword, risk=risk)
            payload = []
            for section in sections:
                payload.append(
                    {
                        **section,
                        "riskScore": risk_score(section),
                        "riskLevel": risk_level(risk_score(section)),
                    }
                )
            json_response(self, HTTPStatus.OK, {"ok": True, "items": payload})
            return
        if parsed.path.startswith("/api/sections/"):
            section_id = parsed.path.rsplit("/", 1)[-1]
            section = REPOSITORY.get_section(section_id)
            if section is None:
                json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "message": "区段不存在。"})
                return
            json_response(
                self,
                HTTPStatus.OK,
                {
                    "ok": True,
                    "item": {
                        **section,
                        "riskScore": risk_score(section),
                        "riskLevel": risk_level(risk_score(section)),
                    },
                },
            )
            return
        if parsed.path == "/api/alerts":
            dataset = REPOSITORY.load()
            json_response(self, HTTPStatus.OK, {"ok": True, "items": build_alerts(dataset["sections"])})
            return
        if parsed.path == "/api/predictions":
            json_response(self, HTTPStatus.OK, {"ok": True, "items": REPOSITORY.recent_predictions()})
            return
        if parsed.path == "/api/recommendations":
            json_response(self, HTTPStatus.OK, {"ok": True, "items": REPOSITORY.recent_recommendations()})
            return
        if parsed.path == "/api/contracts":
            payload = {
                "api": json.loads(CONTRACT_PATH.read_text(encoding="utf-8")) if CONTRACT_PATH.exists() else {},
                "rulebook": json.loads(RULEBOOK_PATH.read_text(encoding="utf-8")) if RULEBOOK_PATH.exists() else {},
            }
            json_response(self, HTTPStatus.OK, {"ok": True, "data": payload})
            return
        json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "message": "接口不存在。"})

    def handle_api_post(self, parsed) -> None:
        if parsed.path == "/api/auth/login":
            body = self.parse_json_body()
            user = REPOSITORY.get_user(body.get("username", ""))
            if user is None or user["password"] != body.get("password", ""):
                json_response(self, HTTPStatus.UNAUTHORIZED, {"ok": False, "message": "用户名或密码错误。"})
                return
            token = secrets.token_hex(16)
            session_user = {
                "username": user["username"],
                "name": user["name"],
                "role": user["role"],
                "title": user["title"],
                "permissions": user["permissions"],
            }
            SESSIONS[token] = session_user
            json_response(self, HTTPStatus.OK, {"ok": True, "token": token, "user": session_user})
            return
        user = self.require_user()
        if user is None:
            return
        body = self.parse_json_body()
        if parsed.path == "/api/auth/logout":
            auth = self.headers.get("Authorization", "")
            token = auth.replace("Bearer ", "", 1)
            if token:
                SESSIONS.pop(token, None)
            json_response(self, HTTPStatus.OK, {"ok": True})
            return
        if parsed.path == "/api/predictions":
            section = REPOSITORY.get_section(body.get("sectionId", ""))
            if section is None:
                json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "message": "未找到指定区段。"})
                return
            dataset = REPOSITORY.load()
            scenario = {
                "scenarioName": body.get("scenarioName", "掌子面推进情景"),
                "generatedAt": body.get("generatedAt", "2026-05-15T11:00:00"),
                "excavationIntensity": body.get("excavationIntensity", 1.0),
                "rainfallFactor": body.get("rainfallFactor", 0.5),
                "safetyFactor": body.get("safetyFactor", 1.15),
            }
            prediction = predict_section(section, scenario, dataset["supportTemplates"])
            REPOSITORY.append_prediction(prediction)
            json_response(self, HTTPStatus.OK, {"ok": True, "item": prediction})
            return
        if parsed.path == "/api/recommendations":
            section = REPOSITORY.get_section(body.get("sectionId", ""))
            if section is None:
                json_response(self, HTTPStatus.BAD_REQUEST, {"ok": False, "message": "未找到指定区段。"})
                return
            dataset = REPOSITORY.load()
            scenario = {
                "scenarioName": body.get("scenarioName", "支护复核情景"),
                "generatedAt": body.get("generatedAt", "2026-05-15T11:10:00"),
                "excavationIntensity": body.get("excavationIntensity", 1.0),
                "rainfallFactor": body.get("rainfallFactor", 0.5),
                "safetyFactor": body.get("safetyFactor", 1.15),
            }
            recommendation = generate_recommendation(section, scenario, dataset["supportTemplates"])
            REPOSITORY.append_recommendation(recommendation)
            json_response(self, HTTPStatus.OK, {"ok": True, "item": recommendation})
            return
        json_response(self, HTTPStatus.NOT_FOUND, {"ok": False, "message": "不支持的提交。"})


def run() -> None:
    REPOSITORY.ensure_seeded()
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), TunnelAssistantHandler)
    print(f"Tunnel assistant running on http://127.0.0.1:{PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()

