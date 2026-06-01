import { api, clearBanner, el, fmtTs, getAuth, installShotTag, setAuth, showBanner, showTipKind } from "./shared.js";

let currentSessionId = null;
let since = 0;

function renderPolicy(policy) {
  if (!policy) {
    el("policy").textContent = "";
    return;
  }
  const p = policy.capabilities;
  el("policy").textContent = `场景策略：强制同步=${p.force_sync ? "是" : "否"}；学生跳转=${p.student_seek ? "允许" : "禁止"}；倍速=${p.student_speed ? "允许" : "禁止"}；循环=${p.student_loop ? "允许" : "禁止"}`;
}

function pushEvent(evt) {
  const tl = el("timeline");
  const row = document.createElement("div");
  row.className = "evt";
  row.innerHTML = `<div class="dot"></div><div class="c"><div class="ts">${fmtTs(evt.created_at)}</div><div class="msg">${evt.action} · ${evt.summary}</div></div>`;
  tl.prepend(row);
}

async function poll() {
  if (!currentSessionId) return;
  const data = await api(`/sessions/${currentSessionId}/events?since=${since}`);
  data.items.forEach((e) => {
    since = Math.max(since, e.seq);
    pushEvent(e);
  });
  setTimeout(poll, 900);
}

async function follow(sessionId) {
  currentSessionId = sessionId;
  since = 0;
  el("timeline").innerHTML = "";
  const pol = await api(`/sessions/${currentSessionId}/policy`);
  renderPolicy(pol.policy);
  showBanner(`开始跟随：${pol.policy.scene_name}`);
  poll();
}

async function main() {
  installShotTag();
  clearBanner();
  const { user } = getAuth();
  if (user) el("who").textContent = `已登录：${user.name}（${user.role}）`;

  el("btnLogin").onclick = async () => {
    const u = el("u").value.trim();
    const p = el("p").value.trim();
    const data = await api("/login", { method: "POST", body: JSON.stringify({ username: u, password: p }) });
    setAuth(data.token, data.user);
    el("who").textContent = `已登录：${data.user.name}（${data.user.role}）`;
    showBanner(`登录成功：${data.user.role}`);
  };

  el("btnFollow").onclick = async () => {
    const sid = el("sessionId").value.trim();
    if (!sid) return;
    await follow(sid);
  };
}

main().catch((err) => {
  console.error(err);
  showTipKind("warning", "页面初始化失败：" + err.message);
});

