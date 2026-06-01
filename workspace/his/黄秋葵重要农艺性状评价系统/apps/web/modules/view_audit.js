import { api } from "./api.js";
import { fmtIsoDateTime, safeText, fmtBadge } from "./format.js";

function render(container) {
  container.innerHTML = `
    <div class="panel__head">
      <h2>操作追溯</h2>
      <div class="panel__hint">把“创建、修改、评分计算”写成可审计事件，便于复核材料来源。</div>
    </div>
    <div class="card">
      <div class="card__title">最近事件</div>
      <div class="card__body">
        <div class="toolbar">
          <input id="audit-limit" type="number" min="1" max="1000" value="200" />
          <button class="btn" id="audit-refresh">刷新</button>
        </div>
        <div id="audit-list" class="list"></div>
      </div>
    </div>
  `;
}

function actionBadge(action) {
  const a = String(action || "");
  if (a.includes("create")) return fmtBadge("创建", "ok");
  if (a.includes("update")) return fmtBadge("修改", "warn");
  if (a.includes("calculate")) return fmtBadge("评分", "ok");
  return fmtBadge("事件", "ok");
}

async function refresh(container) {
  const limit = Number(container.querySelector("#audit-limit").value || 200);
  const list = container.querySelector("#audit-list");
  list.innerHTML = "";
  const items = await api.listAudit(limit);
  if (!items.length) {
    list.innerHTML = `<div class="list-item"><div class="list-item__title">暂无事件</div><div class="list-item__meta">当你创建材料、性状、试验或计算评分时，这里会留下记录。</div></div>`;
    return;
  }
  for (const it of items) {
    const el = document.createElement("div");
    el.className = "list-item";
    const payloadPreview = safeText(JSON.stringify(it.payload || {}, null, 0)).slice(0, 180);
    el.innerHTML = `
      <div class="list-item__title">${actionBadge(it.action)} ${safeText(it.action)}</div>
      <div class="list-item__meta">
        <span class="kv">ID=${safeText(it.id)}</span>
        <span>时间：${safeText(fmtIsoDateTime(it.created_at))}</span>
      </div>
      <div class="list-item__meta"><span class="kv">${payloadPreview}</span></div>
    `;
    list.appendChild(el);
  }
}

function bind(container) {
  container.querySelector("#audit-refresh").addEventListener("click", () => refresh(container));
}

export function mountAudit(container) {
  render(container);
  bind(container);
  refresh(container);
}

