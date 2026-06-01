import { api } from "./api.js";
import { safeText } from "./format.js";

function render(container) {
  container.innerHTML = `
    <div class="panel__head">
      <h2>材料库</h2>
      <div class="panel__hint">记录材料来源与备注；不把“评分口径”写在备注里。</div>
    </div>
    <div class="grid">
      <div class="card">
        <div class="card__title">新增材料</div>
        <div class="card__body">
          <div class="toolbar" style="margin-bottom:10px;justify-content:flex-start;">
            <button class="btn" type="button" data-demo-action="create">新增</button>
            <button class="btn" type="button" data-demo-action="edit">编辑</button>
            <button class="btn" type="button" data-demo-action="view">查看</button>
            <button class="btn" type="button" data-demo-action="delete">删除</button>
          </div>
          <form id="var-form" class="form">
            <label>材料名称<input name="name" placeholder="如：鲁葵-2号" required /></label>
            <label>来源/单位<input name="source" placeholder="如：江苏某育种团队" /></label>
            <label>类型<select name="type">
              <option value="品种">品种</option>
              <option value="杂交组合">杂交组合</option>
              <option value="系谱材料">系谱材料</option>
            </select></label>
            <label>备注<input name="remark" placeholder="如：早熟、抗病观察中" /></label>
            <button type="submit" class="btn primary">保存</button>
          </form>
          <div class="note" id="var-note"></div>
        </div>
      </div>
      <div class="card">
        <div class="card__title">材料列表</div>
        <div class="card__body">
          <div class="toolbar">
            <input id="var-q" placeholder="按名称搜索" />
            <button class="btn" id="var-refresh">刷新</button>
          </div>
          <div id="var-list" class="list"></div>
        </div>
      </div>
    </div>
  `;
}

async function refresh(container) {
  const q = container.querySelector("#var-q").value.trim();
  const list = container.querySelector("#var-list");
  list.innerHTML = "";
  const items = await api.listVarieties(q);
  if (!items.length) {
    list.innerHTML = `<div class="list-item"><div class="list-item__title">暂无材料</div><div class="list-item__meta">可以先录入 2~3 个材料用于演示综合评价。</div></div>`;
    return;
  }
  for (const v of items) {
    const el = document.createElement("div");
    el.className = "list-item";
    el.innerHTML = `
      <div class="list-item__title">${safeText(v.name)}</div>
      <div class="list-item__meta">
        <span class="kv">ID=${safeText(v.id)}</span>
        <span>来源：${safeText(v.source || "-")}</span>
        <span>类型：${safeText(v.type || "-")}</span>
      </div>
      <div class="list-item__meta">${safeText(v.remark || "")}</div>
    `;
    list.appendChild(el);
  }
}

function bind(container) {
  const form = container.querySelector("#var-form");
  const note = container.querySelector("#var-note");
  for (const btn of container.querySelectorAll("[data-demo-action]")) {
    btn.addEventListener("click", () => {
      const action = btn.dataset.demoAction;
      const titleMap = { create: "新增材料", edit: "编辑材料", view: "查看材料", delete: "删除确认" };
      const title = titleMap[action] || "窗口";
      const html = `
        <div class="modal__kvs">
          <div class="kvrow"><div class="k">action</div><div class="v">${safeText(action)}</div></div>
          <div class="kvrow"><div class="k">提示</div><div class="v">本弹窗用于截图演示按钮交互，真实业务以表单保存为准。</div></div>
        </div>
      `;
      window.__rkModal?.openModal?.(title, html);
    });
  }
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    note.textContent = "";
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    try {
      await api.createVariety(payload);
      form.reset();
      await refresh(container);
      note.textContent = "已保存。";
    } catch (err) {
      note.textContent = `保存失败：${String(err?.message || err)}`;
    }
  });
  container.querySelector("#var-refresh").addEventListener("click", () => refresh(container));
  container.querySelector("#var-q").addEventListener("keydown", (e) => {
    if (e.key === "Enter") refresh(container);
  });
}

export function mountVarieties(container) {
  render(container);
  bind(container);
  refresh(container);
}
