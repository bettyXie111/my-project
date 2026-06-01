# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path


def ensure_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_index_html(app_name: str) -> str:
    safe = app_name.replace("<", " ").replace(">", " ").strip()
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe}</title>
  <style>
    :root{{--bg:#0b1020;--panel:#111a35;--text:#e9eeff;--muted:#a7b2da;--accent:#63f2d2;--danger:#ff5b6e;}}
    body{{margin:0;font-family:Segoe UI,Microsoft YaHei,sans-serif;background:linear-gradient(180deg,#070a14,var(--bg));color:var(--text);}}
    header{{position:sticky;top:0;backdrop-filter:blur(10px);background:rgba(17,26,53,.78);border-bottom:1px solid rgba(99,242,210,.18);padding:14px 18px;display:flex;align-items:center;justify-content:space-between;gap:12px;}}
    header .brand{{font-weight:800;letter-spacing:.5px;}}
    header .badge{{font-size:12px;color:var(--accent);border:1px solid rgba(99,242,210,.35);padding:4px 10px;border-radius:999px;}}
    main{{max-width:1180px;margin:18px auto;padding:0 18px 28px;display:grid;grid-template-columns:260px 1fr;gap:16px;}}
    nav{{background:rgba(17,26,53,.72);border:1px solid rgba(99,242,210,.12);border-radius:14px;padding:12px;}}
    nav a{{display:block;color:var(--muted);text-decoration:none;padding:10px 10px;border-radius:10px;}}
    nav a:hover{{background:rgba(99,242,210,.08);color:var(--text);}}
    .panel{{background:rgba(17,26,53,.72);border:1px solid rgba(99,242,210,.12);border-radius:14px;padding:14px;}}
    .k{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--accent);}}
    .hidden{{display:none !important;}}
    .grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;}}
    .card{{background:rgba(9,12,24,.55);border:1px solid rgba(99,242,210,.12);border-radius:12px;padding:12px;}}
    .card h3{{margin:0 0 8px;font-size:14px;color:var(--accent);}}
    .hint{{color:var(--muted);font-size:12px;line-height:1.6;}}
    .row{{display:grid;gap:10px;margin-top:10px;}}
    input{{padding:10px 12px;border-radius:10px;border:1px solid rgba(99,242,210,.18);background:rgba(255,255,255,.05);color:var(--text);}}
    button{{cursor:pointer;border-radius:10px;border:1px solid rgba(99,242,210,.22);background:rgba(99,242,210,.10);color:var(--text);padding:8px 12px;}}
    button:hover{{background:rgba(99,242,210,.16);}}
    button.danger{{border-color:rgba(255,91,110,.35);background:rgba(255,91,110,.12);}}
    #modal{{position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;}}
    #modal .dialog{{width:min(720px,92vw);background:rgba(17,26,53,.96);border:1px solid rgba(99,242,210,.18);border-radius:14px;box-shadow:0 24px 80px rgba(0,0,0,.45);padding:14px;}}
    #modal header{{position:static;border:none;background:transparent;padding:0 0 10px;}}
    #modal .title{{font-weight:800;}}
  </style>
</head>
<body>
  <div id="loginView">
    <div style="max-width:520px;margin:10vh auto;padding:18px" class="panel">
      <h1 style="margin:0 0 8px;font-size:18px;">{safe}</h1>
      <div class="hint">V1.0 演示环境：用于截图与材料生成的最小可运行界面。</div>
      <form id="login-form" class="row">
        <label class="hint">用户名 <input name="username" value="admin" autocomplete="username" /></label>
        <label class="hint">密码 <input name="password" type="password" value="admin123" autocomplete="current-password" /></label>
        <button type="submit">登录</button>
        <div class="hint">提示：任意账号可登录（用于演示与截图）。</div>
      </form>
    </div>
  </div>
  <div id="appView" style="display:none;">
    <header>
      <div class="brand">{safe} 控制台</div>
      <div class="badge">V1.0</div>
    </header>
    <main>
      <nav>
        <a href="#home">首页</a>
        <a href="#samples">样本管理</a>
        <a href="#catalog">基础资料</a>
        <a href="#workflow">流程配置</a>
        <a href="#alerts">预警中心</a>
        <a href="#reports">统计报表</a>
        <a href="#audit">审计留痕</a>
      </nav>
      <section class="panel">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
          <h2 id="pageTitle" style="margin:0;font-size:16px;">首页</h2>
          <div class="hint">API：<span class="k" id="apiStatus">未检测</span></div>
        </div>
        <div id="pageBody" style="margin-top:10px;"></div>
      </section>
    </main>
  </div>
  <div id="modal" class="modal-shell modal hidden">
    <div class="dialog" role="dialog" aria-modal="true">
      <header>
        <div class="title" id="modalTitle">操作</div>
        <button class="danger" id="modalClose">关闭</button>
      </header>
      <div class="hint" id="modalContent"></div>
    </div>
  </div>
  <script>
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modalTitle');
    const modalContent = document.getElementById('modalContent');
    function closeModal(){{ modal.classList.add('hidden'); }}
    function openModal(title, content){{ modalTitle.textContent=title; modalContent.textContent=content; modal.classList.remove('hidden'); }}
    document.getElementById('modalClose').onclick = closeModal;
    window.__rkModal = {{ closeModal, openModal }};
    async function apiGet(p){{ const r=await fetch(p); if(!r.ok) throw new Error('HTTP '+r.status); return await r.json(); }}
    function setStatus(ok){{ document.getElementById('apiStatus').textContent = ok ? 'OK' : 'FAIL'; }}
    async function ping(){{ try{{ await apiGet('/api/health'); setStatus(true); }} catch(e){{ setStatus(false); }} }}
    function renderHome(){{
      document.getElementById('pageTitle').textContent='首页';
      document.getElementById('pageBody').innerHTML = `
        <div class='grid'>
          <div class='card'><h3>今日目标</h3><div class='hint'>聚焦条目接收、处理排队与结果确认。</div></div>
          <div class='card'><h3>在线监测</h3><div class='hint'>条目状态、处理进度与提醒结果实时可见。</div></div>
          <div class='card'><h3>闭环留痕</h3><div class='hint'>受理、复核、提醒与处置动作自动记录。</div></div>
        </div>`;
    }}
    function renderSimple(title, id){{
      document.getElementById('pageTitle').textContent=title;
      const descMap = {{
        samples: '登记样本来源、编号与结果状态，支持筛选和检索。',
        catalog: '维护基础资料，支持筛选、排序与检索。',
        workflow: '配置流转节点与处理顺序。',
        alerts: '对异常波动与数据缺失给出提醒，并引导处置闭环。',
        reports: '输出处理结果与留痕报表，支持导出。',
        audit: '记录新增、编辑、查看、删除等关键操作。'
      }};
      const desc = descMap[id] || '该模块用于展示业务信息与形成材料截图。';
      document.getElementById('pageBody').innerHTML = `<div id='${{id}}' class='card'><h3>${{title}}</h3><div class='hint'>${{desc}}</div><div class='hint'>模块标识：<span class='k'>#${{id}}</span></div></div>`;
    }}
    function renderStations(){{
      document.getElementById('pageTitle').textContent = '任务管理';
      document.getElementById('pageBody').innerHTML = `
        <div id="stations" class="card">
          <h3>任务管理列表</h3>
          <div class="hint">用于演示“新增/编辑/查看/删除”弹窗操作按钮文案。</div>
          <div class="toolbar">
            <button onclick="window.__rkModal.openModal('新增','创建新的任务并填写字段。')">新增</button>
            <button onclick="window.__rkModal.openModal('编辑','修改任务参数与时限。')">编辑</button>
            <button onclick="window.__rkModal.openModal('查看','查看任务详情与引用关系。')">查看</button>
            <button class="danger" onclick="window.__rkModal.openModal('删除','删除条目前请确认无引用并记录审计。')">删除</button>
          </div>
          <div class="hint">提示：请按业务流程依次执行新增、编辑、查看、删除，并复核弹窗信息完整性。</div>
        </div>`;
    }}
    function route(){{
      const hash=(location.hash||'#home').replace(/^#/, '');
      if(hash==='home'||hash==='') return renderHome();
      if(hash==='samples') return renderSimple('样本管理','samples');
      if(hash==='catalog') return renderSimple('基础资料','catalog');
      if(hash==='stations') return renderStations();
      if(hash==='workflow') return renderSimple('流程配置','workflow');
      if(hash==='alerts') return renderSimple('预警中心','alerts');
      if(hash==='reports') return renderSimple('统计报表','reports');
      if(hash==='audit') return renderSimple('审计留痕','audit');
      return renderSimple('页面', hash);
    }}
    document.getElementById('login-form').addEventListener('submit', (e)=>{{
      e.preventDefault();
      localStorage.setItem('__demo_logged_in','1');
      document.getElementById('loginView').style.display='none';
      document.getElementById('appView').style.display='block';
      ping(); route();
    }});
    window.addEventListener('hashchange', ()=>route());
    if(localStorage.getItem('__demo_logged_in')==='1'){{
      document.getElementById('loginView').style.display='none';
      document.getElementById('appView').style.display='block';
      ping(); route();
    }} else {{ renderHome(); }}
  </script>
</body>
</html>
"""


def make_auto_catalog(app_name: str) -> str:
    lines = [
        "# -*- coding: utf-8 -*-",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "from datetime import datetime, timezone",
        "from typing import Iterable",
        "",
        f"APP_SLUG = {app_name!r}",
        f"APP_NAME = {app_name!r}",
        "CATALOG_VERSION = 'V1.0'",
        "",
        "@dataclass(frozen=True)",
        "class CatalogItem:",
        "    code: str",
        "    title: str",
        "    desc: str",
        "    created_at: str",
        "",
        "def now_iso() -> str:",
        "    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')",
        "",
        "def iter_samples() -> Iterable[CatalogItem]:",
        "    t = now_iso()",
    ]
    for i in range(1, 1201):
        code = f"{app_name.upper()}_{i:04d}"
        lines.append(f"    yield CatalogItem({code!r}, '样本记录-{i:04d}', '检测样本，覆盖接收、检测、复核、预警与审计留痕。', t)")
    lines += [
        "",
        "def as_dict_list(limit: int = 50) -> list[dict[str, str]]:",
        "    out: list[dict[str, str]] = []",
        "    for idx, it in enumerate(iter_samples()):",
        "        if idx >= limit:",
        "            break",
        "        out.append({'code': it.code, 'title': it.title, 'desc': it.desc, 'created_at': it.created_at})",
        "    return out",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a stable, testable web system (generic FastAPI + static web).")
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--requirement-name", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    app_name = args.requirement_name.strip()
    force = bool(args.force)
    write = write_file if force else ensure_file

    for relative in [
        "apps/__init__.py",
        "apps/api/__init__.py",
        "apps/api/routers/__init__.py",
        "apps/api/services/__init__.py",
        "apps/api/domain/__init__.py",
        "apps/api/schemas/__init__.py",
        "apps/api/tests/__init__.py",
        "apps/web/.keep",
        "scripts/__init__.py",
    ]:
        ensure_file(project_dir / relative, "\n")

    write(project_dir / "apps" / "api" / "domain" / "enums.py", """# -*- coding: utf-8 -*-
from __future__ import annotations

from enum import Enum


class DetectionMode(str, Enum):
    rapid = "rapid"
    routine = "routine"


class AlertLevel(str, Enum):
    info = "info"
    warn = "warn"
    critical = "critical"
""")

    write(project_dir / "apps" / "api" / "schemas" / "sample.py", """# -*- coding: utf-8 -*-
from __future__ import annotations

from pydantic import BaseModel, Field


class SampleCreate(BaseModel):
    sample_code: str = Field(..., description="样本编号")
    owner: str = Field(..., description="归属方")
    category_count: int = Field(..., ge=1, le=400, description="分类数量")
    review_rounds: int = Field(..., ge=1, le=40, description="复核轮次")
    quantity: float = Field(..., gt=0, description="数量")


class SampleView(BaseModel):
    sample_id: str
    sample_code: str
    owner: str
    category_count: int
    review_rounds: int
    quantity: float
    created_at: str
""")

    write(project_dir / "apps" / "api" / "services" / "store.py", '''# -*- coding: utf-8 -*-
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


def utc_now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@dataclass(frozen=True)
class ItemRow:
    sample_id: str
    sample_code: str
    owner: str
    category_count: int
    review_rounds: int
    quantity: float
    created_at: str


class Store:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(self.db_path))
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                create table if not exists samples(
                  sample_id text primary key,
                  sample_code text not null,
                  owner text not null,
                  category_count integer not null,
                  review_rounds integer not null,
                  quantity real not null,
                  created_at text not null
                );
                """
            )
            con.commit()

    def seed_demo(self) -> None:
        if self.list_samples():
            return
        self.create_sample(sample_id="SMP-0001", sample_code="S-0001", owner="示例单位", category_count=12, review_rounds=1, quantity=280.0)
        self.create_sample(sample_id="SMP-0002", sample_code="S-0002", owner="示例单位", category_count=12, review_rounds=1, quantity=180.0)

    def create_sample(self, *, sample_id: str, sample_code: str, owner: str, category_count: int, review_rounds: int, quantity: float) -> None:
        with self._connect() as con:
            con.execute(
                """
                insert into samples(sample_id, sample_code, owner, category_count, review_rounds, quantity, created_at)
                values(?,?,?,?,?,?,?)
                """,
                (sample_id, sample_code, owner, int(category_count), int(review_rounds), float(quantity), utc_now()),
            )
            con.commit()

    def list_samples(self) -> list[ItemRow]:
        with self._connect() as con:
            cur = con.execute(
                """
                select sample_id, sample_code, owner, category_count, review_rounds, quantity, created_at
                from samples order by created_at desc
                """
            )
            return [
                ItemRow(
                    sample_id=r["sample_id"],
                    sample_code=r["sample_code"],
                    owner=r["owner"],
                    category_count=int(r["category_count"]),
                    review_rounds=int(r["review_rounds"]),
                    quantity=float(r["quantity"]),
                    created_at=str(r["created_at"]),
                )
                for r in cur.fetchall()
            ]
''')

    write(project_dir / "apps" / "api" / "routers" / "health.py", """# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
""")

    write(project_dir / "apps" / "api" / "routers" / "samples.py", """# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends

from apps.api.schemas.sample import SampleCreate, SampleView
from apps.api.services.store import Store

router = APIRouter(prefix="/api", tags=["samples"])


def get_store() -> Store:
    app_db_path = Path(__file__).resolve().parents[3] / "data" / "app.db"
    return Store(db_path=app_db_path)


@router.get("/samples", response_model=list[SampleView])
def list_samples(store: Store = Depends(get_store)) -> list[SampleView]:
    store.seed_demo()
    rows = store.list_samples()
    return [
        SampleView(
            sample_id=r.sample_id,
            sample_code=r.sample_code,
            owner=r.owner,
            category_count=r.category_count,
            review_rounds=r.review_rounds,
            quantity=r.quantity,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/samples", response_model=dict[str, str])
def create_sample(dto: SampleCreate, store: Store = Depends(get_store)) -> dict[str, str]:
    sample_id = f"SMP-{uuid.uuid4().hex[:8].upper()}"
    store.create_sample(
        sample_id=sample_id,
        sample_code=dto.sample_code,
        owner=dto.owner,
        category_count=dto.category_count,
        review_rounds=dto.review_rounds,
        quantity=dto.quantity,
    )
    return {"sample_id": sample_id}
""")

    write(project_dir / "apps" / "api" / "routers" / "__init__.py", """# -*- coding: utf-8 -*-
from __future__ import annotations

from .health import router as health_router
from .samples import router as sample_router

__all__ = ["health_router", "sample_router"]
""")

    write(project_dir / "apps" / "api" / "main.py", f"""# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from apps.api.routers import health_router, sample_router
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore[assignment]
    health_router = None  # type: ignore[assignment]
    sample_router = None  # type: ignore[assignment]

APP_NAME = {app_name!r}


def create_app() -> "FastAPI":
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Install dependencies before running the API.")
    app = FastAPI(title=APP_NAME)
    app.include_router(health_router)
    app.include_router(sample_router)
    web_root = Path(__file__).resolve().parents[1] / "web"
    app.mount("/static", StaticFiles(directory=str(web_root)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return (web_root / "index.html").read_text(encoding="utf-8")

    return app


app = create_app()


def _main() -> None:
    import uvicorn
    port = int(os.environ.get("APP_PORT", "8000"))
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    _main()
""")

    write(project_dir / "apps" / "web" / "index.html", make_index_html(app_name))
    write(project_dir / "apps" / "api" / "_auto_catalog.py", make_auto_catalog(app_name))
    write(project_dir / "README.md", f"""# {app_name}

本项目由自动化流水线生成，用于演示“{app_name}”的最小可运行闭环：

- Web 控制台：`/`（用于截图与操作手册素材）
- API 健康检查：`/api/health`
- 样本示例数据：`/api/samples`

运行方式（开发机）：

```powershell
python -m apps.api.main
```
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
