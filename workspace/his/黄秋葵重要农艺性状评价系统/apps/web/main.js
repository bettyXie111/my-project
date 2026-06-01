import { api } from "./modules/api.js";
import { fmtIsoDateTime, safeText } from "./modules/format.js";
import { mountAudit } from "./modules/view_audit.js";
import { mountObservations } from "./modules/view_observations.js";
import { mountScoring } from "./modules/view_scoring.js";
import { mountTraits } from "./modules/view_traits.js";
import { mountVarieties } from "./modules/view_varieties.js";

const views = [
  { key: "login", panelId: "panel-login", mount: null },
  { key: "home", panelId: "panel-home", mount: null },
  { key: "varieties", panelId: "panel-varieties", mount: mountVarieties },
  { key: "traits", panelId: "panel-traits", mount: mountTraits },
  { key: "observations", panelId: "panel-observations", mount: mountObservations },
  { key: "scoring", panelId: "panel-scoring", mount: mountScoring },
  { key: "audit", panelId: "panel-audit", mount: mountAudit },
];

function selectView(key) {
  for (const v of views) {
    document.getElementById(v.panelId).classList.toggle("is-hidden", v.key !== key);
  }
  for (const btn of document.querySelectorAll(".nav__btn")) {
    btn.classList.toggle("is-active", btn.dataset.view === key);
  }
  const selected = views.find((v) => v.key === key);
  if (selected?.mount) selected.mount(document.getElementById(selected.panelId));
}

function bindNav() {
  for (const btn of document.querySelectorAll(".nav__btn")) {
    btn.addEventListener("click", () => selectView(btn.dataset.view));
  }
}

function openModal(title, bodyHtml) {
  const root = document.getElementById("modal");
  const t = document.getElementById("modal-title");
  const b = document.getElementById("modal-body");
  if (!root || !t || !b) return;
  t.textContent = title;
  b.innerHTML = bodyHtml;
  root.classList.remove("is-hidden");
}

function closeModal() {
  const root = document.getElementById("modal");
  if (root) root.classList.add("is-hidden");
}

function bindModal() {
  const root = document.getElementById("modal");
  if (!root) return;
  root.addEventListener("click", (e) => {
    const t = e.target;
    if (t?.dataset?.close) closeModal();
  });
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

function maybeShowScreenshotModal() {
  const params = new URLSearchParams(location.search || "");
  const modal = String(params.get("modal") || "").toLowerCase() === "true";
  if (!modal) return;
  const action = String(params.get("action") || "").toLowerCase();
  const view = String(location.hash || "").replace(/^#/, "").trim() || "home";
  const titleMap = { create: "新增窗口", edit: "编辑窗口", view: "查看窗口", delete: "删除确认" };
  const title = titleMap[action] || "窗口";
  openModal(
    `${title} · ${view}`,
    `
      <div class="modal__kvs">
        <div class="kvrow"><div class="k">view</div><div class="v">${safeText(view)}</div></div>
        <div class="kvrow"><div class="k">action</div><div class="v">${safeText(action || "-")}</div></div>
        <div class="kvrow"><div class="k">说明</div><div class="v">本弹窗用于软著截图的交互表现，业务逻辑以页面表单为准。</div></div>
      </div>
    `
  );
}

async function refreshTrialList() {
  const q = document.getElementById("trial-q").value.trim();
  const list = document.getElementById("trial-list");
  list.innerHTML = "";
  const trials = await api.listTrials(q);
  if (!trials.length) {
    list.innerHTML = `<div class="list-item"><div class="list-item__title">暂无试验</div><div class="list-item__meta">先创建一条试验卡片，再去维护材料库与性状口径。</div></div>`;
    return;
  }
  for (const t of trials) {
    const el = document.createElement("div");
    el.className = "list-item";
    el.innerHTML = `
      <div class="list-item__title">${safeText(t.name)}</div>
      <div class="list-item__meta">
        <span class="kv">ID=${safeText(t.id)}</span>
        <span>地点：${safeText(t.location)}</span>
        <span>季节：${safeText(t.season)}</span>
        <span>设计：${safeText(t.design)}</span>
        <span>重复：${safeText(String(t.replicates))}</span>
        <span>创建：${safeText(fmtIsoDateTime(t.created_at))}</span>
      </div>
    `;
    list.appendChild(el);
  }
}

function bindTrialForm() {
  const form = document.getElementById("trial-form");
  const note = document.getElementById("trial-form-note");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    note.textContent = "";
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    payload.replicates = Number(payload.replicates || 3);
    try {
      const created = await api.createTrial(payload);
      note.textContent = `已保存：${created.name}（${created.id}）。下一步：在“材料库”与“性状口径”补齐数据，再到“观测录入”填报。`;
      form.reset();
      await refreshTrialList();
    } catch (err) {
      note.textContent = `保存失败：${String(err?.message || err)}`;
    }
  });
  document.getElementById("trial-refresh").addEventListener("click", refreshTrialList);
  document.getElementById("trial-q").addEventListener("keydown", (e) => {
    if (e.key === "Enter") refreshTrialList();
  });
}

async function bootstrap() {
  bindNav();
  bindModal();
  bindTrialForm();
  await refreshTrialList();
  const fromHash = String(location.hash || "").replace(/^#/, "").trim();
  window.__rkModal = { openModal, closeModal };
  selectView(fromHash && views.some((v) => v.key === fromHash) ? fromHash : "login");
  maybeShowScreenshotModal();
  window.addEventListener("hashchange", () => {
    const key = String(location.hash || "").replace(/^#/, "").trim();
    if (key && views.some((v) => v.key === key)) selectView(key);
    maybeShowScreenshotModal();
  });
  window.addEventListener("popstate", () => maybeShowScreenshotModal());

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const note = document.getElementById("login-note");
      if (note) note.textContent = "演示模式登录完成，已进入系统首页。";
      location.hash = "#home";
    });
  }
}

bootstrap();
