VR多模态交互媒介内容创作与发布系统 V1.0
# apps/api/main.py
# apps/api/main.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    from fastapi import FastAPI
import os
except Exception:  # pragma: no cover
try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
    interaction_router,
from apps.api.routers import (
    asset_router,
    audit_router,
    hr_router,
    interaction_router,
    project_router,
    scene_router,
    versioning_router,
)
    app.include_router(hr_router)
    app.include_router(project_router)
def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies
before running the API.")
    app = FastAPI(title="API")
    app.include_router(hr_router)
    app.include_router(project_router)
    app.include_router(asset_router)
    app.include_router(scene_router)
    app.include_router(interaction_router)
    app.include_router(versioning_router)
    app.include_router(audit_router)
  <title>VR多模态交互媒介内容创作与发布系统</title>
    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VR多模态交互媒介内容创作与发布系统</title>
  <style>
    :root { --bg:#0b1020; --panel:#121a33; --text:#e8ecff; --muted:#aab3d9; -
-accent:#6ee7ff; --danger:#ff5b6e; }
    body { margin:0; font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
background:linear-gradient(180deg,#070a14, var(--bg)); color:var(--text); }
    header { display:flex; align-items:center; justify-content:space-between;
padding:14px 18px; background:rgba(18,26,51,.8); border-bottom:1px solid
rgba(110,231,255,.18); position:sticky; top:0; backdrop-filter: blur(8px); }
    header .brand { font-weight:700; letter-spacing:.5px; }
    header .badge { font-size:12px; padding:4px 10px; border:1px solid
rgba(110,231,255,.35); border-radius:999px; color:var(--accent); }
    main { max-width:1180px; margin:18px auto; padding:0 18px 28px;
display:grid; grid-template-columns: 260px 1fr; gap:16px; }
    nav { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:12px; }
    nav a { display:block; color:var(--muted); text-decoration:none;
padding:10px 10px; border-radius:10px; }
    nav a:hover { background:rgba(110,231,255,.08); color:var(--text); }
    .panel { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:14px; }
    .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
    .card { border:1px solid rgba(110,231,255,.12); border-radius:12px;
padding:12px; background:rgba(9,12,24,.55); }
    .card h3 { margin:0 0 8px; font-size:14px; color:var(--accent); }
    .hint { color:var(--muted); font-size:12px; line-height:1.6; }
    .toolbar { display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 6px; }
    button { cursor:pointer; border-radius:10px; border:1px solid rgba(110,
231,255,.22); background:rgba(110,231,255,.10); color:var(--text);
padding:8px 12px; }
    button:hover { background:rgba(110,231,255,.16); }
    button.danger { border-color:rgba(255,91,110,.35); background:rgba(255,
91,110,.12); }
    .k { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas,
monospace; color:var(--accent); }
    .hidden { display:none !important; }
    #loginBox { max-width:520px; margin:10vh auto; padding:18px; }
    #loginBox .row { display:grid; gap:10px; margin-top:10px; }
    input { padding:10px 12px; border-radius:10px; border:1px solid rgba(110,
231,255,.18); background:rgba(255,255,255,.05); color:var(--text); }
    .row label { color:var(--muted); font-size:12px; }
    .row small { color:var(--muted); }
    #modal.modal-shell.modal { position:fixed; inset:0; background:rgba(0,0,
0,.55); display:flex; align-items:center; justify-content:center; }
    #modal .dialog { width:min(680px, 92vw); border-radius:14px;
background:rgba(18,26,51,.96); border:1px solid rgba(110,231,255,.18);
padding:14px; box-shadow:0 24px 80px rgba(0,0,0,.45); }
    #modal .dialog header { position:static; border:none;
background:transparent; padding:0 0 10px; }
    #modal .dialog .title { font-weight:700; }
    #modal .dialog .content { color:var(--muted); line-height:1.7; font-
size:13px; }
  </style>
</head>
<body>
  <div id="loginView">
    <div id="loginBox" class="panel">
      <h1 style="margin:0 0 8px; font-size:18px;
">VR多模态交互媒介内容创作与发布系统</h1>
      <div class="hint">V1.0 演示环境：用于截图与材料生成的最小可运行界面。<
/div>
      <form id="login-form" class="row" onsubmit="return
window.__app.login(event)">
        <label>用户名 <input name="username" value="admin" autocomplete=
"username" /></label>
        <label>密码 <input name="password" type="password" value="admin123"
autocomplete="current-password" /></label>
        <button type="submit">登录</button>
        <small>提示：输入任意值均可登录（用于演示与截图）。</small>
      </form>
    </div>
  </div>
        <a href="/#stations">工作台（Stations）</a>
  <div id="appView" class="hidden">
    <header>
      <div class="badge">V1.0</div>
    </header>
    <main>
      <nav>
        <a href="/#home">首页</a>
        <a href="/#zones">资源分区</a>
        <a href="/#stations">工作台（Stations）</a>
        <a href="/#inspections">交互检查</a>
        <a href="/#alerts">风险提醒</a>
        <a href="/#irrigation">发布流水</a>
        <a href="/#reports">统计报表</a>
      </nav>
      <section class="panel">
        <div id="pageTitle" style="font-weight:700; margin-bottom:10px;
">首页</div>
        <div id="pageBody"></div>
      </section>
    </main>
  </div>
  </div>
  <div id="modal" class="modal-shell modal hidden">
    <div class="dialog" role="dialog" aria-modal="true">
      <header>
        <div class="title" id="modalTitle">操作</div>
        <button class="danger" onclick="window.__rkModal.closeModal()
">关闭</button>
      </header>
      <div class="content" id="modalContent"></div>
    </div>
  </div>
    };
  <script>
    window.__rkModal = {
      closeModal() {
        document.getElementById('modal').classList.add('hidden');
      },
      openModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalContent').textContent = content;
        document.getElementById('modal').classList.remove('hidden');
      }
    };
      body.innerHTML = `<div id="${id}" class="card">
    function renderHome() {
      document.getElementById('pageTitle').textContent = '首页';
      document.getElementById('pageBody').innerHTML = `
        <div class="grid">
          <div class="card"><h3>项目概览</h3><div class=
"hint">资源、场景、交互与发布记录在此汇总展示。</div></div>
        </div>`;
    }
        <div id="stations" class="card">
    function renderSimplePage(title, id) {
      document.getElementById('pageTitle').textContent = title;
      const body = document.getElementById('pageBody');
      body.innerHTML = `<div id="${id}" class="card">
        <h3>${title}</h3>
      </div>`;
    }
'修改条目名称、标签与说明。')">编辑</button>
    function renderStations() {
      document.getElementById('pageTitle').textContent =
'工作台（Stations）';
      const body = document.getElementById('pageBody');
      body.innerHTML = `
        <div id="stations" class="card">
          <h3>Stations 列表</h3>
          <div class="hint">用于演示“新增/编辑/查看/删除”弹窗操作按钮文案。<
/div>
          <div class="toolbar">
            <button onclick="window.__rkModal.openModal('新增',
'创建新的条目并填写字段。')">新增</button>
            <button onclick="window.__rkModal.openModal('编辑',
'修改条目名称、标签与说明。')">编辑</button>
            <button onclick="window.__rkModal.openModal('查看',
'查看条目详情与引用关系。')">查看</button>
            <button class="danger" onclick="window.__rkModal.openModal('删除
', '删除条目前请确认无引用并记录审计。')">删除</button>
          </div>
          <div class="hint">提示：截图脚本会自动点击以上按钮并截取弹窗状态。
</div>
        </div>`;
    }
      login(e) {
    function route() {
      const hash = (location.hash || '#home').replace(/^#/, '');
      if (hash === 'home' || hash === '') return renderHome();
      if (hash === 'stations') return renderStations();
      if (hash === 'zones') return renderSimplePage('资源分区', 'zones');
      if (hash === 'inspections') return renderSimplePage('交互检查',
'inspections');
      if (hash === 'alerts') return renderSimplePage('风险提醒', 'alerts');
      if (hash === 'irrigation') return renderSimplePage('发布流水',
'irrigation');
      if (hash === 'reports') return renderSimplePage('统计报表', 'reports');
      document.getElementById('appView').classList.remove('hidden');
      return renderSimplePage('页面', hash);
    }
  </script>
    window.__app = {
      login(e) {
        e.preventDefault();
        localStorage.setItem('__demo_logged_in', '1');
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('appView').classList.remove('hidden');
        route();
        return false;
      }
    };
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level=
    window.addEventListener('hashchange', () => route());
if __name__ == "__main__":
    if (localStorage.getItem('__demo_logged_in') === '1') {
      document.getElementById('loginView').classList.add('hidden');
      document.getElementById('appView').classList.remove('hidden');
      route();
    }
  </script>
</body>
</html>"""
from .interaction import router as interaction_router
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}
    "hr_router",
    return app
    "asset_router",
    "scene_router",
app = create_app()
    "versioning_router",
    "audit_router",
def _main() -> None:
    import uvicorn
# -*- coding: utf-8 -*-
    port = int(os.environ.get("APP_PORT", "8010"))
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level=
"warning")
from apps.api.services import asset_repo
router = APIRouter(prefix="/api/assets", tags=["assets"])
if __name__ == "__main__":
    _main()
# apps/api/routers/__init__.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    aid = asset_repo.create_asset(
from .hr import router as hr_router
from .project import router as project_router
from .asset import router as asset_router
from .scene import router as scene_router
from .interaction import router as interaction_router
from .versioning import router as versioning_router
from .audit import router as audit_router
    )
__all__ = [
    "hr_router",
    "project_router",
    "asset_router",
    "scene_router",
    "interaction_router",
    "versioning_router",
    "audit_router",
]
# apps/api/routers/asset.py
# -*- coding: utf-8 -*-
from __future__ import annotations
router = APIRouter(prefix="/api/audit", tags=["audit"])
from fastapi import APIRouter, HTTPException
def list_audit(limit: int = 100):
from apps.api.schemas.asset import AssetCreate, AssetOut
from apps.api.services import asset_repo
# -*- coding: utf-8 -*-
from __future__ import annotations
router = APIRouter(prefix="/api/assets", tags=["assets"])
from pydantic import BaseModel, Field
from apps.api.services.store import InMemoryStore
@router.get("", response_model=list[AssetOut])
def list_assets(project_id: str):
    return asset_repo.list_assets(project_id)
class PositionIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
@router.post("", response_model=dict)
def create_asset(payload: AssetCreate):
    aid = asset_repo.create_asset(
        payload.project_id,
        payload.type,
        payload.filename,
        payload.sha256,
        payload.size,
        payload.tags,
        payload.meta_json,
    )
    return {"id": aid}
        return _STORE
@router.get("/departments")
@router.delete("/{asset_id}", response_model=dict)
def delete_asset(asset_id: str):
    ok = asset_repo.delete_asset(asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/audit.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    if not ok:
from fastapi import APIRouter
    return {"deleted": True}
from apps.api.services import audit_repo
def list_positions() -> list[dict]:
    return get_store().list_positions()
router = APIRouter(prefix="/api/audit", tags=["audit"])
def create_position(payload: PositionIn) -> dict:
    _id = get_store().create_position(payload.name, payload.dept_id)
@router.get("", response_model=list[dict])
def list_audit(limit: int = 100):
    return audit_repo.list_audit(limit=limit)
# apps/api/routers/hr.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    return {"deleted": True}
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
    return get_store().list_employees()
from apps.api.services.store import InMemoryStore
def create_employee(payload: EmployeeIn) -> dict:
    _id = get_store().create_employee(payload.name, payload.dept_id,
router = APIRouter(prefix="/api/hr", tags=["hr"])
    return {"id": _id}
@router.delete("/employees/{emp_id}")
class DepartmentIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
class PositionIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
from __future__ import annotations
from fastapi import APIRouter
class EmployeeIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
    title: str = Field(..., min_length=1, max_length=50)
def create_interaction(payload: InteractionCreate):
    iid = interaction_repo.create_interaction(payload.project_id,
def get_store() -> InMemoryStore:
    # module-level singleton to keep the example minimal.
    global _STORE
    try:
        return _STORE
    except NameError:
        _STORE = InMemoryStore()
        return _STORE
from fastapi import APIRouter, HTTPException
from apps.api.schemas.project import ProjectCreate, ProjectOut,
@router.get("/departments")
def list_departments() -> list[dict]:
    return get_store().list_departments()
@router.get("", response_model=list[ProjectOut])
def list_projects():
@router.post("/departments")
def create_department(payload: DepartmentIn) -> dict:
    _id = get_store().create_department(payload.name)
    return {"id": _id}
payload.constraints_json)
    return {"id": pid}
@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str) -> dict:
    ok = get_store().delete_department(dept_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
@router.patch("/{project_id}", response_model=dict)
def patch_project(project_id: str, payload: ProjectUpdate):
@router.get("/positions")
def list_positions() -> list[dict]:
    return get_store().list_positions()
changes")
    return {"updated": True}
@router.post("/positions")
def create_position(payload: PositionIn) -> dict:
    _id = get_store().create_position(payload.name, payload.dept_id)
    return {"id": _id}
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
@router.delete("/positions/{pos_id}")
def delete_position(pos_id: str) -> dict:
    ok = get_store().delete_position(pos_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
SceneNodeOut, SceneOut
from apps.api.services import scene_repo
@router.get("/employees")
def list_employees() -> list[dict]:
    return get_store().list_employees()
    sid = scene_repo.create_scene(payload.project_id, payload.name)
    return {"id": sid}
@router.post("/employees")
def create_employee(payload: EmployeeIn) -> dict:
    _id = get_store().create_employee(payload.name, payload.dept_id,
payload.title)
    return {"id": _id}
    nid = scene_repo.create_node(
        payload.scene_id,
@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: str) -> dict:
    ok = get_store().delete_employee(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/interaction.py
# -*- coding: utf-8 -*-
from __future__ import annotations
def list_nodes(scene_id: str):
from fastapi import APIRouter
# apps/api/routers/versioning.py
from apps.api.schemas.interaction import InteractionCreate, InteractionOut
from apps.api.services import interaction_repo
from fastapi import APIRouter
from apps.api.schemas.versioning import PublishCreate, PublishOut,
router = APIRouter(prefix="/api/interactions", tags=["interactions"])
from apps.api.services import publish_repo, versioning_repo
router = APIRouter(prefix="/api/versioning", tags=["versioning"])
@router.post("", response_model=dict)
def create_interaction(payload: InteractionCreate):
    iid = interaction_repo.create_interaction(payload.project_id,
payload.scene_id, payload.name, payload.enabled, payload.graph_json)
    return {"id": iid}
@router.get("/versions", response_model=list[VersionOut])
def list_versions(project_id: str):
@router.get("", response_model=list[InteractionOut])
def list_interactions(project_id: str):
    return interaction_repo.list_interactions(project_id)
# apps/api/routers/project.py
# -*- coding: utf-8 -*-
from __future__ import annotations
@router.get("/publish", response_model=list[PublishOut])
from fastapi import APIRouter, HTTPException
    return publish_repo.list_publish_records(project_id)
from apps.api.schemas.project import ProjectCreate, ProjectOut,
ProjectUpdate
from apps.api.services import project_repo
from __future__ import annotations
from dataclasses import dataclass
router = APIRouter(prefix="/api/projects", tags=["projects"])
@dataclass(frozen=True)
class Department:
@router.get("", response_model=list[ProjectOut])
def list_projects():
    return project_repo.list_projects()
@dataclass(frozen=True)
class Position:
@router.post("", response_model=dict)
def create_project(payload: ProjectCreate):
    pid = project_repo.create_project(payload.name, payload.target_device,
payload.constraints_json)
    return {"id": pid}
class Employee:
    id: str
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str):
    p = project_repo.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="not found")
    return p
# -*- coding: utf-8 -*-
from __future__ import annotations
@router.patch("/{project_id}", response_model=dict)
def patch_project(project_id: str, payload: ProjectUpdate):
    ok = project_repo.update_project(project_id, payload.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="not found or no
changes")
    return {"updated": True}
        conn.execute(
            "INSERT INTO asset(id,project_id,type,filename,sha256,size,tags,
@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str):
    ok = project_repo.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/publish.py
        rows = conn.execute("SELECT * FROM asset WHERE project_id=? ORDER BY
# apps/api/routers/scene.py
# -*- coding: utf-8 -*-
from __future__ import annotations
            d = dict(r)
from fastapi import APIRouter, HTTPException
            out.append(d)
from apps.api.schemas.scene import SceneCreate, SceneNodeCreate,
SceneNodeOut, SceneOut
from apps.api.services import scene_repo
        cur = conn.execute("DELETE FROM asset WHERE id=?", (asset_id,))
        return cur.rowcount > 0
router = APIRouter(prefix="/api/scenes", tags=["scenes"])
# -*- coding: utf-8 -*-
from __future__ import annotations
@router.post("", response_model=dict)
def create_scene(payload: SceneCreate):
    sid = scene_repo.create_scene(payload.project_id, payload.name)
    return {"id": sid}
    aid = new_id()
    with db() as conn:
@router.get("", response_model=list[SceneOut])
def list_scenes(project_id: str):
    return scene_repo.list_scenes(project_id)
            (aid, actor or "system", action, target_type, target_id,
json_dumps(detail or {}), utc_now()),
@router.post("/nodes", response_model=dict)
def create_node(payload: SceneNodeCreate):
    nid = scene_repo.create_node(
        payload.scene_id,
        payload.parent_id,
        payload.name,
        payload.node_type,
        payload.transform_json,
        payload.asset_ref_id,
        payload.props_json,
    )
    return {"id": nid}
def create_interaction(project_id: str, scene_id: str, name: str, enabled:
bool, graph_json: str) -> str:
@router.get("/{scene_id}/nodes", response_model=list[SceneNodeOut])
def list_nodes(scene_id: str):
    return scene_repo.list_nodes(scene_id)
# apps/api/routers/versioning.py
# -*- coding: utf-8 -*-
from __future__ import annotations
graph_json or "{}", utc_now()),
from fastapi import APIRouter
    return iid
from apps.api.schemas.versioning import PublishCreate, PublishOut,
VersionCreate, VersionOut
from apps.api.services import publish_repo, versioning_repo
ORDER BY created_at DESC", (project_id,)).fetchall()
        out = []
router = APIRouter(prefix="/api/versioning", tags=["versioning"])
            d = dict(r)
            d["enabled"] = bool(d.get("enabled"))
@router.post("/versions", response_model=dict)
def create_version(payload: VersionCreate):
    vid = versioning_repo.create_version(payload.project_id, payload.version,
payload.note)
    return {"id": vid}
import sqlite3
from apps.api.db import db
@router.get("/versions", response_model=list[VersionOut])
def list_versions(project_id: str):
    return versioning_repo.list_versions(project_id)
    pid = new_id()
    with db() as conn:
@router.post("/publish", response_model=dict)
def create_publish(payload: PublishCreate):
    pid = publish_repo.create_publish_record(payload.project_id,
payload.version_id, payload.channel, payload.note, payload.artifact_path)
    return {"id": pid}
        )
    return pid
@router.get("/publish", response_model=list[PublishOut])
def list_publish(project_id: str):
    return publish_repo.list_publish_records(project_id)
# apps/api/domain/__init__.py
        return [dict(r) for r in rows]
# apps/api/domain/models.py
# -*- coding: utf-8 -*-
from __future__ import annotations
.fetchone()
from dataclasses import dataclass
from datetime import datetime
    allow = {"name", "target_device", "constraints_json", "status"}
    fields = {k: v for k, v in patch.items() if k in allow and v is not None}
@dataclass(frozen=True)
class Department:
    id: str
    name: str
    created_at: datetime
        cur = conn.execute(f"UPDATE project SET {sets} WHERE id=?", values)
        return cur.rowcount > 0
@dataclass(frozen=True)
class Position:
    id: str
    name: str
    dept_id: str
    created_at: datetime
from __future__ import annotations
from apps.api.db import db
@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    dept_id: str
    title: str
    created_at: datetime
# apps/api/services/__init__.py
            (pid, project_id, version_id, channel or "local_export", note or
# apps/api/services/asset_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
def list_publish_records(project_id: str) -> list[dict]:
import sqlite3
        rows = conn.execute("SELECT * FROM publish_record WHERE project_id=?
from apps.api.db import db
from apps.api.util import csv_tags, new_id, parse_tags, utc_now
# apps/api/services/scene_repo.py
# -*- coding: utf-8 -*-
def create_asset(project_id: str, type: str, filename: str, sha256: str,
size: int, tags: list[str], meta_json: str) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO asset(id,project_id,type,filename,sha256,size,tags,
meta_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (aid, project_id, type, filename, sha256, int(size),
csv_tags(tags), meta_json or "{}", utc_now()),
        )
    return aid
        rows = conn.execute("SELECT * FROM scene WHERE project_id=? ORDER BY
created_at DESC", (project_id,)).fetchall()
def list_assets(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM asset WHERE project_id=? ORDER BY
created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["tags"] = parse_tags(d.get("tags", ""))
            out.append(d)
        return out
", asset_ref_id, props_json or "{}", utc_now()),
        )
def delete_asset(asset_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM asset WHERE id=?", (asset_id,))
        return cur.rowcount > 0
# apps/api/services/audit_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
# -*- coding: utf-8 -*-
from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now
from datetime import datetime
from typing import Any
def write_audit(actor: str, action: str, target_type: str, target_id: str,
detail: dict) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO audit_log(id,actor,action,target_type,target_id,
detail_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (aid, actor or "system", action, target_type, target_id,
json_dumps(detail or {}), utc_now()),
        )
    return aid
        _id = self._new_id()
        self._departments[_id] = {"id": _id, "name": name, "created_at":
def list_audit(limit: int = 100) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM audit_log ORDER BY created_at
DESC LIMIT ?", (int(limit),)).fetchall()
        return [dict(r) for r in rows]
# apps/api/services/interaction_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
        self._positions[_id] = {"id": _id, "name": name, "dept_id": dept_id,
from apps.api.db import db
from apps.api.util import new_id, utc_now
    def delete_position(self, pos_id: str) -> bool:
        return self._positions.pop(pos_id, None) is not None
def create_interaction(project_id: str, scene_id: str, name: str, enabled:
bool, graph_json: str) -> str:
    iid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO interaction(id,project_id,scene_id,name,enabled,
graph_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (iid, project_id, scene_id, name, 1 if enabled else 0,
graph_json or "{}", utc_now()),
        )
    return iid
        return _id
    def delete_employee(self, emp_id: str) -> bool:
def list_interactions(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM interaction WHERE project_id=?
ORDER BY created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["enabled"] = bool(d.get("enabled"))
            out.append(d)
        return out
# apps/api/services/project_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    return [dict(r) for r in rows]
import sqlite3
    scenes = conn.execute("SELECT id,name,created_at FROM scene WHERE
from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now
        "SELECT id,scene_id,name,enabled,graph_json,created_at FROM
interaction WHERE project_id=? ORDER BY created_at ASC",
def create_project(name: str, target_device: str, constraints_json: str) ->
str:
    pid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO project(id,name,target_device,constraints_json,
status,created_at) VALUES (?,?,?,?,?,?)",
            (pid, name, target_device, constraints_json or "{}", "draft",
utc_now()),
        )
    return pid
        conn.execute(
            "INSERT INTO version(id,project_id,version,note,snapshot_json,
def list_projects() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM project ORDER BY created_at DESC")
.fetchall()
        return [dict(r) for r in rows]
def list_versions(project_id: str) -> list[dict]:
    with db() as conn:
def get_project(project_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT * FROM project WHERE id=?", (project_id,))
.fetchone()
        return dict(row) if row else None
from __future__ import annotations
from pydantic import BaseModel, Field
def update_project(project_id: str, patch: dict) -> bool:
    allow = {"name", "target_device", "constraints_json", "status"}
    fields = {k: v for k, v in patch.items() if k in allow and v is not None}
# apps/api/__init__.py
    if not fields:
        return False
    sets = ", ".join([f"{k}=?" for k in fields.keys()])
    values = list(fields.values()) + [project_id]
    with db() as conn:
        cur = conn.execute(f"UPDATE project SET {sets} WHERE id=?", values)
        return cur.rowcount > 0
from typing import Iterator
def resolve_db_path() -> Path:
def delete_project(project_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM project WHERE id=?", (project_id,))
        return cur.rowcount > 0
# apps/api/services/publish_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
CREATE TABLE IF NOT EXISTS project (
from apps.api.db import db
from apps.api.util import new_id, utc_now
  target_device TEXT NOT NULL,
  constraints_json TEXT NOT NULL,
def create_publish_record(project_id: str, version_id: str, channel: str,
note: str, artifact_path: str) -> str:
    pid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO publish_record(id,project_id,version_id,channel,
note,artifact_path,created_at) VALUES (?,?,?,?,?,?,?)",
            (pid, project_id, version_id, channel or "local_export", note or
"", artifact_path or "", utc_now()),
        )
    return pid
  meta_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
def list_publish_records(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM publish_record WHERE project_id=?
ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
# apps/api/services/scene_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
  name TEXT NOT NULL,
from apps.api.db import db
from apps.api.util import new_id, utc_now
);
CREATE INDEX IF NOT EXISTS idx_scene_project ON scene(project_id);
def create_scene(project_id: str, name: str) -> str:
    sid = new_id()
    with db() as conn:
        conn.execute("INSERT INTO scene(id,project_id,name,created_at)
VALUES (?,?,?,?)", (sid, project_id, name, utc_now()))
    return sid
  transform_json TEXT NOT NULL,
  asset_ref_id TEXT,
def list_scenes(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM scene WHERE project_id=? ORDER BY
created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
CREATE TABLE IF NOT EXISTS interaction (
  id TEXT PRIMARY KEY,
def create_node(scene_id: str, parent_id: str | None, name: str, node_type:
str, transform_json: str, asset_ref_id: str | None, props_json: str) -> str:
    nid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO scene_node(id,scene_id,parent_id,name,node_type,
transform_json,asset_ref_id,props_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)
",
            (nid, scene_id, parent_id, name, node_type, transform_json or "{}
", asset_ref_id, props_json or "{}", utc_now()),
        )
    return nid
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
def list_nodes(scene_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM scene_node WHERE scene_id=? ORDER
BY created_at ASC", (scene_id,)).fetchall()
        return [dict(r) for r in rows]
# apps/api/services/store.py
# -*- coding: utf-8 -*-
from __future__ import annotations
version);
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import uuid4
  channel TEXT NOT NULL,
  note TEXT NOT NULL,
class InMemoryStore:
    def __init__(self) -> None:
        self._departments: dict[str, dict[str, Any]] = {}
        self._positions: dict[str, dict[str, Any]] = {}
        self._employees: dict[str, dict[str, Any]] = {}
CREATE INDEX IF NOT EXISTS idx_publish_project ON publish_record(project_id);
    def _new_id(self) -> str:
        return uuid4().hex
  actor TEXT NOT NULL,
    def list_departments(self) -> list[dict[str, Any]]:
        return list(self._departments.values())
  target_id TEXT NOT NULL,
    def create_department(self, name: str) -> str:
        _id = self._new_id()
        self._departments[_id] = {"id": _id, "name": name, "created_at":
datetime.utcnow().isoformat()}
        return _id
    )
    def delete_department(self, dept_id: str) -> bool:
        return self._departments.pop(dept_id, None) is not None
    path = resolve_db_path()
    def list_positions(self) -> list[dict[str, Any]]:
        return list(self._positions.values())
    conn.row_factory = sqlite3.Row
    def create_position(self, name: str, dept_id: str) -> str:
        _id = self._new_id()
        self._positions[_id] = {"id": _id, "name": name, "dept_id": dept_id,
"created_at": datetime.utcnow().isoformat()}
        return _id
        conn.close()
    def delete_position(self, pos_id: str) -> bool:
        return self._positions.pop(pos_id, None) is not None
# -*- coding: utf-8 -*-
    def list_employees(self) -> list[dict[str, Any]]:
        return list(self._employees.values())
class AssetCreate(BaseModel):
    def create_employee(self, name: str, dept_id: str, title: str) -> str:
        _id = self._new_id()
        self._employees[_id] = {
            "id": _id,
            "name": name,
            "dept_id": dept_id,
            "title": title,
            "created_at": datetime.utcnow().isoformat(),
        }
        return _id
    type: str
    def delete_employee(self, emp_id: str) -> bool:
        return self._employees.pop(emp_id, None) is not None
# apps/api/services/versioning_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    created_at: str
import json
# -*- coding: utf-8 -*-
from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now
class InteractionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
def _asset_manifest(conn, project_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id,type,filename,sha256,size,tags,meta_json,created_at FROM
asset WHERE project_id=? ORDER BY created_at ASC",
        (project_id,),
    ).fetchall()
    return [dict(r) for r in rows]
    scene_id: str
    name: str
def _snapshot(conn, project_id: str) -> dict:
    scenes = conn.execute("SELECT id,name,created_at FROM scene WHERE
project_id=? ORDER BY created_at ASC", (project_id,)).fetchall()
    interactions = conn.execute(
        "SELECT id,scene_id,name,enabled,graph_json,created_at FROM
interaction WHERE project_id=? ORDER BY created_at ASC",
        (project_id,),
    ).fetchall()
    return {
        "scenes": [dict(r) for r in scenes],
        "interactions": [dict(r) for r in interactions],
    }
    constraints_json: str = Field("{}", max_length=4000, description=
"性能/规格约束 JSON")
def create_version(project_id: str, version: str, note: str) -> str:
    vid = new_id()
    with db() as conn:
        manifest = _asset_manifest(conn, project_id)
        snap = _snapshot(conn, project_id)
        conn.execute(
            "INSERT INTO version(id,project_id,version,note,snapshot_json,
asset_manifest_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (vid, project_id, version, note or "", json_dumps(snap),
json_dumps(manifest), utc_now()),
        )
    return vid
# apps/api/schemas/scene.py
# -*- coding: utf-8 -*-
def list_versions(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM version WHERE project_id=? ORDER
BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
# apps/api/schemas/common.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    name: str
from pydantic import BaseModel, Field
class SceneNodeCreate(BaseModel):
    scene_id: str = Field(..., min_length=8, max_length=64)
class IdResponse(BaseModel):
    id: str = Field(..., description="资源唯一标识")
# apps/__init__.py
    transform_json: str = Field("{}", max_length=4000)
# apps/api/__init__.py
    props_json: str = Field("{}", max_length=8000)
# apps/api/db.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    parent_id: str | None
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
    created_at: str
# apps/api/schemas/versioning.py
def resolve_db_path() -> Path:
    base = os.environ.get("APP_DB_DIR", "").strip()
    root = Path(base).resolve() if base else Path.cwd().resolve()
    return root / "data" / "app.db"
    project_id: str = Field(..., min_length=8, max_length=64)
    version: str = Field(..., min_length=2, max_length=20, description=
def ensure_db_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  target_device TEXT NOT NULL,
  constraints_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
    version_id: str = Field(..., min_length=8, max_length=64)
CREATE TABLE IF NOT EXISTS asset (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  type TEXT NOT NULL,
  filename TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  size INTEGER NOT NULL,
  tags TEXT NOT NULL,
  meta_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_asset_project ON asset(project_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_unique_hash ON asset(project_id,
sha256);
from __future__ import annotations
CREATE TABLE IF NOT EXISTS scene (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_scene_project ON scene(project_id);
        self.assertEqual(resp.json().get("status"), "ok")
CREATE TABLE IF NOT EXISTS scene_node (
  id TEXT PRIMARY KEY,
  scene_id TEXT NOT NULL,
  parent_id TEXT,
  name TEXT NOT NULL,
  node_type TEXT NOT NULL,
  transform_json TEXT NOT NULL,
  asset_ref_id TEXT,
  props_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scene_id) REFERENCES scene(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_node_scene ON scene_node(scene_id);
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
CREATE TABLE IF NOT EXISTS interaction (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  scene_id TEXT NOT NULL,
  name TEXT NOT NULL,
  enabled INTEGER NOT NULL,
  graph_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
  FOREIGN KEY(scene_id) REFERENCES scene(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_interaction_project ON interaction(project_id)
;
            t = t.replace(",", " ")
CREATE TABLE IF NOT EXISTS version (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  version TEXT NOT NULL,
  note TEXT NOT NULL,
  snapshot_json TEXT NOT NULL,
  asset_manifest_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_version_unique ON version(project_id,
version);
    for t in (tags_csv or "").split(","):
CREATE TABLE IF NOT EXISTS publish_record (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  note TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
  FOREIGN KEY(version_id) REFERENCES version(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_publish_project ON publish_record(project_id);
</ul>
</body></html>
CREATE TABLE IF NOT EXISTS audit_log (
  id TEXT PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  detail_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(created_at);
"""
    )
      <li><a href="./student.html">员工端</a></li>
      <li><a href="./admin.html">管理员端</a></li>
@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    path = resolve_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    ensure_db_schema(conn)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
# apps/api/schemas/__init__.py
</ul>
# apps/api/schemas/asset.py
# -*- coding: utf-8 -*-
from __future__ import annotations
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
from pydantic import BaseModel, Field
<title>教师端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>教师端</h1>
class AssetCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    type: str = Field(..., min_length=2, max_length=20)
    filename: str = Field(..., min_length=1, max_length=160)
    sha256: str = Field(..., min_length=16, max_length=80)
    size: int = Field(..., ge=0, le=2_000_000_000)
    tags: list[str] = Field(default_factory=list)
    meta_json: str = Field("{}", max_length=8000)
from __future__ import annotations
import os
class AssetOut(BaseModel):
    id: str
    project_id: str
    type: str
    filename: str
    sha256: str
    size: int
    tags: list[str]
    meta_json: str
    created_at: str
# apps/api/schemas/interaction.py
# -*- coding: utf-8 -*-
from __future__ import annotations
)
from pydantic import BaseModel, Field
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies
class InteractionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    scene_id: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=80)
    enabled: bool = Field(True)
    graph_json: str = Field("{}", max_length=20000)
    app.include_router(interaction_router)
    app.include_router(versioning_router)
class InteractionOut(BaseModel):
    id: str
    project_id: str
    scene_id: str
    name: str
    enabled: bool
    graph_json: str
    created_at: str
# apps/api/schemas/project.py
# -*- coding: utf-8 -*-
from __future__ import annotations
-accent:#6ee7ff; --danger:#ff5b6e; }
from pydantic import BaseModel, Field
background:linear-gradient(180deg,#070a14, var(--bg)); color:var(--text); }
    header { display:flex; align-items:center; justify-content:space-between;
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, description=
"项目名称")
    target_device: str = Field(..., min_length=2, max_length=30, description=
"目标设备")
    constraints_json: str = Field("{}", max_length=4000, description=
"性能/规格约束 JSON")
    nav { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:12px; }
class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    target_device: str | None = Field(None, min_length=2, max_length=30)
    constraints_json: str | None = Field(None, max_length=4000)
    status: str | None = Field(None, max_length=30)
    .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
    .card { border:1px solid rgba(110,231,255,.12); border-radius:12px;
class ProjectOut(BaseModel):
    id: str
    name: str
    target_device: str
    constraints_json: str
    status: str
    created_at: str
# apps/api/schemas/scene.py
# -*- coding: utf-8 -*-
from __future__ import annotations
    .k { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas,
from pydantic import BaseModel, Field
    .hidden { display:none !important; }
    #loginBox { max-width:520px; margin:10vh auto; padding:18px; }
class SceneCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=80)
    .row label { color:var(--muted); font-size:12px; }
    .row small { color:var(--muted); }
class SceneOut(BaseModel):
    id: str
    project_id: str
    name: str
    created_at: str
    #modal .dialog header { position:static; border:none;
background:transparent; padding:0 0 10px; }
class SceneNodeCreate(BaseModel):
    scene_id: str = Field(..., min_length=8, max_length=64)
    parent_id: str | None = Field(None, max_length=64)
    name: str = Field(..., min_length=1, max_length=80)
    node_type: str = Field(..., min_length=2, max_length=30)
    transform_json: str = Field("{}", max_length=4000)
    asset_ref_id: str | None = Field(None, max_length=64)
    props_json: str = Field("{}", max_length=8000)
      <h1 style="margin:0 0 8px; font-size:18px;
">VR多模态交互媒介内容创作与发布系统</h1>
class SceneNodeOut(BaseModel):
    id: str
    scene_id: str
    parent_id: str | None
    name: str
    node_type: str
    transform_json: str
    asset_ref_id: str | None
    props_json: str
    created_at: str
# apps/api/schemas/versioning.py
# -*- coding: utf-8 -*-
from __future__ import annotations
  <div id="appView" class="hidden">
from pydantic import BaseModel, Field
      <div class="badge">V1.0</div>
    </header>
class VersionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    version: str = Field(..., min_length=2, max_length=20, description=
"版本号，如 V1.0.0")
    note: str = Field("", max_length=1000)
        <a href="/#inspections">交互检查</a>
        <a href="/#alerts">风险提醒</a>
class VersionOut(BaseModel):
    id: str
    project_id: str
    version: str
    note: str
    snapshot_json: str
    asset_manifest_json: str
    created_at: str
    </main>
  </div>
class PublishCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    version_id: str = Field(..., min_length=8, max_length=64)
    channel: str = Field("local_export", max_length=40)
    note: str = Field("", max_length=1000)
    artifact_path: str = Field("", max_length=300)
      </header>
      <div class="content" id="modalContent"></div>
class PublishOut(BaseModel):
    id: str
    project_id: str
    version_id: str
    channel: str
    note: str
    artifact_path: str
    created_at: str
# apps/api/tests/__init__.py
# -*- coding: utf-8 -*-
        document.getElementById('modal').classList.remove('hidden');
# apps/api/tests/test_health.py
# -*- coding: utf-8 -*-
from __future__ import annotations
      document.getElementById('pageTitle').textContent = '首页';
import unittest
        <div class="grid">
from fastapi.testclient import TestClient
"hint">资源、场景、交互与发布记录在此汇总展示。</div></div>
from apps.api.main import create_app
    }
    function renderSimplePage(title, id) {
class HealthEndpointTests(unittest.TestCase):
    def test_health_ok(self) -> None:
        client = TestClient(create_app())
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")
    function renderStations() {
      document.getElementById('pageTitle').textContent =
if __name__ == "__main__":
    unittest.main()
      body.innerHTML = `
# apps/api/util.py
# -*- coding: utf-8 -*-
from __future__ import annotations
/div>
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4
            <button onclick="window.__rkModal.openModal('查看',
'查看条目详情与引用关系。')">查看</button>
def new_id() -> str:
    return uuid4().hex
          </div>
          <div class="hint">提示：截图脚本会自动点击以上按钮并截取弹窗状态。
def utc_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
    }
    function route() {
def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
      if (hash === 'stations') return renderStations();
      if (hash === 'zones') return renderSimplePage('资源分区', 'zones');
def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()
'irrigation');
      if (hash === 'reports') return renderSimplePage('统计报表', 'reports');
def csv_tags(tags: list[str]) -> str:
    clean = []
    for t in tags:
        t = (t or "").strip()
        if not t:
            continue
        if "," in t:
            t = t.replace(",", " ")
        clean.append(t)
    # de-dup, keep order
    seen = set()
    out = []
    for t in clean:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return ",".join(out)
  </script>
</body>
def parse_tags(tags_csv: str) -> list[str]:
    items = []
    for t in (tags_csv or "").split(","):
        t = t.strip()
        if t:
            items.append(t)
    return items
# apps/web/admin.html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
content="width=device-width, initial-scale=1" />
<title>管理端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>管理端</h1>
<ul>
  <li>核心动作按钮口径：新增 / 编辑 / 查看 / 删除</li>
</ul>
</body></html>
# apps/web/index.html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>VR多模态交互媒介内容创作与发布系统</title>
  </head>
  <body>
    <h1>VR多模态交互媒介内容创作与发布系统</h1>
    <ul>
      <li><a href="./teacher.html">业务专员端</a></li>
      <li><a href="./student.html">员工端</a></li>
      <li><a href="./admin.html">管理员端</a></li>
    </ul>
  </body>
</html>
# apps/web/student.html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
content="width=device-width, initial-scale=1" />
<title>学生端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>学生端</h1>
<ul>
  <li>当前版本：V1.0（示例）</li>
  <li>体验说明：按交互节点顺序体验并记录问题</li>
  <li>反馈方式：提交问题编号与截图（后续版本接入反馈单）</li>
</ul>
</body></html>
# apps/web/teacher.html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
content="width=device-width, initial-scale=1" />
<title>教师端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>教师端</h1>
<ol>
  <li>查看项目概览与关键指标（资源数、场景数、交互数、最近发布）。</li>
  <li>对比两个版本的变更摘要（资源替换、交互规则变更）。</li>
  <li>导出发布说明与清单，用于验收留痕。</li>
</ol>
</body></html>
# apps/api/main.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
from apps.api.routers import (
    asset_router,
    audit_router,
    hr_router,
    interaction_router,
    project_router,
    scene_router,
    versioning_router,
)
def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies
before running the API.")
    app = FastAPI(title="API")
    app.include_router(hr_router)
    app.include_router(project_router)
    app.include_router(asset_router)
    app.include_router(scene_router)
    app.include_router(interaction_router)
    app.include_router(versioning_router)
    app.include_router(audit_router)
    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VR多模态交互媒介内容创作与发布系统</title>
  <style>
    :root { --bg:#0b1020; --panel:#121a33; --text:#e8ecff; --muted:#aab3d9; -
-accent:#6ee7ff; --danger:#ff5b6e; }
    body { margin:0; font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
background:linear-gradient(180deg,#070a14, var(--bg)); color:var(--text); }
    header { display:flex; align-items:center; justify-content:space-between;
padding:14px 18px; background:rgba(18,26,51,.8); border-bottom:1px solid
rgba(110,231,255,.18); position:sticky; top:0; backdrop-filter: blur(8px); }
    header .brand { font-weight:700; letter-spacing:.5px; }
    header .badge { font-size:12px; padding:4px 10px; border:1px solid
rgba(110,231,255,.35); border-radius:999px; color:var(--accent); }
    main { max-width:1180px; margin:18px auto; padding:0 18px 28px;
display:grid; grid-template-columns: 260px 1fr; gap:16px; }
    nav { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:12px; }
    nav a { display:block; color:var(--muted); text-decoration:none;
padding:10px 10px; border-radius:10px; }
    nav a:hover { background:rgba(110,231,255,.08); color:var(--text); }
    .panel { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:14px; }
    .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
    .card { border:1px solid rgba(110,231,255,.12); border-radius:12px;
padding:12px; background:rgba(9,12,24,.55); }
    .card h3 { margin:0 0 8px; font-size:14px; color:var(--accent); }
    .hint { color:var(--muted); font-size:12px; line-height:1.6; }
    .toolbar { display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 6px; }
    button { cursor:pointer; border-radius:10px; border:1px solid rgba(110,
231,255,.22); background:rgba(110,231,255,.10); color:var(--text);
padding:8px 12px; }
    button:hover { background:rgba(110,231,255,.16); }
    button.danger { border-color:rgba(255,91,110,.35); background:rgba(255,
91,110,.12); }
    .k { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas,
monospace; color:var(--accent); }
    .hidden { display:none !important; }
    #loginBox { max-width:520px; margin:10vh auto; padding:18px; }
    #loginBox .row { display:grid; gap:10px; margin-top:10px; }
    input { padding:10px 12px; border-radius:10px; border:1px solid rgba(110,
231,255,.18); background:rgba(255,255,255,.05); color:var(--text); }
    .row label { color:var(--muted); font-size:12px; }
    .row small { color:var(--muted); }
    #modal.modal-shell.modal { position:fixed; inset:0; background:rgba(0,0,
0,.55); display:flex; align-items:center; justify-content:center; }
    #modal .dialog { width:min(680px, 92vw); border-radius:14px;
background:rgba(18,26,51,.96); border:1px solid rgba(110,231,255,.18);
padding:14px; box-shadow:0 24px 80px rgba(0,0,0,.45); }
    #modal .dialog header { position:static; border:none;
background:transparent; padding:0 0 10px; }
    #modal .dialog .title { font-weight:700; }
    #modal .dialog .content { color:var(--muted); line-height:1.7; font-
size:13px; }
  </style>
</head>
<body>
  <div id="loginView">
    <div id="loginBox" class="panel">
      <h1 style="margin:0 0 8px; font-size:18px;
">VR多模态交互媒介内容创作与发布系统</h1>
      <div class="hint">V1.0 演示环境：用于截图与材料生成的最小可运行界面。<
/div>
      <form id="login-form" class="row" onsubmit="return
window.__app.login(event)">
        <label>用户名 <input name="username" value="admin" autocomplete=
"username" /></label>
        <label>密码 <input name="password" type="password" value="admin123"
autocomplete="current-password" /></label>
        <button type="submit">登录</button>
        <small>提示：输入任意值均可登录（用于演示与截图）。</small>
      </form>
    </div>
  </div>
  <div id="appView" class="hidden">
    <header>
      <div class="badge">V1.0</div>
    </header>
    <main>
      <nav>
        <a href="/#home">首页</a>
        <a href="/#zones">资源分区</a>
        <a href="/#stations">工作台（Stations）</a>
        <a href="/#inspections">交互检查</a>
        <a href="/#alerts">风险提醒</a>
        <a href="/#irrigation">发布流水</a>
        <a href="/#reports">统计报表</a>
      </nav>
      <section class="panel">
        <div id="pageTitle" style="font-weight:700; margin-bottom:10px;
">首页</div>
        <div id="pageBody"></div>
      </section>
    </main>
  </div>
  <div id="modal" class="modal-shell modal hidden">
    <div class="dialog" role="dialog" aria-modal="true">
      <header>
        <div class="title" id="modalTitle">操作</div>
        <button class="danger" onclick="window.__rkModal.closeModal()
">关闭</button>
      </header>
      <div class="content" id="modalContent"></div>
    </div>
  </div>
  <script>
    window.__rkModal = {
      closeModal() {
        document.getElementById('modal').classList.add('hidden');
      },
      openModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalContent').textContent = content;
        document.getElementById('modal').classList.remove('hidden');
      }
    };
    function renderHome() {
      document.getElementById('pageTitle').textContent = '首页';
      document.getElementById('pageBody').innerHTML = `
        <div class="grid">
          <div class="card"><h3>项目概览</h3><div class=
"hint">资源、场景、交互与发布记录在此汇总展示。</div></div>
        </div>`;
    }
    function renderSimplePage(title, id) {
      document.getElementById('pageTitle').textContent = title;
      const body = document.getElementById('pageBody');
      body.innerHTML = `<div id="${id}" class="card">
        <h3>${title}</h3>
      </div>`;
    }
    function renderStations() {
      document.getElementById('pageTitle').textContent =
'工作台（Stations）';
      const body = document.getElementById('pageBody');
      body.innerHTML = `
        <div id="stations" class="card">
          <h3>Stations 列表</h3>
          <div class="hint">用于演示“新增/编辑/查看/删除”弹窗操作按钮文案。<
/div>
          <div class="toolbar">
            <button onclick="window.__rkModal.openModal('新增',
'创建新的条目并填写字段。')">新增</button>
            <button onclick="window.__rkModal.openModal('编辑',
'修改条目名称、标签与说明。')">编辑</button>
            <button onclick="window.__rkModal.openModal('查看',
'查看条目详情与引用关系。')">查看</button>
            <button class="danger" onclick="window.__rkModal.openModal('删除
', '删除条目前请确认无引用并记录审计。')">删除</button>
          </div>
          <div class="hint">提示：截图脚本会自动点击以上按钮并截取弹窗状态。
</div>
        </div>`;
    }
    function route() {
      const hash = (location.hash || '#home').replace(/^#/, '');
      if (hash === 'home' || hash === '') return renderHome();
      if (hash === 'stations') return renderStations();
      if (hash === 'zones') return renderSimplePage('资源分区', 'zones');
      if (hash === 'inspections') return renderSimplePage('交互检查',
'inspections');
      if (hash === 'alerts') return renderSimplePage('风险提醒', 'alerts');
      if (hash === 'irrigation') return renderSimplePage('发布流水',
'irrigation');
      if (hash === 'reports') return renderSimplePage('统计报表', 'reports');
      return renderSimplePage('页面', hash);
    }
    window.__app = {
      login(e) {
        e.preventDefault();
        localStorage.setItem('__demo_logged_in', '1');
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('appView').classList.remove('hidden');
        route();
        return false;
      }
    };
    window.addEventListener('hashchange', () => route());
    if (localStorage.getItem('__demo_logged_in') === '1') {
      document.getElementById('loginView').classList.add('hidden');
      document.getElementById('appView').classList.remove('hidden');
      route();
    }
  </script>
</body>
</html>"""
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}
    return app
app = create_app()
def _main() -> None:
    import uvicorn
    port = int(os.environ.get("APP_PORT", "8010"))
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level=
"warning")
if __name__ == "__main__":
    _main()
# apps/api/routers/__init__.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from .hr import router as hr_router
from .project import router as project_router
from .asset import router as asset_router
from .scene import router as scene_router
from .interaction import router as interaction_router
from .versioning import router as versioning_router
from .audit import router as audit_router
__all__ = [
    "hr_router",
    "project_router",
    "asset_router",
    "scene_router",
    "interaction_router",
    "versioning_router",
    "audit_router",
]
# apps/api/routers/asset.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from apps.api.schemas.asset import AssetCreate, AssetOut
from apps.api.services import asset_repo
router = APIRouter(prefix="/api/assets", tags=["assets"])
@router.get("", response_model=list[AssetOut])
def list_assets(project_id: str):
    return asset_repo.list_assets(project_id)
@router.post("", response_model=dict)
def create_asset(payload: AssetCreate):
    aid = asset_repo.create_asset(
        payload.project_id,
        payload.type,
        payload.filename,
        payload.sha256,
        payload.size,
        payload.tags,
        payload.meta_json,
    )
    return {"id": aid}
@router.delete("/{asset_id}", response_model=dict)
def delete_asset(asset_id: str):
    ok = asset_repo.delete_asset(asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/audit.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter
from apps.api.services import audit_repo
router = APIRouter(prefix="/api/audit", tags=["audit"])
@router.get("", response_model=list[dict])
def list_audit(limit: int = 100):
    return audit_repo.list_audit(limit=limit)
# apps/api/routers/hr.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from apps.api.services.store import InMemoryStore
router = APIRouter(prefix="/api/hr", tags=["hr"])
class DepartmentIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
class PositionIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
class EmployeeIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
    title: str = Field(..., min_length=1, max_length=50)
def get_store() -> InMemoryStore:
    # module-level singleton to keep the example minimal.
    global _STORE
    try:
        return _STORE
    except NameError:
        _STORE = InMemoryStore()
        return _STORE
@router.get("/departments")
def list_departments() -> list[dict]:
    return get_store().list_departments()
@router.post("/departments")
def create_department(payload: DepartmentIn) -> dict:
    _id = get_store().create_department(payload.name)
    return {"id": _id}
@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str) -> dict:
    ok = get_store().delete_department(dept_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
@router.get("/positions")
def list_positions() -> list[dict]:
    return get_store().list_positions()
@router.post("/positions")
def create_position(payload: PositionIn) -> dict:
    _id = get_store().create_position(payload.name, payload.dept_id)
    return {"id": _id}
@router.delete("/positions/{pos_id}")
def delete_position(pos_id: str) -> dict:
    ok = get_store().delete_position(pos_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
@router.get("/employees")
def list_employees() -> list[dict]:
    return get_store().list_employees()
@router.post("/employees")
def create_employee(payload: EmployeeIn) -> dict:
    _id = get_store().create_employee(payload.name, payload.dept_id,
payload.title)
    return {"id": _id}
@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: str) -> dict:
    ok = get_store().delete_employee(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/interaction.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter
from apps.api.schemas.interaction import InteractionCreate, InteractionOut
from apps.api.services import interaction_repo
router = APIRouter(prefix="/api/interactions", tags=["interactions"])
@router.post("", response_model=dict)
def create_interaction(payload: InteractionCreate):
    iid = interaction_repo.create_interaction(payload.project_id,
payload.scene_id, payload.name, payload.enabled, payload.graph_json)
    return {"id": iid}
@router.get("", response_model=list[InteractionOut])
def list_interactions(project_id: str):
    return interaction_repo.list_interactions(project_id)
# apps/api/routers/project.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from apps.api.schemas.project import ProjectCreate, ProjectOut,
ProjectUpdate
from apps.api.services import project_repo
router = APIRouter(prefix="/api/projects", tags=["projects"])
@router.get("", response_model=list[ProjectOut])
def list_projects():
    return project_repo.list_projects()
@router.post("", response_model=dict)
def create_project(payload: ProjectCreate):
    pid = project_repo.create_project(payload.name, payload.target_device,
payload.constraints_json)
    return {"id": pid}
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str):
    p = project_repo.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="not found")
    return p
@router.patch("/{project_id}", response_model=dict)
def patch_project(project_id: str, payload: ProjectUpdate):
    ok = project_repo.update_project(project_id, payload.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="not found or no
changes")
    return {"updated": True}
@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str):
    ok = project_repo.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/publish.py
# apps/api/routers/scene.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from apps.api.schemas.scene import SceneCreate, SceneNodeCreate,
SceneNodeOut, SceneOut
from apps.api.services import scene_repo
router = APIRouter(prefix="/api/scenes", tags=["scenes"])
@router.post("", response_model=dict)
def create_scene(payload: SceneCreate):
    sid = scene_repo.create_scene(payload.project_id, payload.name)
    return {"id": sid}
@router.get("", response_model=list[SceneOut])
def list_scenes(project_id: str):
    return scene_repo.list_scenes(project_id)
@router.post("/nodes", response_model=dict)
def create_node(payload: SceneNodeCreate):
    nid = scene_repo.create_node(
        payload.scene_id,
        payload.parent_id,
        payload.name,
        payload.node_type,
        payload.transform_json,
        payload.asset_ref_id,
        payload.props_json,
    )
    return {"id": nid}
@router.get("/{scene_id}/nodes", response_model=list[SceneNodeOut])
def list_nodes(scene_id: str):
    return scene_repo.list_nodes(scene_id)
# apps/api/routers/versioning.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter
from apps.api.schemas.versioning import PublishCreate, PublishOut,
VersionCreate, VersionOut
from apps.api.services import publish_repo, versioning_repo
router = APIRouter(prefix="/api/versioning", tags=["versioning"])
@router.post("/versions", response_model=dict)
def create_version(payload: VersionCreate):
    vid = versioning_repo.create_version(payload.project_id, payload.version,
payload.note)
    return {"id": vid}
@router.get("/versions", response_model=list[VersionOut])
def list_versions(project_id: str):
    return versioning_repo.list_versions(project_id)
@router.post("/publish", response_model=dict)
def create_publish(payload: PublishCreate):
    pid = publish_repo.create_publish_record(payload.project_id,
payload.version_id, payload.channel, payload.note, payload.artifact_path)
    return {"id": pid}
@router.get("/publish", response_model=list[PublishOut])
def list_publish(project_id: str):
    return publish_repo.list_publish_records(project_id)
# apps/api/domain/__init__.py
# apps/api/domain/models.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True)
class Department:
    id: str
    name: str
    created_at: datetime
@dataclass(frozen=True)
class Position:
    id: str
    name: str
    dept_id: str
    created_at: datetime
@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    dept_id: str
    title: str
    created_at: datetime
# apps/api/services/__init__.py
# apps/api/services/asset_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import sqlite3
from apps.api.db import db
from apps.api.util import csv_tags, new_id, parse_tags, utc_now
def create_asset(project_id: str, type: str, filename: str, sha256: str,
size: int, tags: list[str], meta_json: str) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO asset(id,project_id,type,filename,sha256,size,tags,
meta_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (aid, project_id, type, filename, sha256, int(size),
csv_tags(tags), meta_json or "{}", utc_now()),
        )
    return aid
def list_assets(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM asset WHERE project_id=? ORDER BY
created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["tags"] = parse_tags(d.get("tags", ""))
            out.append(d)
        return out
def delete_asset(asset_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM asset WHERE id=?", (asset_id,))
        return cur.rowcount > 0
# apps/api/services/audit_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now
def write_audit(actor: str, action: str, target_type: str, target_id: str,
detail: dict) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO audit_log(id,actor,action,target_type,target_id,
detail_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (aid, actor or "system", action, target_type, target_id,
json_dumps(detail or {}), utc_now()),
        )
    return aid
def list_audit(limit: int = 100) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM audit_log ORDER BY created_at
DESC LIMIT ?", (int(limit),)).fetchall()
        return [dict(r) for r in rows]
# apps/api/services/interaction_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from apps.api.db import db
from apps.api.util import new_id, utc_now
def create_interaction(project_id: str, scene_id: str, name: str, enabled:
bool, graph_json: str) -> str:
    iid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO interaction(id,project_id,scene_id,name,enabled,
graph_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (iid, project_id, scene_id, name, 1 if enabled else 0,
graph_json or "{}", utc_now()),
        )
    return iid
def list_interactions(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM interaction WHERE project_id=?
ORDER BY created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["enabled"] = bool(d.get("enabled"))
            out.append(d)
        return out
# apps/api/services/project_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import sqlite3
from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now
def create_project(name: str, target_device: str, constraints_json: str) ->
str:
    pid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO project(id,name,target_device,constraints_json,
status,created_at) VALUES (?,?,?,?,?,?)",
            (pid, name, target_device, constraints_json or "{}", "draft",
utc_now()),
        )
    return pid
def list_projects() -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM project ORDER BY created_at DESC")
.fetchall()
        return [dict(r) for r in rows]
def get_project(project_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT * FROM project WHERE id=?", (project_id,))
.fetchone()
        return dict(row) if row else None
def update_project(project_id: str, patch: dict) -> bool:
    allow = {"name", "target_device", "constraints_json", "status"}
    fields = {k: v for k, v in patch.items() if k in allow and v is not None}
    if not fields:
        return False
    sets = ", ".join([f"{k}=?" for k in fields.keys()])
    values = list(fields.values()) + [project_id]
    with db() as conn:
        cur = conn.execute(f"UPDATE project SET {sets} WHERE id=?", values)
        return cur.rowcount > 0
def delete_project(project_id: str) -> bool:
    with db() as conn:
        cur = conn.execute("DELETE FROM project WHERE id=?", (project_id,))
        return cur.rowcount > 0
# apps/api/services/publish_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from apps.api.db import db
from apps.api.util import new_id, utc_now
def create_publish_record(project_id: str, version_id: str, channel: str,
note: str, artifact_path: str) -> str:
    pid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO publish_record(id,project_id,version_id,channel,
note,artifact_path,created_at) VALUES (?,?,?,?,?,?,?)",
            (pid, project_id, version_id, channel or "local_export", note or
"", artifact_path or "", utc_now()),
        )
    return pid
def list_publish_records(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM publish_record WHERE project_id=?
ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
# apps/api/services/scene_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from apps.api.db import db
from apps.api.util import new_id, utc_now
def create_scene(project_id: str, name: str) -> str:
    sid = new_id()
    with db() as conn:
        conn.execute("INSERT INTO scene(id,project_id,name,created_at)
VALUES (?,?,?,?)", (sid, project_id, name, utc_now()))
    return sid
def list_scenes(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM scene WHERE project_id=? ORDER BY
created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
def create_node(scene_id: str, parent_id: str | None, name: str, node_type:
str, transform_json: str, asset_ref_id: str | None, props_json: str) -> str:
    nid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO scene_node(id,scene_id,parent_id,name,node_type,
transform_json,asset_ref_id,props_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)
",
            (nid, scene_id, parent_id, name, node_type, transform_json or "{}
", asset_ref_id, props_json or "{}", utc_now()),
        )
    return nid
def list_nodes(scene_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM scene_node WHERE scene_id=? ORDER
BY created_at ASC", (scene_id,)).fetchall()
        return [dict(r) for r in rows]
# apps/api/services/store.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import uuid4
class InMemoryStore:
    def __init__(self) -> None:
        self._departments: dict[str, dict[str, Any]] = {}
        self._positions: dict[str, dict[str, Any]] = {}
        self._employees: dict[str, dict[str, Any]] = {}
    def _new_id(self) -> str:
        return uuid4().hex
    def list_departments(self) -> list[dict[str, Any]]:
        return list(self._departments.values())
    def create_department(self, name: str) -> str:
        _id = self._new_id()
        self._departments[_id] = {"id": _id, "name": name, "created_at":
datetime.utcnow().isoformat()}
        return _id
    def delete_department(self, dept_id: str) -> bool:
        return self._departments.pop(dept_id, None) is not None
    def list_positions(self) -> list[dict[str, Any]]:
        return list(self._positions.values())
    def create_position(self, name: str, dept_id: str) -> str:
        _id = self._new_id()
        self._positions[_id] = {"id": _id, "name": name, "dept_id": dept_id,
"created_at": datetime.utcnow().isoformat()}
        return _id
    def delete_position(self, pos_id: str) -> bool:
        return self._positions.pop(pos_id, None) is not None
    def list_employees(self) -> list[dict[str, Any]]:
        return list(self._employees.values())
    def create_employee(self, name: str, dept_id: str, title: str) -> str:
        _id = self._new_id()
        self._employees[_id] = {
            "id": _id,
            "name": name,
            "dept_id": dept_id,
            "title": title,
            "created_at": datetime.utcnow().isoformat(),
        }
        return _id
    def delete_employee(self, emp_id: str) -> bool:
        return self._employees.pop(emp_id, None) is not None
# apps/api/services/versioning_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from apps.api.db import db
from apps.api.util import json_dumps, new_id, utc_now
def _asset_manifest(conn, project_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id,type,filename,sha256,size,tags,meta_json,created_at FROM
asset WHERE project_id=? ORDER BY created_at ASC",
        (project_id,),
    ).fetchall()
    return [dict(r) for r in rows]
def _snapshot(conn, project_id: str) -> dict:
    scenes = conn.execute("SELECT id,name,created_at FROM scene WHERE
project_id=? ORDER BY created_at ASC", (project_id,)).fetchall()
    interactions = conn.execute(
        "SELECT id,scene_id,name,enabled,graph_json,created_at FROM
interaction WHERE project_id=? ORDER BY created_at ASC",
        (project_id,),
    ).fetchall()
    return {
        "scenes": [dict(r) for r in scenes],
        "interactions": [dict(r) for r in interactions],
    }
def create_version(project_id: str, version: str, note: str) -> str:
    vid = new_id()
    with db() as conn:
        manifest = _asset_manifest(conn, project_id)
        snap = _snapshot(conn, project_id)
        conn.execute(
            "INSERT INTO version(id,project_id,version,note,snapshot_json,
asset_manifest_json,created_at) VALUES (?,?,?,?,?,?,?)",
            (vid, project_id, version, note or "", json_dumps(snap),
json_dumps(manifest), utc_now()),
        )
    return vid
def list_versions(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM version WHERE project_id=? ORDER
BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]
# apps/api/schemas/common.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from pydantic import BaseModel, Field
class IdResponse(BaseModel):
    id: str = Field(..., description="资源唯一标识")
# apps/__init__.py
# apps/api/__init__.py
# apps/api/db.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
def resolve_db_path() -> Path:
    base = os.environ.get("APP_DB_DIR", "").strip()
    root = Path(base).resolve() if base else Path.cwd().resolve()
    return root / "data" / "app.db"
def ensure_db_schema(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(
        """
CREATE TABLE IF NOT EXISTS project (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  target_device TEXT NOT NULL,
  constraints_json TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS asset (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  type TEXT NOT NULL,
  filename TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  size INTEGER NOT NULL,
  tags TEXT NOT NULL,
  meta_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_asset_project ON asset(project_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_asset_unique_hash ON asset(project_id,
sha256);
CREATE TABLE IF NOT EXISTS scene (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_scene_project ON scene(project_id);
CREATE TABLE IF NOT EXISTS scene_node (
  id TEXT PRIMARY KEY,
  scene_id TEXT NOT NULL,
  parent_id TEXT,
  name TEXT NOT NULL,
  node_type TEXT NOT NULL,
  transform_json TEXT NOT NULL,
  asset_ref_id TEXT,
  props_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(scene_id) REFERENCES scene(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_node_scene ON scene_node(scene_id);
CREATE TABLE IF NOT EXISTS interaction (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  scene_id TEXT NOT NULL,
  name TEXT NOT NULL,
  enabled INTEGER NOT NULL,
  graph_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
  FOREIGN KEY(scene_id) REFERENCES scene(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_interaction_project ON interaction(project_id)
;
CREATE TABLE IF NOT EXISTS version (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  version TEXT NOT NULL,
  note TEXT NOT NULL,
  snapshot_json TEXT NOT NULL,
  asset_manifest_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_version_unique ON version(project_id,
version);
CREATE TABLE IF NOT EXISTS publish_record (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  version_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  note TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
  FOREIGN KEY(version_id) REFERENCES version(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_publish_project ON publish_record(project_id);
CREATE TABLE IF NOT EXISTS audit_log (
  id TEXT PRIMARY KEY,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  target_type TEXT NOT NULL,
  target_id TEXT NOT NULL,
  detail_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(created_at);
"""
    )
@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    path = resolve_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    ensure_db_schema(conn)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
# apps/api/schemas/__init__.py
# apps/api/schemas/asset.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from pydantic import BaseModel, Field
class AssetCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    type: str = Field(..., min_length=2, max_length=20)
    filename: str = Field(..., min_length=1, max_length=160)
    sha256: str = Field(..., min_length=16, max_length=80)
    size: int = Field(..., ge=0, le=2_000_000_000)
    tags: list[str] = Field(default_factory=list)
    meta_json: str = Field("{}", max_length=8000)
class AssetOut(BaseModel):
    id: str
    project_id: str
    type: str
    filename: str
    sha256: str
    size: int
    tags: list[str]
    meta_json: str
    created_at: str
# apps/api/schemas/interaction.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from pydantic import BaseModel, Field
class InteractionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    scene_id: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=80)
    enabled: bool = Field(True)
    graph_json: str = Field("{}", max_length=20000)
class InteractionOut(BaseModel):
    id: str
    project_id: str
    scene_id: str
    name: str
    enabled: bool
    graph_json: str
    created_at: str
# apps/api/schemas/project.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from pydantic import BaseModel, Field
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80, description=
"项目名称")
    target_device: str = Field(..., min_length=2, max_length=30, description=
"目标设备")
    constraints_json: str = Field("{}", max_length=4000, description=
"性能/规格约束 JSON")
class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=80)
    target_device: str | None = Field(None, min_length=2, max_length=30)
    constraints_json: str | None = Field(None, max_length=4000)
    status: str | None = Field(None, max_length=30)
class ProjectOut(BaseModel):
    id: str
    name: str
    target_device: str
    constraints_json: str
    status: str
    created_at: str
# apps/api/schemas/scene.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from pydantic import BaseModel, Field
class SceneCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    name: str = Field(..., min_length=2, max_length=80)
class SceneOut(BaseModel):
    id: str
    project_id: str
    name: str
    created_at: str
class SceneNodeCreate(BaseModel):
    scene_id: str = Field(..., min_length=8, max_length=64)
    parent_id: str | None = Field(None, max_length=64)
    name: str = Field(..., min_length=1, max_length=80)
    node_type: str = Field(..., min_length=2, max_length=30)
    transform_json: str = Field("{}", max_length=4000)
    asset_ref_id: str | None = Field(None, max_length=64)
    props_json: str = Field("{}", max_length=8000)
class SceneNodeOut(BaseModel):
    id: str
    scene_id: str
    parent_id: str | None
    name: str
    node_type: str
    transform_json: str
    asset_ref_id: str | None
    props_json: str
    created_at: str
# apps/api/schemas/versioning.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from pydantic import BaseModel, Field
class VersionCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    version: str = Field(..., min_length=2, max_length=20, description=
"版本号，如 V1.0.0")
    note: str = Field("", max_length=1000)
class VersionOut(BaseModel):
    id: str
    project_id: str
    version: str
    note: str
    snapshot_json: str
    asset_manifest_json: str
    created_at: str
class PublishCreate(BaseModel):
    project_id: str = Field(..., min_length=8, max_length=64)
    version_id: str = Field(..., min_length=8, max_length=64)
    channel: str = Field("local_export", max_length=40)
    note: str = Field("", max_length=1000)
    artifact_path: str = Field("", max_length=300)
class PublishOut(BaseModel):
    id: str
    project_id: str
    version_id: str
    channel: str
    note: str
    artifact_path: str
    created_at: str
# apps/api/tests/__init__.py
# -*- coding: utf-8 -*-
# apps/api/tests/test_health.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import unittest
from fastapi.testclient import TestClient
from apps.api.main import create_app
class HealthEndpointTests(unittest.TestCase):
    def test_health_ok(self) -> None:
        client = TestClient(create_app())
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get("status"), "ok")
if __name__ == "__main__":
    unittest.main()
# apps/api/util.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4
def new_id() -> str:
    return uuid4().hex
def utc_now() -> str:
    return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()
def json_dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()
def csv_tags(tags: list[str]) -> str:
    clean = []
    for t in tags:
        t = (t or "").strip()
        if not t:
            continue
        if "," in t:
            t = t.replace(",", " ")
        clean.append(t)
    # de-dup, keep order
    seen = set()
    out = []
    for t in clean:
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return ",".join(out)
def parse_tags(tags_csv: str) -> list[str]:
    items = []
    for t in (tags_csv or "").split(","):
        t = t.strip()
        if t:
            items.append(t)
    return items
# apps/web/admin.html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
content="width=device-width, initial-scale=1" />
<title>管理端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>管理端</h1>
<ul>
  <li>核心动作按钮口径：新增 / 编辑 / 查看 / 删除</li>
</ul>
</body></html>
# apps/web/index.html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>VR多模态交互媒介内容创作与发布系统</title>
  </head>
  <body>
    <h1>VR多模态交互媒介内容创作与发布系统</h1>
    <ul>
      <li><a href="./teacher.html">业务专员端</a></li>
      <li><a href="./student.html">员工端</a></li>
      <li><a href="./admin.html">管理员端</a></li>
    </ul>
  </body>
</html>
# apps/web/student.html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
content="width=device-width, initial-scale=1" />
<title>学生端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>学生端</h1>
<ul>
  <li>当前版本：V1.0（示例）</li>
  <li>体验说明：按交互节点顺序体验并记录问题</li>
  <li>反馈方式：提交问题编号与截图（后续版本接入反馈单）</li>
</ul>
</body></html>
# apps/web/teacher.html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport"
content="width=device-width, initial-scale=1" />
<title>教师端 - VR多模态交互媒介内容创作与发布系统</title></head><body>
<h1>教师端</h1>
<ol>
  <li>查看项目概览与关键指标（资源数、场景数、交互数、最近发布）。</li>
  <li>对比两个版本的变更摘要（资源替换、交互规则变更）。</li>
  <li>导出发布说明与清单，用于验收留痕。</li>
</ol>
</body></html>
# apps/api/main.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import os
try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
from apps.api.routers import (
    asset_router,
    audit_router,
    hr_router,
    interaction_router,
    project_router,
    scene_router,
    versioning_router,
)
def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies
before running the API.")
    app = FastAPI(title="API")
    app.include_router(hr_router)
    app.include_router(project_router)
    app.include_router(asset_router)
    app.include_router(scene_router)
    app.include_router(interaction_router)
    app.include_router(versioning_router)
    app.include_router(audit_router)
    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VR多模态交互媒介内容创作与发布系统</title>
  <style>
    :root { --bg:#0b1020; --panel:#121a33; --text:#e8ecff; --muted:#aab3d9; -
-accent:#6ee7ff; --danger:#ff5b6e; }
    body { margin:0; font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
background:linear-gradient(180deg,#070a14, var(--bg)); color:var(--text); }
    header { display:flex; align-items:center; justify-content:space-between;
padding:14px 18px; background:rgba(18,26,51,.8); border-bottom:1px solid
rgba(110,231,255,.18); position:sticky; top:0; backdrop-filter: blur(8px); }
    header .brand { font-weight:700; letter-spacing:.5px; }
    header .badge { font-size:12px; padding:4px 10px; border:1px solid
rgba(110,231,255,.35); border-radius:999px; color:var(--accent); }
    main { max-width:1180px; margin:18px auto; padding:0 18px 28px;
display:grid; grid-template-columns: 260px 1fr; gap:16px; }
    nav { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:12px; }
    nav a { display:block; color:var(--muted); text-decoration:none;
padding:10px 10px; border-radius:10px; }
    nav a:hover { background:rgba(110,231,255,.08); color:var(--text); }
    .panel { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,
.12); border-radius:14px; padding:14px; }
    .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
    .card { border:1px solid rgba(110,231,255,.12); border-radius:12px;
padding:12px; background:rgba(9,12,24,.55); }
    .card h3 { margin:0 0 8px; font-size:14px; color:var(--accent); }
    .hint { color:var(--muted); font-size:12px; line-height:1.6; }
    .toolbar { display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 6px; }
    button { cursor:pointer; border-radius:10px; border:1px solid rgba(110,
231,255,.22); background:rgba(110,231,255,.10); color:var(--text);
padding:8px 12px; }
    button:hover { background:rgba(110,231,255,.16); }
    button.danger { border-color:rgba(255,91,110,.35); background:rgba(255,
91,110,.12); }
    .k { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas,
monospace; color:var(--accent); }
    .hidden { display:none !important; }
    #loginBox { max-width:520px; margin:10vh auto; padding:18px; }
    #loginBox .row { display:grid; gap:10px; margin-top:10px; }
    input { padding:10px 12px; border-radius:10px; border:1px solid rgba(110,
231,255,.18); background:rgba(255,255,255,.05); color:var(--text); }
    .row label { color:var(--muted); font-size:12px; }
    .row small { color:var(--muted); }
    #modal.modal-shell.modal { position:fixed; inset:0; background:rgba(0,0,
0,.55); display:flex; align-items:center; justify-content:center; }
    #modal .dialog { width:min(680px, 92vw); border-radius:14px;
background:rgba(18,26,51,.96); border:1px solid rgba(110,231,255,.18);
padding:14px; box-shadow:0 24px 80px rgba(0,0,0,.45); }
    #modal .dialog header { position:static; border:none;
background:transparent; padding:0 0 10px; }
    #modal .dialog .title { font-weight:700; }
    #modal .dialog .content { color:var(--muted); line-height:1.7; font-
size:13px; }
  </style>
</head>
<body>
  <div id="loginView">
    <div id="loginBox" class="panel">
      <h1 style="margin:0 0 8px; font-size:18px;
">VR多模态交互媒介内容创作与发布系统</h1>
      <div class="hint">V1.0 演示环境：用于截图与材料生成的最小可运行界面。<
/div>
      <form id="login-form" class="row" onsubmit="return
window.__app.login(event)">
        <label>用户名 <input name="username" value="admin" autocomplete=
"username" /></label>
        <label>密码 <input name="password" type="password" value="admin123"
autocomplete="current-password" /></label>
        <button type="submit">登录</button>
        <small>提示：输入任意值均可登录（用于演示与截图）。</small>
      </form>
    </div>
  </div>
  <div id="appView" class="hidden">
    <header>
      <div class="badge">V1.0</div>
    </header>
    <main>
      <nav>
        <a href="/#home">首页</a>
        <a href="/#zones">资源分区</a>
        <a href="/#stations">工作台（Stations）</a>
        <a href="/#inspections">交互检查</a>
        <a href="/#alerts">风险提醒</a>
        <a href="/#irrigation">发布流水</a>
        <a href="/#reports">统计报表</a>
      </nav>
      <section class="panel">
        <div id="pageTitle" style="font-weight:700; margin-bottom:10px;
">首页</div>
        <div id="pageBody"></div>
      </section>
    </main>
  </div>
  <div id="modal" class="modal-shell modal hidden">
    <div class="dialog" role="dialog" aria-modal="true">
      <header>
        <div class="title" id="modalTitle">操作</div>
        <button class="danger" onclick="window.__rkModal.closeModal()
">关闭</button>
      </header>
      <div class="content" id="modalContent"></div>
    </div>
  </div>
  <script>
    window.__rkModal = {
      closeModal() {
        document.getElementById('modal').classList.add('hidden');
      },
      openModal(title, content) {
        document.getElementById('modalTitle').textContent = title;
        document.getElementById('modalContent').textContent = content;
        document.getElementById('modal').classList.remove('hidden');
      }
    };
    function renderHome() {
      document.getElementById('pageTitle').textContent = '首页';
      document.getElementById('pageBody').innerHTML = `
        <div class="grid">
          <div class="card"><h3>项目概览</h3><div class=
"hint">资源、场景、交互与发布记录在此汇总展示。</div></div>
        </div>`;
    }
    function renderSimplePage(title, id) {
      document.getElementById('pageTitle').textContent = title;
      const body = document.getElementById('pageBody');
      body.innerHTML = `<div id="${id}" class="card">
        <h3>${title}</h3>
      </div>`;
    }
    function renderStations() {
      document.getElementById('pageTitle').textContent =
'工作台（Stations）';
      const body = document.getElementById('pageBody');
      body.innerHTML = `
        <div id="stations" class="card">
          <h3>Stations 列表</h3>
          <div class="hint">用于演示“新增/编辑/查看/删除”弹窗操作按钮文案。<
/div>
          <div class="toolbar">
            <button onclick="window.__rkModal.openModal('新增',
'创建新的条目并填写字段。')">新增</button>
            <button onclick="window.__rkModal.openModal('编辑',
'修改条目名称、标签与说明。')">编辑</button>
            <button onclick="window.__rkModal.openModal('查看',
'查看条目详情与引用关系。')">查看</button>
            <button class="danger" onclick="window.__rkModal.openModal('删除
', '删除条目前请确认无引用并记录审计。')">删除</button>
          </div>
          <div class="hint">提示：截图脚本会自动点击以上按钮并截取弹窗状态。
</div>
        </div>`;
    }
    function route() {
      const hash = (location.hash || '#home').replace(/^#/, '');
      if (hash === 'home' || hash === '') return renderHome();
      if (hash === 'stations') return renderStations();
      if (hash === 'zones') return renderSimplePage('资源分区', 'zones');
      if (hash === 'inspections') return renderSimplePage('交互检查',
'inspections');
      if (hash === 'alerts') return renderSimplePage('风险提醒', 'alerts');
      if (hash === 'irrigation') return renderSimplePage('发布流水',
'irrigation');
      if (hash === 'reports') return renderSimplePage('统计报表', 'reports');
      return renderSimplePage('页面', hash);
    }
    window.__app = {
      login(e) {
        e.preventDefault();
        localStorage.setItem('__demo_logged_in', '1');
        document.getElementById('loginView').classList.add('hidden');
        document.getElementById('appView').classList.remove('hidden');
        route();
        return false;
      }
    };
    window.addEventListener('hashchange', () => route());
    if (localStorage.getItem('__demo_logged_in') === '1') {
      document.getElementById('loginView').classList.add('hidden');
      document.getElementById('appView').classList.remove('hidden');
      route();
    }
  </script>
</body>
</html>"""
    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}
    return app
app = create_app()
def _main() -> None:
    import uvicorn
    port = int(os.environ.get("APP_PORT", "8010"))
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level=
"warning")
if __name__ == "__main__":
    _main()
# apps/api/routers/__init__.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from .hr import router as hr_router
from .project import router as project_router
from .asset import router as asset_router
from .scene import router as scene_router
from .interaction import router as interaction_router
from .versioning import router as versioning_router
from .audit import router as audit_router
__all__ = [
    "hr_router",
    "project_router",
    "asset_router",
    "scene_router",
    "interaction_router",
    "versioning_router",
    "audit_router",
]
# apps/api/routers/asset.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from apps.api.schemas.asset import AssetCreate, AssetOut
from apps.api.services import asset_repo
router = APIRouter(prefix="/api/assets", tags=["assets"])
@router.get("", response_model=list[AssetOut])
def list_assets(project_id: str):
    return asset_repo.list_assets(project_id)
@router.post("", response_model=dict)
def create_asset(payload: AssetCreate):
    aid = asset_repo.create_asset(
        payload.project_id,
        payload.type,
        payload.filename,
        payload.sha256,
        payload.size,
        payload.tags,
        payload.meta_json,
    )
    return {"id": aid}
@router.delete("/{asset_id}", response_model=dict)
def delete_asset(asset_id: str):
    ok = asset_repo.delete_asset(asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/audit.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter
from apps.api.services import audit_repo
router = APIRouter(prefix="/api/audit", tags=["audit"])
@router.get("", response_model=list[dict])
def list_audit(limit: int = 100):
    return audit_repo.list_audit(limit=limit)
# apps/api/routers/hr.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from apps.api.services.store import InMemoryStore
router = APIRouter(prefix="/api/hr", tags=["hr"])
class DepartmentIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
class PositionIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
class EmployeeIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept_id: str
    title: str = Field(..., min_length=1, max_length=50)
def get_store() -> InMemoryStore:
    # module-level singleton to keep the example minimal.
    global _STORE
    try:
        return _STORE
    except NameError:
        _STORE = InMemoryStore()
        return _STORE
@router.get("/departments")
def list_departments() -> list[dict]:
    return get_store().list_departments()
@router.post("/departments")
def create_department(payload: DepartmentIn) -> dict:
    _id = get_store().create_department(payload.name)
    return {"id": _id}
@router.delete("/departments/{dept_id}")
def delete_department(dept_id: str) -> dict:
    ok = get_store().delete_department(dept_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
@router.get("/positions")
def list_positions() -> list[dict]:
    return get_store().list_positions()
@router.post("/positions")
def create_position(payload: PositionIn) -> dict:
    _id = get_store().create_position(payload.name, payload.dept_id)
    return {"id": _id}
@router.delete("/positions/{pos_id}")
def delete_position(pos_id: str) -> dict:
    ok = get_store().delete_position(pos_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
@router.get("/employees")
def list_employees() -> list[dict]:
    return get_store().list_employees()
@router.post("/employees")
def create_employee(payload: EmployeeIn) -> dict:
    _id = get_store().create_employee(payload.name, payload.dept_id,
payload.title)
    return {"id": _id}
@router.delete("/employees/{emp_id}")
def delete_employee(emp_id: str) -> dict:
    ok = get_store().delete_employee(emp_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/interaction.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter
from apps.api.schemas.interaction import InteractionCreate, InteractionOut
from apps.api.services import interaction_repo
router = APIRouter(prefix="/api/interactions", tags=["interactions"])
@router.post("", response_model=dict)
def create_interaction(payload: InteractionCreate):
    iid = interaction_repo.create_interaction(payload.project_id,
payload.scene_id, payload.name, payload.enabled, payload.graph_json)
    return {"id": iid}
@router.get("", response_model=list[InteractionOut])
def list_interactions(project_id: str):
    return interaction_repo.list_interactions(project_id)
# apps/api/routers/project.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from apps.api.schemas.project import ProjectCreate, ProjectOut,
ProjectUpdate
from apps.api.services import project_repo
router = APIRouter(prefix="/api/projects", tags=["projects"])
@router.get("", response_model=list[ProjectOut])
def list_projects():
    return project_repo.list_projects()
@router.post("", response_model=dict)
def create_project(payload: ProjectCreate):
    pid = project_repo.create_project(payload.name, payload.target_device,
payload.constraints_json)
    return {"id": pid}
@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str):
    p = project_repo.get_project(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="not found")
    return p
@router.patch("/{project_id}", response_model=dict)
def patch_project(project_id: str, payload: ProjectUpdate):
    ok = project_repo.update_project(project_id, payload.model_dump())
    if not ok:
        raise HTTPException(status_code=404, detail="not found or no
changes")
    return {"updated": True}
@router.delete("/{project_id}", response_model=dict)
def delete_project(project_id: str):
    ok = project_repo.delete_project(project_id)
    if not ok:
        raise HTTPException(status_code=404, detail="not found")
    return {"deleted": True}
# apps/api/routers/publish.py
# apps/api/routers/scene.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from apps.api.schemas.scene import SceneCreate, SceneNodeCreate,
SceneNodeOut, SceneOut
from apps.api.services import scene_repo
router = APIRouter(prefix="/api/scenes", tags=["scenes"])
@router.post("", response_model=dict)
def create_scene(payload: SceneCreate):
    sid = scene_repo.create_scene(payload.project_id, payload.name)
    return {"id": sid}
@router.get("", response_model=list[SceneOut])
def list_scenes(project_id: str):
    return scene_repo.list_scenes(project_id)
@router.post("/nodes", response_model=dict)
def create_node(payload: SceneNodeCreate):
    nid = scene_repo.create_node(
        payload.scene_id,
        payload.parent_id,
        payload.name,
        payload.node_type,
        payload.transform_json,
        payload.asset_ref_id,
        payload.props_json,
    )
    return {"id": nid}
@router.get("/{scene_id}/nodes", response_model=list[SceneNodeOut])
def list_nodes(scene_id: str):
    return scene_repo.list_nodes(scene_id)
# apps/api/routers/versioning.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from fastapi import APIRouter
from apps.api.schemas.versioning import PublishCreate, PublishOut,
VersionCreate, VersionOut
from apps.api.services import publish_repo, versioning_repo
router = APIRouter(prefix="/api/versioning", tags=["versioning"])
@router.post("/versions", response_model=dict)
def create_version(payload: VersionCreate):
    vid = versioning_repo.create_version(payload.project_id, payload.version,
payload.note)
    return {"id": vid}
@router.get("/versions", response_model=list[VersionOut])
def list_versions(project_id: str):
    return versioning_repo.list_versions(project_id)
@router.post("/publish", response_model=dict)
def create_publish(payload: PublishCreate):
    pid = publish_repo.create_publish_record(payload.project_id,
payload.version_id, payload.channel, payload.note, payload.artifact_path)
    return {"id": pid}
@router.get("/publish", response_model=list[PublishOut])
def list_publish(project_id: str):
    return publish_repo.list_publish_records(project_id)
# apps/api/domain/__init__.py
# apps/api/domain/models.py
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
@dataclass(frozen=True)
class Department:
    id: str
    name: str
    created_at: datetime
@dataclass(frozen=True)
class Position:
    id: str
    name: str
    dept_id: str
    created_at: datetime
@dataclass(frozen=True)
class Employee:
    id: str
    name: str
    dept_id: str
    title: str
    created_at: datetime
# apps/api/services/__init__.py
# apps/api/services/asset_repo.py
# -*- coding: utf-8 -*-
from __future__ import annotations
import sqlite3
from apps.api.db import db
from apps.api.util import csv_tags, new_id, parse_tags, utc_now
def create_asset(project_id: str, type: str, filename: str, sha256: str,
size: int, tags: list[str], meta_json: str) -> str:
    aid = new_id()
    with db() as conn:
        conn.execute(
            "INSERT INTO asset(id,project_id,type,filename,sha256,size,tags,
meta_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (aid, project_id, type, filename, sha256, int(size),
csv_tags(tags), meta_json or "{}", utc_now()),
        )
    return aid
def list_assets(project_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM asset WHERE project_id=? ORDER BY
created_at DESC", (project_id,)).fetchall()
        out = []
        for r in rows: