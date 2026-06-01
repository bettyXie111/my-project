import { api } from "./api.js";
import { safeText, fmtBadge } from "./format.js";

function render(container) {
  container.innerHTML = `
    <div class="panel__head">
      <h2>观测录入</h2>
      <div class="panel__hint">按“小区-日期-性状”录入。超范围不会强拦截，但会写入备注提示，便于复核。</div>
    </div>
    <div class="grid">
      <div class="card">
        <div class="card__title">录入观测</div>
        <div class="card__body">
          <form id="obs-form" class="form">
            <label>试验ID<input name="trial_id" placeholder="从试验卡片复制" required /></label>
            <label>小区ID<input name="plot_id" placeholder="从试验详情复制" required /></label>
            <label>性状ID<input name="trait_id" placeholder="从性状口径复制" required /></label>
            <label>观测日期<input name="observed_at" type="date" required /></label>
            <label>数值<input name="value" type="number" step="0.01" required /></label>
            <label>记录员<input name="operator" placeholder="可留空" /></label>
            <label>备注<input name="note" placeholder="如：雨后补测/虫咬影响" /></label>
            <button type="submit" class="btn primary">提交</button>
          </form>
          <div class="note" id="obs-note"></div>
        </div>
      </div>
      <div class="card">
        <div class="card__title">观测列表</div>
        <div class="card__body">
          <div class="toolbar">
            <input id="obs-trial" placeholder="trial_id 过滤" />
            <input id="obs-plot" placeholder="plot_id 过滤" />
            <button class="btn" id="obs-refresh">刷新</button>
          </div>
          <div id="obs-list" class="list"></div>
        </div>
      </div>
    </div>
  `;
}

function statusBadge(status) {
  const s = String(status || "").toLowerCase();
  if (s === "approved") return fmtBadge("已批准", "ok");
  if (s === "rejected") return fmtBadge("已退回", "bad");
  if (s === "draft") return fmtBadge("草稿", "warn");
  return fmtBadge("已提交", "ok");
}

async function refresh(container) {
  const trial = container.querySelector("#obs-trial").value.trim();
  const plot = container.querySelector("#obs-plot").value.trim();
  const list = container.querySelector("#obs-list");
  list.innerHTML = "";
  const items = await api.listObservations({ trial_id: trial, plot_id: plot });
  if (!items.length) {
    list.innerHTML = `<div class="list-item"><div class="list-item__title">暂无观测记录</div><div class="list-item__meta">建议先在 API 冒烟测试里走一条完整链路，或手动录入 10~20 条记录用于评分对比。</div></div>`;
    return;
  }
  for (const o of items) {
    const el = document.createElement("div");
    el.className = "list-item";
    el.innerHTML = `
      <div class="list-item__title">${statusBadge(o.status)} ${safeText(o.observed_at)} · ${safeText(String(o.value))}</div>
      <div class="list-item__meta">
        <span class="kv">obs=${safeText(o.id)}</span>
        <span class="kv">plot=${safeText(o.plot_id)}</span>
        <span class="kv">trait=${safeText(o.trait_id)}</span>
        <span>${safeText(o.operator || "")}</span>
      </div>
      <div class="list-item__meta">${safeText(o.note || "")}</div>
    `;
    list.appendChild(el);
  }
}

function bind(container) {
  const form = container.querySelector("#obs-form");
  const note = container.querySelector("#obs-note");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    note.textContent = "";
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    payload.value = Number(payload.value);
    delete payload.trial_id;
    try {
      await api.createObservation(payload);
      form.reset();
      await refresh(container);
      note.textContent = "已提交观测记录。";
    } catch (err) {
      note.textContent = `提交失败：${String(err?.message || err)}`;
    }
  });
  container.querySelector("#obs-refresh").addEventListener("click", () => refresh(container));
}

export function mountObservations(container) {
  render(container);
  bind(container);
  refresh(container);
}

