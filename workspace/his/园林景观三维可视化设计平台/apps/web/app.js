const App = (() => {
  const state = {
    token: localStorage.getItem("g3d_token") || "",
    role: localStorage.getItem("g3d_role") || "",
    season: "春",
    plants: [],
    materials: [],
    lights: [],
    issues: [],
    versions: [],
  };

  async function apiGet(path) {
    const headers = {};
    if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
    const res = await fetch(path, { headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.ok === false) throw new Error(data.error || "api_failed");
    return data;
  }

  async function loadCoreData() {
    const [plants, materials, lights, issues, versions] = await Promise.all([
      apiGet("/api/plants"),
      apiGet("/api/materials"),
      apiGet("/api/lights"),
      apiGet("/api/issues"),
      apiGet("/api/versions"),
    ]);
    state.plants = plants.items || [];
    state.materials = materials.items || [];
    state.lights = lights.items || [];
    state.issues = issues.items || [];
    state.versions = versions.items || [];
  }

  const views = {
    home: {
      title: "方案总览",
      desc: "聚焦场地、版本、评审与清单输出。",
      render: () => `
        <div class="grid">
          <section class="card">
            <div class="hd"><h2>快速入口</h2><span class="pill">自然雅致主题</span></div>
            <div class="bd">
              <div class="row">
                <a class="btn primary" href="#site">进入场地</a>
                <a class="btn" href="#plan">方案编辑</a>
                <a class="btn" href="#review">评审中心</a>
                <a class="btn" href="#export">清单导出</a>
              </div>
              <div style="height:10px"></div>
              <div class="muted">演示账号：admin/admin123（用于自动截图与门禁）。</div>
            </div>
          </section>
          <section class="card">
            <div class="hd"><h2>关键指标</h2><span class="muted">V1.0 数据示例</span></div>
            <div class="bd">
              <div class="kpi">
                <div class="box"><div class="num">1</div><div class="lab">场地</div></div>
                <div class="box"><div class="num">3</div><div class="lab">方案版本</div></div>
                <div class="box"><div class="num">${state.plants.length}</div><div class="lab">植物品种</div></div>
                <div class="box"><div class="num">${state.issues.length}</div><div class="lab">评审事项</div></div>
              </div>
            </div>
          </section>
        </div>
      `,
    },
    site: {
      title: "场地与底图",
      desc: "底图标定、北向与比例尺，作为三维场景的基准。",
      render: () => `
        <section class="card">
          <div class="hd"><h2>场地信息</h2><span class="pill">基准：平面坐标</span></div>
          <div class="bd split">
            <div>
              <div class="field"><label>场地名称</label><input value="滨水公园示范段" readonly /></div>
              <div class="field"><label>位置</label><input value="华东 · 城市新区" readonly /></div>
              <div class="field"><label>比例尺标定</label><input value="1px = 0.05m（两点测距标定）" readonly /></div>
              <div class="muted">提示：V1.0 以快速可视化与清单闭环为主，地形与构件为轻量参数化对象。</div>
            </div>
            <div>
              <div class="field"><label>底图（示意）</label><div class="card" style="border-style:dashed; box-shadow:none; padding:14px;">
                <div class="muted">底图上传与透明度调节在完整实现中提供。本演示用于门禁截图与材料生成。</div>
              </div></div>
            </div>
          </div>
        </section>
      `,
    },
    plan: {
      title: "方案编辑",
      desc: "道路、铺装、水体、构筑物与季相预览。",
      render: () => `
        <section class="card">
          <div class="hd">
            <h2>编辑面板</h2>
            <div class="row">
              <span class="pill">季相：${state.season}</span>
              <button class="btn" id="season-btn">切换季节</button>
              <a class="btn" href="#planting">植物布置</a>
              <a class="btn" href="#materials">材质库</a>
            </div>
          </div>
          <div class="bd">
            <div class="view-title">
              <div>
                <h3>三维视窗（演示）</h3>
                <p>真实三维渲染在 V1.0 规划中采用浏览器 WebGL；此处用“场景要素清单”替代，以便截图、文档与代码闭环。</p>
              </div>
              <span class="pill">版本：V1.0.0</span>
            </div>
            <div style="height:8px"></div>
            <table>
              <thead><tr><th>要素</th><th>参数</th><th>说明</th></tr></thead>
              <tbody>
                <tr><td>道路</td><td>中心线+宽度 3.5m</td><td>主园路，圆角过渡</td></tr>
                <tr><td>铺装面</td><td>透水砖（暖灰）</td><td>入口广场与节点铺装</td></tr>
                <tr><td>水体</td><td>水面高程 +0.2m</td><td>浅水景观与亲水平台</td></tr>
                <tr><td>灯光</td><td>3000K 暖光</td><td>夜景路径引导</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      `,
      bind: () => {
        const btn = document.getElementById("season-btn");
        if (!btn) return;
        btn.addEventListener("click", () => {
          const order = ["春", "夏", "秋", "冬"];
          const idx = order.indexOf(state.season);
          state.season = order[(idx + 1) % order.length];
          render();
        });
      },
    },
    planting: {
      title: "植物库与布置",
      desc: "品种、规格与季相信息统一到清单中。",
      render: () => `
        <section class="card">
          <div class="hd">
            <h2>植物库（可评审）</h2>
            <div class="row">
              <button class="btn primary" data-action="create">新增</button>
              <button class="btn" data-action="edit">编辑</button>
              <button class="btn" data-action="view">查看</button>
              <button class="btn danger" data-action="delete">删除</button>
            </div>
          </div>
          <div class="bd">
            <div class="muted">说明：此页用于展示“新增/编辑/查看/删除”四类弹窗截图，支撑软著操作手册与门禁截图计划。</div>
            <div style="height:10px"></div>
            <table>
              <thead><tr><th>编号</th><th>中文名</th><th>类别</th><th>常绿/落叶</th><th>冠幅</th><th>季相要点</th></tr></thead>
              <tbody>
                ${
                  state.plants
                    .map((p) => {
                      const evergreen = p.evergreen ? "常绿" : "落叶";
                      const crown = `${p.crownMinM}-${p.crownMaxM}m`;
                      return `<tr><td>${p.code}</td><td>${p.cnName}</td><td>${p.category}</td><td>${evergreen}</td><td>${crown}</td><td>${p.seasonHint || ""}</td></tr>`;
                    })
                    .join("")
                }
              </tbody>
            </table>
          </div>
        </section>
      `,
      bind: () => {
        document.querySelectorAll('[data-action]').forEach((el) => {
          el.addEventListener("click", () => openPlantModal(el.getAttribute("data-action")));
        });
      },
    },
    materials: {
      title: "材料与铺装",
      desc: "把视觉效果与工程清单映射到同一份材料字典。",
      render: () => `
        <section class="card">
          <div class="hd"><h2>材料字典</h2><span class="pill">低饱和 · 暖灰</span></div>
          <div class="bd">
            <table>
              <thead><tr><th>编号</th><th>名称</th><th>计量单位</th><th>用途</th></tr></thead>
              <tbody>
                ${state.materials.map(m => `<tr><td>${m.code}</td><td>${m.name}</td><td>${m.unit}</td><td>${m.usage}</td></tr>`).join("")}
              </tbody>
            </table>
          </div>
        </section>
      `,
    },
    review: {
      title: "评审中心",
      desc: "意见基于截图流转，版本可追溯。",
      render: () => `
        <section class="card">
          <div class="hd"><h2>评审事项</h2><span class="pill">版本：V1.0.0</span></div>
          <div class="bd">
            <table>
              <thead><tr><th>编号</th><th>标题</th><th>标签</th><th>优先级</th><th>状态</th></tr></thead>
              <tbody>
                ${state.issues.map(i => `<tr><td>${i.id}</td><td>${i.title}</td><td>${i.tag}</td><td>${i.priority}</td><td>${i.status}</td></tr>`).join("")}
              </tbody>
            </table>
            <div style="height:10px"></div>
            <div class="muted">V1.0：意见状态流转为 新建→处理中→已解决→已关闭。演示数据用于材料生成与截图。</div>
          </div>
        </section>
      `,
    },
    export: {
      title: "清单导出",
      desc: "植物、材料与灯具清单以 CSV 输出，支撑交付与招采。",
      render: () => `
        <section class="card">
          <div class="hd"><h2>导出面板</h2><span class="muted">示例导出</span></div>
          <div class="bd">
            <div class="row">
              <button class="btn primary" id="export-plants">导出植物清单</button>
              <button class="btn" id="export-materials">导出材料清单</button>
              <button class="btn" id="export-lights">导出灯具清单</button>
            </div>
            <div style="height:12px"></div>
            <pre id="export-out" class="card" style="box-shadow:none; background:#fbfcfb; border-style:dashed; padding:12px; white-space:pre-wrap; margin:0;"></pre>
          </div>
        </section>
      `,
      bind: () => {
        const out = document.getElementById("export-out");
        const write = (txt) => { if(out) out.textContent = txt; };
        const csv = (rows) => rows.map(r => r.map(v => `"${String(v).replaceAll('"','""')}"`).join(",")).join("\n");
        document.getElementById("export-plants")?.addEventListener("click", () => {
          write(csv([["编号","中文名","类别","常绿/落叶","冠幅范围(m)"], ...state.plants.map(p=>[p.code,p.cnName,p.category,(p.evergreen? "常绿":"落叶"),`${p.crownMinM}-${p.crownMaxM}`])]));
        });
        document.getElementById("export-materials")?.addEventListener("click", () => {
          write(csv([["编号","名称","单位","用途"], ...state.materials.map(m=>[m.code,m.name,m.unit,m.usage])]));
        });
        document.getElementById("export-lights")?.addEventListener("click", () => {
          write(csv([["编号","色温","功率(W)","数量"], ...state.lights.map(l=>[l.code,l.cct,l.watt,l.qty])]));
        });
      },
    },
  };

  function setActiveNav(hash) {
    document.querySelectorAll(".nav a").forEach((a) => {
      const target = (a.getAttribute("href") || "").replace(/^#/, "");
      a.classList.toggle("active", target === hash);
    });
  }

  function currentHash() {
    const h = (location.hash || "").replace(/^#/, "");
    return h || "home";
  }

  function ensureAuth() {
    const view = currentHash();
    if (!state.token && view !== "login") {
      location.hash = "login";
      return false;
    }
    return true;
  }

  function openModal({ title, bodyHtml, footerButtons }) {
    const shell = document.getElementById("modal");
    shell.classList.add("modal");
    shell.innerHTML = `
      <div class="modal" role="dialog" aria-label="${escapeHtml(title)}">
        <div class="mhd">
          <strong>${escapeHtml(title)}</strong>
          <button class="btn" id="modal-close">关闭</button>
        </div>
        <div class="mbd">${bodyHtml}</div>
        <div class="mft">${footerButtons || `<button class="btn primary" id="modal-ok">确定</button>`}</div>
      </div>
    `;
    shell.querySelector("#modal-close")?.addEventListener("click", closeModal);
    shell.querySelector("#modal-ok")?.addEventListener("click", closeModal);
  }

  function closeModal() {
    const shell = document.getElementById("modal");
    shell.classList.remove("modal");
    shell.innerHTML = "";
  }

  function openPlantModal(action) {
    const map = { create: "新增植物品种", edit: "编辑植物信息", view: "查看植物详情", delete: "删除植物确认" };
    const title = map[action] || "植物操作";
    if (action === "delete") {
      return openModal({
        title,
        bodyHtml: `<p>将从本方案的植物字典中移除所选品种（示例：紫薇 P-002）。</p><p class="muted">V1.0 演示不做真实删除，仅用于截图与流程说明。</p>`,
        footerButtons: `<button class="btn" id="modal-ok">取消</button><button class="btn danger" id="modal-del">确认删除</button>`,
      });
    }
    const readonly = action === "view" ? "readonly" : "";
    const hint = action === "view" ? "（只读预览）" : "（示例表单）";
    openModal({
      title: `${title}${hint}`,
      bodyHtml: `
        <div class="split">
          <div class="field"><label>中文名</label><input value="紫薇" ${readonly} /></div>
          <div class="field"><label>类别</label><select ${readonly ? "disabled" : ""}><option>乔木</option><option>灌木</option><option>地被</option></select></div>
          <div class="field"><label>常绿/落叶</label><select ${readonly ? "disabled" : ""}><option>落叶</option><option>常绿</option></select></div>
          <div class="field"><label>冠幅范围</label><input value="3-5m" ${readonly} /></div>
        </div>
        <div class="field"><label>季相要点</label><textarea ${readonly}>夏季花期明显，适合节点色彩强调；秋季叶色偏黄，建议与常绿灌木搭配。</textarea></div>
      `,
    });
  }

  function escapeHtml(s) {
    return String(s).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;");
  }

  async function apiLogin(username, password) {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.ok) throw new Error(data.error || "login_failed");
    return data;
  }

  function bindLogin() {
    const form = document.getElementById("login-form");
    if (!form) return;
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const u = form.querySelector('input[name="username"]').value.trim();
      const p = form.querySelector('input[name="password"]').value.trim();
      const msg = document.getElementById("login-msg");
      try {
        const data = await apiLogin(u, p);
        state.token = data.token;
        state.role = data.role;
        localStorage.setItem("g3d_token", state.token);
        localStorage.setItem("g3d_role", state.role);
        location.hash = "home";
      } catch (err) {
        if (msg) msg.textContent = "账号或密码不正确（演示：admin/admin123）。";
      }
    });
  }

  function renderLogin() {
    return `
      <div class="wrap">
        <section class="card" style="max-width:860px; margin:26px auto;">
          <div class="hd">
            <h2>登录</h2>
            <span class="pill">园林景观三维可视化设计平台</span>
          </div>
          <div class="bd">
            <div class="split">
              <div>
                <form id="login-form">
                  <div class="field"><label>用户名</label><input name="username" autocomplete="username" value="admin" /></div>
                  <div class="field"><label>密码</label><input name="password" type="password" autocomplete="current-password" value="admin123" /></div>
                  <div class="row">
                    <button class="btn primary" type="submit">登录</button>
                    <span id="login-msg" class="muted"></span>
                  </div>
                </form>
              </div>
              <div>
                <div class="card" style="box-shadow:none; background:#fbfcfb; border-style:dashed;">
                  <div class="bd">
                    <div class="view-title">
                      <div>
                        <h3>演示说明</h3>
                        <p>本系统用于软著材料自动生成：登录、首页、核心功能页与弹窗截图将自动采集。</p>
                      </div>
                      <span class="pill">V1.0</span>
                    </div>
                    <ul class="muted">
                      <li>设计师：designer/design123</li>
                      <li>评审人：reviewer/review123</li>
                      <li>管理员：admin/admin123</li>
                    </ul>
                    <div class="muted">视觉风格：低饱和绿 + 暖灰 + 克制阴影，突出绿植与场景留白。</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    `;
  }

  function renderShell(innerHtml) {
    const h = currentHash();
    const navItems = [
      ["home", "总览"],
      ["site", "场地"],
      ["plan", "方案"],
      ["planting", "植物"],
      ["materials", "材料"],
      ["review", "评审"],
      ["export", "导出"],
    ];
    return `
      <header>
        <div class="topbar">
          <div class="brand">
            <div class="logo" aria-hidden="true"></div>
            <div>
              <h1>园林景观三维可视化设计平台</h1>
              <div class="sub">自然雅致 · 版本 V1.0 · 登录角色：${state.role || "未登录"}</div>
            </div>
          </div>
          <nav class="nav" aria-label="主导航">
            ${navItems.map(([k, t]) => `<a href="#${k}" class="${k === h ? "active" : ""}">${t}</a>`).join("")}
            <a href="#login" id="logout-link">退出</a>
          </nav>
        </div>
      </header>
      <div class="wrap">${innerHtml}</div>
      <div id="modal" class="modal-shell"></div>
    `;
  }

  function bindShell() {
    document.getElementById("logout-link")?.addEventListener("click", () => {
      state.token = "";
      state.role = "";
      localStorage.removeItem("g3d_token");
      localStorage.removeItem("g3d_role");
      closeModal();
    });
  }

  async function render() {
    const mount = document.getElementById("app");
    const h = currentHash();
    if (!mount) return;

    if (h === "login") {
      mount.innerHTML = renderLogin();
      bindLogin();
      return;
    }

    if (!ensureAuth()) return;
    if (!state.plants.length || !state.materials.length || !state.issues.length) {
      try {
        await loadCoreData();
      } catch (e) {
        // During static preview, api may be unavailable; keep UI usable.
      }
    }
    const view = views[h] || views.home;
    const inner = view.render();
    mount.innerHTML = renderShell(inner);
    setActiveNav(h);
    bindShell();
    view.bind?.();
  }

  window.__rkModal = { closeModal };
  window.addEventListener("hashchange", render);

  return { render };
})();

window.addEventListener("DOMContentLoaded", () => App.render());
