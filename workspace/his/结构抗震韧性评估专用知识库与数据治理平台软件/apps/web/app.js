/* Blueprint-style SPA for resilience knowledge base & governance */
const state = {
  token: "",
  role: "",
  displayName: "",
  view: "home",
  cache: {
    projects: [],
    structures: [],
    datasets: [],
    audit: [],
  },
  selection: {
    projectId: 1,
    structureId: 1,
    datasetId: 1,
    datasetVersionId: 1,
  },
};

const el = (id) => document.getElementById(id);
const storage = {
  load() {
    try {
      const raw = localStorage.getItem("rk_session") || "";
      if (!raw) return null;
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },
  save(session) {
    localStorage.setItem("rk_session", JSON.stringify(session));
  },
  clear() {
    localStorage.removeItem("rk_session");
  },
};

function api(path, { method = "GET", body = null } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
  return fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  }).then(async (r) => {
    const text = await r.text();
    let data = {};
    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      data = { raw: text };
    }
    if (!r.ok) throw new Error(data.detail || data.message || `HTTP ${r.status}`);
    return data;
  });
}

function setActiveNav(hash) {
  document.querySelectorAll(".nav-item").forEach((a) => {
    a.classList.toggle("active", a.dataset.hash === hash);
  });
}

function setRolePill() {
  const pill = el("role-pill");
  if (!state.token) {
    pill.textContent = "未登录";
    return;
  }
  const name = state.displayName ? `${state.displayName}` : "用户";
  pill.textContent = `${name} · ${state.role}`;
}

function show(panelLogin) {
  el("panel-login").classList.toggle("hidden", !panelLogin);
  el("panel-main").classList.toggle("hidden", panelLogin);
}

function routeFromHash() {
  const raw = (location.hash || "#home").replace("#", "");
  const hash = raw.trim() || "home";
  state.view = hash === "home" ? "home" : hash;
  setActiveNav(state.view);
  render();
}

function setTitle(title, desc) {
  el("view-title").textContent = title;
  el("view-desc").textContent = desc;
}

function card(k, v) {
  return `<div class="card"><div class="k">${k}</div><div class="v">${v}</div></div>`;
}

function renderCards(cards) {
  el("cards").innerHTML = cards.join("");
}

function renderTable(columns, rows, actions = []) {
  el("thead").innerHTML = `<tr>${columns.map((c) => `<th>${c}</th>`).join("")}<th>操作</th></tr>`;
  el("tbody").innerHTML = rows
    .map((r, idx) => {
      const tds = columns.map((c) => `<td>${escapeHtml(String(r[c] ?? ""))}</td>`).join("");
      const btns = actions
        .map((a) => `<button class="btn btn-ghost" data-act="${a.act}" data-idx="${idx}">${a.label}</button>`)
        .join(" ");
      return `<tr>${tds}<td>${btns}</td></tr>`;
    })
    .join("");
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]));
}

function openModal(title, contentHtml, footButtons = []) {
  el("modal-title").textContent = title;
  el("modal-content").innerHTML = contentHtml;
  el("modal-foot").innerHTML = footButtons
    .map((b) => `<button class="btn ${b.kind || "btn-ghost"}" data-modal-act="${b.act}">${b.label}</button>`)
    .join("");
  el("modal").classList.add("modal");
  el("modal").classList.remove("hidden");
}

function closeModal() {
  el("modal").classList.remove("modal");
  el("modal").classList.add("hidden");
  el("modal-content").innerHTML = "";
  el("modal-foot").innerHTML = "";
}

window.__rkModal = { openModal, closeModal };

function bindModalActions(handlers) {
  el("modal-foot").querySelectorAll("[data-modal-act]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const act = btn.dataset.modalAct;
      if (handlers[act]) handlers[act]();
    });
  });
}

function buildForm(fields, initial = {}) {
  return `
    <form class="form" id="modal-form">
      ${fields
        .map((f) => {
          const val = initial[f.key] ?? "";
          return `
          <label class="field">
            <span>${f.label}</span>
            <input name="${f.key}" value="${escapeHtml(String(val))}" placeholder="${escapeHtml(f.ph || "")}"/>
          </label>
        `;
        })
        .join("")}
    </form>
  `;
}

function readForm() {
  const form = document.getElementById("modal-form");
  const fd = new FormData(form);
  const obj = {};
  for (const [k, v] of fd.entries()) obj[k] = String(v).trim();
  return obj;
}

async function refreshCache() {
  state.cache.projects = await api("/projects");
  state.cache.structures = await api("/structures");
  state.cache.datasets = await api("/datasets");
  state.cache.audit = await api("/audit/logs?limit=80");
}

function render() {
  if (!state.token) return;

  const view = state.view;
  const createBtn = el("btn-create");
  createBtn.classList.remove("hidden");

  if (view === "home") {
    setTitle("首页概览", "从链路视角浏览：项目/结构/数据集与审计概况。");
    renderCards([
      card("项目数量", state.cache.projects.length),
      card("结构对象", state.cache.structures.length),
      card("数据集", state.cache.datasets.length),
      card("审计记录(近80)", state.cache.audit.length),
    ]);
    const rows = state.cache.projects.map((p) => ({
      id: p.id,
      name: p.name,
      region: p.region,
      site_class: p.site_class,
      importance: p.importance,
      owner: p.owner,
    }));
    renderTable(["id", "name", "region", "site_class", "importance", "owner"], rows, [
      { act: "view", label: "查看" },
    ]);
    bindTableActions({
      view: (row) => openModal("查看", `<pre>${escapeHtml(JSON.stringify(row, null, 2))}</pre>`),
    });
    createBtn.classList.add("hidden");
    return;
  }

  if (view === "projects") {
    setTitle("项目台账", "创建与维护评估项目，作为结构对象与评估记录的容器。");
    renderCards([
      card("当前项目数", state.cache.projects.length),
      card("区域分布", new Set(state.cache.projects.map((p) => p.region)).size),
      card("场地类别", new Set(state.cache.projects.map((p) => p.site_class)).size),
      card("重要性等级", new Set(state.cache.projects.map((p) => p.importance)).size),
    ]);
    renderTable(["id", "name", "region", "site_class", "importance", "owner"], state.cache.projects, [
      { act: "view", label: "查看" },
      { act: "edit", label: "编辑" },
      { act: "delete", label: "删除" },
    ]);
    bindTableActions({
      view: (row) => openModal("查看", `<pre>${escapeHtml(JSON.stringify(row, null, 2))}</pre>`),
      edit: (row) => openProjectEdit(row),
      delete: (row) => openProjectDelete(row),
    });
    createBtn.onclick = () => openProjectCreate();
    return;
  }

  if (view === "structures") {
    setTitle("结构对象", "在项目下登记结构对象，用于指标绑定与评估记录归档。");
    renderCards([
      card("结构对象总数", state.cache.structures.length),
      card("结构类型", new Set(state.cache.structures.map((s) => s.type)).size),
      card("材料体系", new Set(state.cache.structures.map((s) => s.material_system)).size),
      card("设防烈度", new Set(state.cache.structures.map((s) => s.fortification_intensity)).size),
    ]);
    renderTable(
      ["id", "project_name", "name", "type", "year_built", "stories", "material_system", "fortification_intensity"],
      state.cache.structures,
      [{ act: "view", label: "查看" }]
    );
    bindTableActions({
      view: (row) => openModal("查看", `<pre>${escapeHtml(JSON.stringify(row, null, 2))}</pre>`),
    });
    createBtn.onclick = () =>
      openModal(
        "新增",
        buildForm(
          [
            { key: "project_id", label: "项目ID", ph: "1" },
            { key: "name", label: "结构名称" },
            { key: "type", label: "结构类型" },
            { key: "year_built", label: "建成年代", ph: "2012" },
            { key: "stories", label: "层数", ph: "18" },
            { key: "material_system", label: "材料体系" },
            { key: "fortification_intensity", label: "设防烈度" },
          ],
          { project_id: 1, year_built: 2012, stories: 10 }
        ),
        [
          { act: "cancel", label: "取消" },
          { act: "submit", label: "提交", kind: "btn-primary" },
        ]
      );
    el("modal-close").onclick = closeModal;
    bindModalActions({
      cancel: closeModal,
      submit: async () => {
        const v = readForm();
        v.project_id = Number(v.project_id || 1);
        v.year_built = Number(v.year_built || 2010);
        v.stories = Number(v.stories || 1);
        await api("/structures", { method: "POST", body: v });
        closeModal();
        await refreshCache();
        render();
      },
    });
    return;
  }

  if (view === "datasets") {
    setTitle("数据集治理", "登记数据集并维护版本与来源说明，形成可复核的数据台账。");
    renderCards([
      card("数据集总数", state.cache.datasets.length),
      card("敏感级别", new Set(state.cache.datasets.map((d) => d.sensitivity_level)).size),
      card("类别", new Set(state.cache.datasets.map((d) => d.category)).size),
      card("责任人", new Set(state.cache.datasets.map((d) => d.owner)).size),
    ]);
    renderTable(["id", "name", "category", "owner", "sensitivity_level"], state.cache.datasets, [
      { act: "view", label: "查看" },
    ]);
    bindTableActions({
      view: async (row) => {
        const versions = await api(`/datasets/${row.id}/versions`);
        openModal(
          "查看",
          `<pre>${escapeHtml(JSON.stringify({ dataset: row, versions }, null, 2))}</pre>`
        );
      },
    });
    createBtn.onclick = () => openDatasetCreate();
    return;
  }

  if (view === "quality") {
    setTitle("质量检查", "对数据集版本执行质量规则，输出评分与问题明细。");
    renderCards([
      card("默认演示数据集ID", 1),
      card("建议规则", 3),
      card("执行频率", "按版本/按需"),
      card("输出", "评分+问题列表"),
    ]);
    const rows = [
      { dataset_version_id: 1, action: "查看默认示例（需先创建版本/规则）", hint: "演示环境可先新增版本再执行" },
    ];
    renderTable(["dataset_version_id", "action", "hint"], rows, [{ act: "view", label: "查看" }]);
    bindTableActions({
      view: () =>
        openModal(
          "查看",
          `<div class="muted">质量检查页面的“查看”用于展示一次模拟执行入口。你也可以从“数据集治理”创建版本后再运行。</div>`,
          [
            { act: "cancel", label: "关闭" },
            { act: "run", label: "执行质量检查", kind: "btn-primary" },
          ]
        ),
    });
    bindModalActions({
      cancel: closeModal,
      run: async () => {
        const result = await api(`/quality/run?dataset_version_id=1`, { method: "POST" }).catch((e) => ({ error: String(e) }));
        openModal("查看", `<pre>${escapeHtml(JSON.stringify(result, null, 2))}</pre>`);
      },
    });
    createBtn.onclick = () => openQualityRuleCreate();
    return;
  }

  if (view === "indicators") {
    setTitle("指标配置", "为结构对象配置指标，并绑定到数据集版本以支撑可追溯评估。");
    renderCards([card("示例结构ID", 1), card("指标来源", "数据版本"), card("方法", "公式/人工"), card("单位", "可配置")]);
    renderTable(["hint", "value"], [{ hint: "本版本以演示为主", value: "可通过 API 创建 indicators 并写入 bindings" }], [
      { act: "view", label: "查看" },
    ]);
    bindTableActions({
      view: () =>
        openModal(
          "查看",
          `<pre>${escapeHtml(
            JSON.stringify(
              {
                example: {
                  structure_id: 1,
                  name: "层间位移角(限值比)",
                  method: "manual_or_formula",
                  unit: "ratio",
                  data_bindings_json: { dataset_version_id: 1, fields: ["story_drift_angle"] },
                },
              },
              null,
              2
            )
          )}</pre>`
        ),
    });
    createBtn.onclick = () =>
      openModal(
        "新增",
        buildForm(
          [
            { key: "structure_id", label: "结构ID", ph: "1" },
            { key: "name", label: "指标名称", ph: "层间位移角(限值比)" },
            { key: "method", label: "方法", ph: "manual_or_formula" },
            { key: "unit", label: "单位", ph: "ratio" },
          ],
          { structure_id: 1, method: "manual_or_formula", unit: "ratio" }
        ),
        [
          { act: "cancel", label: "取消" },
          { act: "submit", label: "提交", kind: "btn-primary" },
        ]
      );
    bindModalActions({
      cancel: closeModal,
      submit: async () => {
        const v = readForm();
        const payload = {
          structure_id: Number(v.structure_id || 1),
          name: v.name || "指标",
          method: v.method || "manual",
          unit: v.unit || "-",
          data_bindings_json: { dataset_version_id: 1, fields: ["demo_field"] },
        };
        await api("/indicators", { method: "POST", body: payload });
        closeModal();
        openModal("查看", `<pre>${escapeHtml(JSON.stringify({ ok: true, created: payload }, null, 2))}</pre>`);
      },
    });
    return;
  }

  if (view === "assessments") {
    setTitle("评估记录", "提交评估任务并形成结论，支持复核与知识沉淀。");
    renderCards([card("状态", "submitted/approved/rejected"), card("证据链", "lineage_edges"), card("复核", "review endpoint"), card("沉淀", "knowledge")]);
    renderTable(["hint", "value"], [{ hint: "演示入口", value: "点击新增创建一条评估记录(绑定指标ID列表)" }], [
      { act: "view", label: "查看" },
    ]);
    bindTableActions({
      view: () => openModal("查看", `<div class="muted">评估记录以结构对象为主键聚合。演示可直接通过“新增”创建。</div>`),
    });
    createBtn.onclick = () =>
      openModal(
        "新增",
        buildForm(
          [
            { key: "structure_id", label: "结构ID", ph: "1" },
            { key: "summary", label: "评估摘要", ph: "本结构在设防烈度下具备可接受的功能恢复能力..." },
            { key: "indicator_ids", label: "指标ID列表(逗号分隔)", ph: "1,2" },
          ],
          { structure_id: 1, indicator_ids: "1" }
        ),
        [
          { act: "cancel", label: "取消" },
          { act: "submit", label: "提交", kind: "btn-primary" },
        ]
      );
    bindModalActions({
      cancel: closeModal,
      submit: async () => {
        const v = readForm();
        const ids = (v.indicator_ids || "")
          .split(",")
          .map((x) => Number(x.trim()))
          .filter((x) => Number.isFinite(x) && x > 0);
        const payload = { structure_id: Number(v.structure_id || 1), summary: v.summary || "评估摘要", indicator_ids: ids };
        const res = await api("/assessments", { method: "POST", body: payload });
        closeModal();
        openModal("查看", `<pre>${escapeHtml(JSON.stringify(res, null, 2))}</pre>`);
      },
    });
    return;
  }

  if (view === "knowledge") {
    setTitle("知识条目", "沉淀评估结论与证据引用，支持检索与复用。");
    renderCards([card("沉淀来源", "评估记录"), card("标签", "结构类型/区域/指标"), card("证据", "数据版本+质量"), card("用途", "复核与复用")]);
    renderTable(["hint", "value"], [{ hint: "演示入口", value: "点击新增创建知识条目" }], [{ act: "view", label: "查看" }]);
    bindTableActions({
      view: () => openModal("查看", `<div class="muted">知识条目支持关键词检索，后端提供 /knowledge?q=...</div>`),
    });
    createBtn.onclick = () =>
      openModal(
        "新增",
        buildForm(
          [
            { key: "title", label: "标题", ph: "框架-剪力墙结构韧性评估结论条目" },
            { key: "tags", label: "标签(逗号分隔)", ph: "框剪,滨海新区,层间位移角" },
            { key: "summary", label: "摘要", ph: "关键指标与证据链摘要..." },
          ],
          { title: "结构韧性评估知识条目", tags: "韧性,证据链" }
        ),
        [
          { act: "cancel", label: "取消" },
          { act: "submit", label: "提交", kind: "btn-primary" },
        ]
      );
    bindModalActions({
      cancel: closeModal,
      submit: async () => {
        const v = readForm();
        const payload = {
          title: v.title || "知识条目",
          tags: (v.tags || "").split(",").map((x) => x.trim()).filter(Boolean),
          summary: v.summary || "",
          evidence_refs_json: { dataset_version_id: 1, quality_run_id: 1, note: "demo evidence" },
        };
        const res = await api("/knowledge", { method: "POST", body: payload });
        closeModal();
        openModal("查看", `<pre>${escapeHtml(JSON.stringify(res, null, 2))}</pre>`);
      },
    });
    return;
  }

  if (view === "audit") {
    setTitle("审计留痕", "关键操作统一写入审计日志，便于复核与问责。");
    renderCards([card("展示上限", "80"), card("动作类型", "create/update/delete/run/review/login"), card("对象", "project/dataset/..."), card("时间", "Unix 秒")]);
    renderTable(["id", "actor", "action", "object_type", "object_id", "detail", "at"], state.cache.audit, [{ act: "view", label: "查看" }]);
    bindTableActions({
      view: (row) => openModal("查看", `<pre>${escapeHtml(JSON.stringify(row, null, 2))}</pre>`),
    });
    createBtn.classList.add("hidden");
    return;
  }
}

function bindTableActions(handlers) {
  el("tbody").querySelectorAll("[data-act]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = Number(btn.dataset.idx);
      const act = btn.dataset.act;
      const rows = currentRows();
      const row = rows[idx];
      if (handlers[act]) handlers[act](row);
    });
  });
}

function currentRows() {
  const view = state.view;
  if (view === "home") return state.cache.projects.map((p) => ({ ...p }));
  if (view === "projects") return state.cache.projects;
  if (view === "structures") return state.cache.structures;
  if (view === "datasets") return state.cache.datasets;
  if (view === "audit") return state.cache.audit;
  return [];
}

function openProjectCreate() {
  openModal(
    "新增",
    buildForm(
      [
        { key: "name", label: "项目名称" },
        { key: "region", label: "区域", ph: "滨海新区" },
        { key: "site_class", label: "场地类别", ph: "II类场地" },
        { key: "importance", label: "重要性等级", ph: "乙类" },
      ],
      {}
    ),
    [
      { act: "cancel", label: "取消" },
      { act: "submit", label: "提交", kind: "btn-primary" },
    ]
  );
  bindModalActions({
    cancel: closeModal,
    submit: async () => {
      const v = readForm();
      await api("/projects", { method: "POST", body: v });
      closeModal();
      await refreshCache();
      render();
    },
  });
}

function openProjectEdit(row) {
  openModal(
    "编辑",
    buildForm(
      [
        { key: "name", label: "项目名称" },
        { key: "region", label: "区域" },
        { key: "site_class", label: "场地类别" },
        { key: "importance", label: "重要性等级" },
      ],
      row
    ),
    [
      { act: "cancel", label: "取消" },
      { act: "submit", label: "提交", kind: "btn-primary" },
    ]
  );
  bindModalActions({
    cancel: closeModal,
    submit: async () => {
      const v = readForm();
      await api(`/projects/${row.id}`, { method: "PUT", body: v });
      closeModal();
      await refreshCache();
      render();
    },
  });
}

function openProjectDelete(row) {
  openModal("删除", `<div>确认删除项目：<b>${escapeHtml(row.name)}</b>？该操作会级联删除结构对象。</div>`, [
    { act: "cancel", label: "取消" },
    { act: "submit", label: "删除", kind: "btn-primary" },
  ]);
  bindModalActions({
    cancel: closeModal,
    submit: async () => {
      await api(`/projects/${row.id}`, { method: "DELETE" });
      closeModal();
      await refreshCache();
      render();
    },
  });
}

function openDatasetCreate() {
  openModal(
    "新增",
    buildForm(
      [
        { key: "name", label: "数据集名称" },
        { key: "category", label: "类别", ph: "构件台账" },
        { key: "source_desc", label: "来源说明", ph: "现场核查/检测/监测等" },
        { key: "sensitivity_level", label: "敏感级别", ph: "内部" },
      ],
      {}
    ),
    [
      { act: "cancel", label: "取消" },
      { act: "submit", label: "提交", kind: "btn-primary" },
    ]
  );
  bindModalActions({
    cancel: closeModal,
    submit: async () => {
      const v = readForm();
      await api("/datasets", { method: "POST", body: v });
      closeModal();
      await refreshCache();
      render();
    },
  });
}

function openQualityRuleCreate() {
  openModal(
    "新增",
    buildForm(
      [
        { key: "dataset_id", label: "数据集ID", ph: "1" },
        { key: "rule_type", label: "规则类型", ph: "required_field / min_items / enum" },
        { key: "rule_expr", label: "规则表达式", ph: "required_field: fieldName; min_items: items,2; enum: level=a|b" },
        { key: "severity", label: "严重性", ph: "warn / error" },
      ],
      { dataset_id: 1, rule_type: "required_field", rule_expr: "items", severity: "error" }
    ),
    [
      { act: "cancel", label: "取消" },
      { act: "submit", label: "提交", kind: "btn-primary" },
    ]
  );
  bindModalActions({
    cancel: closeModal,
    submit: async () => {
      const v = readForm();
      const payload = {
        dataset_id: Number(v.dataset_id || 1),
        rule_type: v.rule_type || "required_field",
        rule_expr: v.rule_expr || "items",
        severity: v.severity || "error",
        enabled: true,
      };
      await api("/quality/rules", { method: "POST", body: payload });
      closeModal();
      openModal("查看", `<pre>${escapeHtml(JSON.stringify({ ok: true, created: payload }, null, 2))}</pre>`);
    },
  });
}

function bindChrome() {
  window.addEventListener("hashchange", routeFromHash);
  document.querySelectorAll(".nav-item").forEach((a) => a.addEventListener("click", () => setActiveNav(a.dataset.hash)));

  el("modal-close").onclick = closeModal;
  el("modal").addEventListener("click", (e) => {
    if (e.target.classList.contains("modal-mask")) closeModal();
  });

  el("btn-logout").onclick = () => {
    state.token = "";
    state.role = "";
    state.displayName = "";
    storage.clear();
    setRolePill();
    show(true);
    location.hash = "#home";
  };

  el("btn-refresh").onclick = async () => {
    await refreshCache();
    render();
  };

  el("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const username = String(fd.get("username") || "").trim();
    const password = String(fd.get("password") || "").trim();
    el("login-msg").textContent = "";
    try {
      const res = await api("/auth/login", { method: "POST", body: { username, password } });
      state.token = res.token;
      state.role = res.role;
      state.displayName = res.display_name;
      storage.save({ token: state.token, role: state.role, displayName: state.displayName });
      setRolePill();
      show(false);
      await refreshCache();
      routeFromHash();
    } catch (err) {
      el("login-msg").textContent = `登录失败：${String(err.message || err)}`;
    }
  });
}

bindChrome();
const restored = storage.load();
if (restored && restored.token) {
  state.token = restored.token;
  state.role = restored.role || "";
  state.displayName = restored.displayName || "";
  setRolePill();
  show(false);
  refreshCache().then(() => routeFromHash()).catch(() => show(true));
} else {
  show(true);
  setRolePill();
}
