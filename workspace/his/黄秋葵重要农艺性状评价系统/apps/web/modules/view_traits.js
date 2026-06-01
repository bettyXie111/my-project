import { api } from "./api.js";
import { safeText, fmtBadge } from "./format.js";

const directions = [
  { value: "higher_is_better", label: "越大越好" },
  { value: "lower_is_better", label: "越小越好" },
  { value: "target_range", label: "目标区间最佳" },
];

function render(container) {
  container.innerHTML = `
    <div class="panel__head">
      <h2>性状口径</h2>
      <div class="panel__hint">把“测定方法、单位、范围、方向性”写清楚，后续评分才可复核。</div>
    </div>
    <div class="grid">
      <div class="card">
        <div class="card__title">新增性状</div>
        <div class="card__body">
          <form id="trait-form" class="form">
            <label>编码<input name="code" placeholder="如：PH/DF/YPP" required /></label>
            <label>名称<input name="name" placeholder="如：株高/始花期" required /></label>
            <label>单位<input name="unit" placeholder="如：cm/d/个" /></label>
            <label>方向性<select name="direction">${directions
              .map((d) => `<option value="${d.value}">${d.label}</option>`)
              .join("")}</select></label>
            <label>合理最小值<input name="min_value" type="number" step="0.01" placeholder="可留空" /></label>
            <label>合理最大值<input name="max_value" type="number" step="0.01" placeholder="可留空" /></label>
            <label>测定方法<input name="method" placeholder="一句话说明口径" /></label>
            <button type="submit" class="btn primary">保存</button>
          </form>
          <div class="note" id="trait-note"></div>
        </div>
      </div>
      <div class="card">
        <div class="card__title">性状列表</div>
        <div class="card__body">
          <div class="toolbar">
            <input id="trait-q" placeholder="按名称/编码搜索" />
            <button class="btn" id="trait-refresh">刷新</button>
          </div>
          <div id="trait-list" class="list"></div>
        </div>
      </div>
    </div>
  `;
}

function dirLabel(value) {
  const found = directions.find((d) => d.value === value);
  return found ? found.label : value;
}

async function refresh(container) {
  const q = container.querySelector("#trait-q").value.trim();
  const list = container.querySelector("#trait-list");
  list.innerHTML = "";
  const items = await api.listTraits(q);
  if (!items.length) {
    list.innerHTML = `<div class="list-item"><div class="list-item__title">暂无性状</div><div class="list-item__meta">建议先录入 6~10 个性状：株高、始花期、单株结荚数、商品荚比例、单荚重、病害等级等。</div></div>`;
    return;
  }
  for (const t of items) {
    const range = [
      t.min_value === null || t.min_value === undefined ? "" : `min=${t.min_value}`,
      t.max_value === null || t.max_value === undefined ? "" : `max=${t.max_value}`,
    ]
      .filter(Boolean)
      .join(", ");
    const badge = t.direction === "higher_is_better" ? fmtBadge("↑", "ok") : t.direction === "lower_is_better" ? fmtBadge("↓", "warn") : fmtBadge("◎", "ok");
    const el = document.createElement("div");
    el.className = "list-item";
    el.innerHTML = `
      <div class="list-item__title">${badge} ${safeText(t.code)} · ${safeText(t.name)}</div>
      <div class="list-item__meta">
        <span>单位：${safeText(t.unit || "-")}</span>
        <span>方向：${safeText(dirLabel(t.direction))}</span>
        <span>${safeText(range || "范围未设置")}</span>
      </div>
      <div class="list-item__meta">${safeText(t.method || "")}</div>
      <div class="list-item__meta"><span class="kv">ID=${safeText(t.id)}</span></div>
    `;
    list.appendChild(el);
  }
}

function bind(container) {
  const form = container.querySelector("#trait-form");
  const note = container.querySelector("#trait-note");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    note.textContent = "";
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    for (const key of ["min_value", "max_value"]) {
      if (payload[key] === "") delete payload[key];
      else payload[key] = Number(payload[key]);
    }
    try {
      await api.createTrait(payload);
      form.reset();
      await refresh(container);
      note.textContent = "已保存。";
    } catch (err) {
      note.textContent = `保存失败：${String(err?.message || err)}`;
    }
  });
  container.querySelector("#trait-refresh").addEventListener("click", () => refresh(container));
  container.querySelector("#trait-q").addEventListener("keydown", (e) => {
    if (e.key === "Enter") refresh(container);
  });
}

export function mountTraits(container) {
  render(container);
  bind(container);
  refresh(container);
}

