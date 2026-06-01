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
        raise RuntimeError("FastAPI is not installed. Install dependencies before running the API.")
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
    :root { --bg:#0b1020; --panel:#121a33; --text:#e8ecff; --muted:#aab3d9; --accent:#6ee7ff; --danger:#ff5b6e; }
    body { margin:0; font-family: "Segoe UI", "Microsoft YaHei", sans-serif; background:linear-gradient(180deg,#070a14, var(--bg)); color:var(--text); }
    header { display:flex; align-items:center; justify-content:space-between; padding:14px 18px; background:rgba(18,26,51,.8); border-bottom:1px solid rgba(110,231,255,.18); position:sticky; top:0; backdrop-filter: blur(8px); }
    header .brand { font-weight:700; letter-spacing:.5px; }
    header .badge { font-size:12px; padding:4px 10px; border:1px solid rgba(110,231,255,.35); border-radius:999px; color:var(--accent); }
    main { max-width:1180px; margin:18px auto; padding:0 18px 28px; display:grid; grid-template-columns: 260px 1fr; gap:16px; }
    nav { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,.12); border-radius:14px; padding:12px; }
    nav a { display:block; color:var(--muted); text-decoration:none; padding:10px 10px; border-radius:10px; }
    nav a:hover { background:rgba(110,231,255,.08); color:var(--text); }
    .panel { background:rgba(18,26,51,.7); border:1px solid rgba(110,231,255,.12); border-radius:14px; padding:14px; }
    .grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; }
    .card { border:1px solid rgba(110,231,255,.12); border-radius:12px; padding:12px; background:rgba(9,12,24,.55); }
    .card h3 { margin:0 0 8px; font-size:14px; color:var(--accent); }
    .hint { color:var(--muted); font-size:12px; line-height:1.6; }
    .toolbar { display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 6px; }
    button { cursor:pointer; border-radius:10px; border:1px solid rgba(110,231,255,.22); background:rgba(110,231,255,.10); color:var(--text); padding:8px 12px; }
    button:hover { background:rgba(110,231,255,.16); }
    button.danger { border-color:rgba(255,91,110,.35); background:rgba(255,91,110,.12); }
    .k { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; color:var(--accent); }
    .hidden { display:none !important; }
    #loginBox { max-width:520px; margin:10vh auto; padding:18px; }
    #loginBox .row { display:grid; gap:10px; margin-top:10px; }
    input { padding:10px 12px; border-radius:10px; border:1px solid rgba(110,231,255,.18); background:rgba(255,255,255,.05); color:var(--text); }
    .row label { color:var(--muted); font-size:12px; }
    .row small { color:var(--muted); }
    #modal.modal-shell.modal { position:fixed; inset:0; background:rgba(0,0,0,.55); display:flex; align-items:center; justify-content:center; }
    #modal .dialog { width:min(680px, 92vw); border-radius:14px; background:rgba(18,26,51,.96); border:1px solid rgba(110,231,255,.18); padding:14px; box-shadow:0 24px 80px rgba(0,0,0,.45); }
    #modal .dialog header { position:static; border:none; background:transparent; padding:0 0 10px; }
    #modal .dialog .title { font-weight:700; }
    #modal .dialog .content { color:var(--muted); line-height:1.7; font-size:13px; }
  </style>
</head>
<body>
  <div id="loginView">
    <div id="loginBox" class="panel">
      <h1 style="margin:0 0 8px; font-size:18px;">VR多模态交互媒介内容创作与发布系统</h1>
      <div class="hint">V1.0 演示环境：用于截图与材料生成的最小可运行界面。</div>
      <form id="login-form" class="row" onsubmit="return window.__app.login(event)">
        <label>用户名 <input name="username" value="admin" autocomplete="username" /></label>
        <label>密码 <input name="password" type="password" value="admin123" autocomplete="current-password" /></label>
        <button type="submit">登录</button>
        <small>提示：输入任意值均可登录（用于演示与截图）。</small>
      </form>
    </div>
  </div>

  <div id="appView" class="hidden">
    <header>
      <div class="brand">创作与发布控制台</div>
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
        <div id="pageTitle" style="font-weight:700; margin-bottom:10px;">首页</div>
        <div id="pageBody"></div>
      </section>
    </main>
  </div>

  <div id="modal" class="modal-shell modal hidden">
    <div class="dialog" role="dialog" aria-modal="true">
      <header>
        <div class="title" id="modalTitle">操作</div>
        <button class="danger" onclick="window.__rkModal.closeModal()">关闭</button>
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
          <div class="card"><h3>项目概览</h3><div class="hint">资源、场景、交互与发布记录在此汇总展示。</div></div>
          <div class="card"><h3>版本快照</h3><div class="hint">冻结资源清单（含 hash）与交互摘要，支持回滚。</div></div>
          <div class="card"><h3>发布留痕</h3><div class="hint">发布说明、渠道与导出目录可追溯。</div></div>
        </div>`;
    }

    function renderSimplePage(title, id) {
      document.getElementById('pageTitle').textContent = title;
      const body = document.getElementById('pageBody');
      body.innerHTML = `<div id="${id}" class="card">
        <h3>${title}</h3>
        <div class="hint">该页用于演示信息架构与截图留痕。Hash：<span class="k">#${id}</span></div>
      </div>`;
    }

    function renderStations() {
      document.getElementById('pageTitle').textContent = '工作台（Stations）';
      const body = document.getElementById('pageBody');
      body.innerHTML = `
        <div id="stations" class="card">
          <h3>Stations 列表</h3>
          <div class="hint">用于演示“新增/编辑/查看/删除”弹窗操作按钮文案。</div>
          <div class="toolbar">
            <button onclick="window.__rkModal.openModal('新增', '创建新的条目并填写字段。')">新增</button>
            <button onclick="window.__rkModal.openModal('编辑', '修改条目名称、标签与说明。')">编辑</button>
            <button onclick="window.__rkModal.openModal('查看', '查看条目详情与引用关系。')">查看</button>
            <button class="danger" onclick="window.__rkModal.openModal('删除', '删除条目前请确认无引用并记录审计。')">删除</button>
          </div>
          <div class="hint">提示：截图脚本会自动点击以上按钮并截取弹窗状态。</div>
        </div>`;
    }

    function route() {
      const hash = (location.hash || '#home').replace(/^#/, '');
      if (hash === 'home' || hash === '') return renderHome();
      if (hash === 'stations') return renderStations();
      if (hash === 'zones') return renderSimplePage('资源分区', 'zones');
      if (hash === 'inspections') return renderSimplePage('交互检查', 'inspections');
      if (hash === 'alerts') return renderSimplePage('风险提醒', 'alerts');
      if (hash === 'irrigation') return renderSimplePage('发布流水', 'irrigation');
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
    uvicorn.run("apps.api.main:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    _main()
