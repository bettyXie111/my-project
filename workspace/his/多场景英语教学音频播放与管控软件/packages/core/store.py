from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from pathlib import Path


def _now_ms() -> int:
    return int(time.time() * 1000)


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


@dataclass
class InMemoryDB:
    base_dir: Path

    def __post_init__(self) -> None:
        self._users = []
        self._scenes = []
        self._devices = []
        self._lessons = []
        self._clips = []
        self._sessions = []
        self._events = []
        self._seq = 0
        self._seed()

    def _seed(self) -> None:
        from .crypto import hash_password

        self._users = [
            {"id": "u_teacher", "name": "英语教师", "role": "teacher", "username": "teacher", "password_hash": hash_password("demo")},
            {"id": "u_student", "name": "学生端", "role": "student", "username": "student", "password_hash": hash_password("demo")},
            {"id": "u_admin", "name": "管理员", "role": "admin", "username": "admin", "password_hash": hash_password("demo")},
        ]

        self._scenes = [
            {"id": "scene_classroom", "name": "普通教室", "capabilities": {"force_sync": False, "student_seek": False, "student_speed": False, "student_loop": False}},
            {"id": "scene_language_lab", "name": "语音室", "capabilities": {"force_sync": True, "student_seek": False, "student_speed": False, "student_loop": True}},
            {"id": "scene_live", "name": "线上直播", "capabilities": {"force_sync": True, "student_seek": False, "student_speed": False, "student_loop": False}},
            {"id": "scene_corner", "name": "口语角", "capabilities": {"force_sync": False, "student_seek": True, "student_speed": True, "student_loop": True}},
            {"id": "scene_selfstudy", "name": "自习室", "capabilities": {"force_sync": False, "student_seek": True, "student_speed": True, "student_loop": True}},
        ]

        self._devices = []
        for scene in self._scenes:
            sid = scene["id"]
            self._devices.append({"id": _id("dev"), "scene_id": sid, "name": f"{scene['name']} 教师控制台", "type": "teacher_console", "online": True, "last_seen": _now_ms()})
            for i in range(1, 4):
                self._devices.append({"id": _id("dev"), "scene_id": sid, "name": f"{scene['name']} 学生终端 {i}", "type": "student_terminal", "online": (i != 3), "last_seen": _now_ms() - i * 7000})

        demo = self.create_lesson(title="Unit 1 听力热身", scene_id="scene_language_lab", teacher_id="u_teacher", book_unit="Unit 1")
        asset_id = "asset_demo_001"
        self._clips.extend(
            [
                {"id": _id("clip"), "lesson_id": demo["id"], "audio_asset_id": asset_id, "label": "对话开头", "start_ms": 0, "end_ms": 12000, "default_speed": 1.0, "loop_suggest": 1},
                {"id": _id("clip"), "lesson_id": demo["id"], "audio_asset_id": asset_id, "label": "重点句复听", "start_ms": 12000, "end_ms": 24000, "default_speed": 0.9, "loop_suggest": 2},
                {"id": _id("clip"), "lesson_id": demo["id"], "audio_asset_id": asset_id, "label": "听写片段", "start_ms": 24000, "end_ms": 38000, "default_speed": 0.8, "loop_suggest": 3},
                {"id": _id("clip"), "lesson_id": demo["id"], "audio_asset_id": asset_id, "label": "跟读收尾", "start_ms": 38000, "end_ms": 52000, "default_speed": 1.0, "loop_suggest": 1},
            ]
        )

    def get_user_by_username(self, username: str) -> dict | None:
        for u in self._users:
            if u["username"] == username:
                return u
        return None

    def list_scenes(self) -> list[dict]:
        return list(self._scenes)

    def get_scene(self, scene_id: str) -> dict | None:
        for s in self._scenes:
            if s["id"] == scene_id:
                return s
        return None

    def update_scene_capabilities(self, scene_id: str, capabilities: dict) -> dict | None:
        scene = self.get_scene(scene_id)
        if not scene:
            return None
        merged = dict(scene.get("capabilities") or {})
        for k in ("force_sync", "student_seek", "student_speed", "student_loop"):
            if k in capabilities:
                merged[k] = bool(capabilities[k])
        scene["capabilities"] = merged
        return scene

    def list_devices(self, scene_id: str | None = None) -> list[dict]:
        if not scene_id:
            return list(self._devices)
        return [d for d in self._devices if d["scene_id"] == scene_id]

    def list_lessons(self) -> list[dict]:
        items = []
        for l in self._lessons:
            scene = self.get_scene(l["scene_id"])
            items.append({**l, "scene_name": scene["name"] if scene else l["scene_id"]})
        return items

    def create_lesson(self, title: str, scene_id: str, teacher_id: str, book_unit: str) -> dict:
        item = {"id": _id("lesson"), "title": title, "scene_id": scene_id, "teacher_id": teacher_id, "book_unit": book_unit, "status": "draft"}
        self._lessons.append(item)
        return item

    def get_lesson(self, lesson_id: str) -> dict | None:
        for l in self._lessons:
            if l["id"] == lesson_id:
                return l
        return None

    def list_clips(self, lesson_id: str) -> list[dict]:
        return [c for c in self._clips if c["lesson_id"] == lesson_id]

    def create_clip(
        self,
        lesson_id: str,
        audio_asset_id: str,
        label: str,
        start_ms: int,
        end_ms: int,
        default_speed: float,
        loop_suggest: int,
    ) -> dict:
        item = {
            "id": _id("clip"),
            "lesson_id": lesson_id,
            "audio_asset_id": audio_asset_id,
            "label": label,
            "start_ms": start_ms,
            "end_ms": end_ms,
            "default_speed": default_speed,
            "loop_suggest": loop_suggest,
        }
        self._clips.append(item)
        return item

    def start_session(self, lesson_id: str) -> dict | None:
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return None
        lesson["status"] = "running"
        session = {"id": _id("sess"), "lesson_id": lesson_id, "started_at": _now_ms(), "ended_at": None}
        self._sessions.append(session)
        return session

    def end_session(self, session_id: str) -> dict | None:
        sess = next((s for s in self._sessions if s["id"] == session_id), None)
        if not sess:
            return None
        if not sess.get("ended_at"):
            sess["ended_at"] = _now_ms()
        lesson = self.get_lesson(sess["lesson_id"])
        if lesson:
            lesson["status"] = "ended"
        return sess

    def end_active_session(self, lesson_id: str) -> dict | None:
        sess = next((s for s in reversed(self._sessions) if s["lesson_id"] == lesson_id and not s.get("ended_at")), None)
        if not sess:
            return None
        return self.end_session(sess["id"])

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def add_event(self, session_id: str, actor_user_id: str, target: str, action: str, payload: dict) -> dict | None:
        sess = next((s for s in self._sessions if s["id"] == session_id), None)
        if not sess:
            return None
        seq = self._next_seq()
        summary = self._event_summary(action=action, payload=payload)
        evt = {
            "seq": seq,
            "id": _id("evt"),
            "session_id": session_id,
            "actor_user_id": actor_user_id,
            "target": target,
            "action": action,
            "payload": payload,
            "summary": summary,
            "created_at": _now_ms(),
        }
        self._events.append(evt)
        return evt

    def list_events(self, session_id: str, since: int = 0) -> list[dict]:
        items = [e for e in self._events if e["session_id"] == session_id and e["seq"] > since]
        return items[-80:]

    def get_session_policy(self, session_id: str) -> dict | None:
        sess = next((s for s in self._sessions if s["id"] == session_id), None)
        if not sess:
            return None
        lesson = self.get_lesson(sess["lesson_id"])
        if not lesson:
            return None
        scene = self.get_scene(lesson["scene_id"])
        if not scene:
            return None
        return {"scene_id": scene["id"], "scene_name": scene["name"], "capabilities": scene["capabilities"]}

    def lesson_stats(self, lesson_id: str) -> dict | None:
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return None
        sessions = [s for s in self._sessions if s["lesson_id"] == lesson_id]
        events = [e for e in self._events if any(s["id"] == e["session_id"] for s in sessions)]
        by_action: dict[str, int] = {}
        for e in events:
            by_action[e["action"]] = by_action.get(e["action"], 0) + 1
        return {"lesson": lesson, "session_count": len(sessions), "event_count": len(events), "action_count": by_action}

    def _event_summary(self, action: str, payload: dict) -> str:
        if action == "play":
            return f"播放片段：{payload.get('label','')}"
        if action == "pause":
            return "暂停播放"
        if action == "ab_loop":
            return "A-B 循环"
        if action == "speed":
            return f"倍速 {payload.get('speed')}"
        return action


db = InMemoryDB(base_dir=Path(__file__).resolve().parents[2])
