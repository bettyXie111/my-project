import { api } from "./api.js";
import { safeText, fmtBadge } from "./format.js";

function render(container) {
  container.innerHTML = `
    <div class="panel__head">
      <h2>综合评价</h2>
      <div class="panel__hint">综合分=标准分×权重。每次计算都会写入“操作追溯”。</div>
    </div>
    <div class="grid">
      <div class="card">
        <div class="card__title">计算评分</div>
        <div class="card__body">
          <form id="score-form" class="form">
            <label>试验ID<input name="trial_id" placeholder="从试验卡片复制" required /></label>
            <label>评分模板ID<input name="profile_id" placeholder="可留空：默认等权" /></label>
            <button type="submit" class="btn primary">计算</button>
          </form>
          <div class="note" id="score-note"></div>
        </div>
      </div>
      <div class="card">
        <div class="card__title">排名</div>
        <div class="card__body">
          <div id="score-list" class="list"></div>
        </div>
      </div>
    </div>
  `;
}

function rankBadge(i) {
  if (i === 0) return fmtBadge("1", "ok");
  if (i === 1) return fmtBadge("2", "warn");
  if (i === 2) return fmtBadge("3", "warn");
  return fmtBadge(String(i + 1), "ok");
}

function explainLine(item) {
  const keys = Object.keys(item.trait_scores || {});
  if (!keys.length) return "无性状分解：可能缺失观测数据。";
  const parts = keys
    .slice(0, 6)
    .map((k) => `${k}:${Number(item.trait_scores[k]).toFixed(1)}`)
    .join("，");
  return parts + (keys.length > 6 ? "…" : "");
}

async function run(container, trialId, profileId) {
  const list = container.querySelector("#score-list");
  list.innerHTML = "";
  const items = await api.trialScores(trialId, profileId);
  if (!items.length) {
    list.innerHTML = `<div class="list-item"><div class="list-item__title">暂无评分结果</div><div class="list-item__meta">需要至少 1 个材料、1 个性状与 1 条观测记录。</div></div>`;
    return;
  }
  items.forEach((s, idx) => {
    const el = document.createElement("div");
    el.className = "list-item";
    el.innerHTML = `
      <div class="list-item__title">${rankBadge(idx)} ${safeText(s.variety_name)} · ${safeText(String(s.total_score.toFixed(2)))}</div>
      <div class="list-item__meta">
        <span class="kv">var=${safeText(s.variety_id)}</span>
        <span class="kv">trial=${safeText(s.trial_id)}</span>
      </div>
      <div class="list-item__meta">${safeText(explainLine(s))}</div>
      <div class="list-item__meta">${safeText(s.explain || "")}</div>
    `;
    list.appendChild(el);
  });
}

function bind(container) {
  const form = container.querySelector("#score-form");
  const note = container.querySelector("#score-note");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    note.textContent = "";
    const fd = new FormData(form);
    const trialId = String(fd.get("trial_id") || "").trim();
    const profileId = String(fd.get("profile_id") || "").trim();
    try {
      await run(container, trialId, profileId);
      note.textContent = "已计算。建议去“操作追溯”查看本次计算记录。";
    } catch (err) {
      note.textContent = `计算失败：${String(err?.message || err)}`;
    }
  });
}

export function mountScoring(container) {
  render(container);
  bind(container);
}

