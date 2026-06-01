import { api, clearBanner, clearAuth, el, getAuth, installShotTag, qsa, setAuth, showBanner, showTipKind, fmtTs } from "./shared.js";

let currentLesson = null;
let currentScene = null;
let currentSession = null;
let currentClip = null;
let since = 0;

async function refreshScenes() {
  const data = await api("/scenes");
  const sel = el("sceneSelect");
  sel.innerHTML = "";
  data.items.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    sel.appendChild(opt);
  });
  currentScene = data.items[0] || null;
  if (currentScene) sel.value = currentScene.id;
  sel.onchange = async () => {
    currentScene = data.items.find((x) => x.id === sel.value) || null;
    showBanner(`已切换场景：${currentScene ? currentScene.name : "-"}`);
    await refreshDevices();
  };
  await refreshDevices();
}

async function refreshDevices() {
  const data = await api("/devices" + (currentScene ? `?scene_id=${encodeURIComponent(currentScene.id)}` : ""));
  const box = el("devices");
  box.innerHTML = "";
  data.items.forEach((d) => {
    const row = document.createElement("div");
    row.className = "device";
    row.innerHTML = `<div><div style="font-weight:600">${d.name}</div><div style="color:var(--muted);font-size:12px">${d.type}</div></div>`;
    const b = document.createElement("div");
    b.className = "badge " + (d.online ? "on" : "off");
    b.textContent = d.online ? "在线" : "离线";
    row.appendChild(b);
    box.appendChild(row);
  });
}

async function refreshLessons() {
  const data = await api("/lessons");
  const sel = el("lessonSelect");
  sel.innerHTML = "";
  data.items.forEach((l) => {
    const opt = document.createElement("option");
    opt.value = l.id;
    opt.textContent = `${l.title}（${l.scene_name}）`;
    sel.appendChild(opt);
  });
  currentLesson = data.items[0] || null;
  if (currentLesson) sel.value = currentLesson.id;
  sel.onchange = async () => {
    currentLesson = data.items.find((x) => x.id === sel.value) || null;
    showBanner(`已选择课时：${currentLesson ? currentLesson.title : "-"}`);
    await refreshClips();
  };
  await refreshClips();
}

async function refreshClips() {
  const box = el("clips");
  box.innerHTML = "";
  currentClip = null;
  if (!currentLesson) return;
  const data = await api(`/lessons/${currentLesson.id}/clips`);
  data.items.forEach((c) => {
    const d = document.createElement("div");
    d.className = "clip";
    d.innerHTML = `<div class="t">${c.label}</div><div class="m">${(c.end_ms - c.start_ms) / 1000}s · 默认倍速 ${c.default_speed}x</div>`;
    d.onclick = () => {
      currentClip = c;
      qsa(".clip").forEach((x) => x.classList.remove("active"));
      d.classList.add("active");
      showBanner(`已选择片段：${c.label}`);
    };
    box.appendChild(d);
  });
}

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

async function pollEvents() {
  if (!currentSession) return;
  const data = await api(`/sessions/${currentSession.id}/events?since=${since}`);
  data.items.forEach((e) => {
    since = Math.max(since, e.seq);
    pushEvent(e);
  });
  setTimeout(pollEvents, 900);
}

async function ensureSessionPolicy() {
  if (!currentSession) return;
  const data = await api(`/sessions/${currentSession.id}/policy`);
  renderPolicy(data.policy);
}

function requireTeacher() {
  const { user } = getAuth();
  if (!user || user.role !== "teacher") {
    showTipKind("warning", "请先用 teacher 登录。");
    return false;
  }
  return true;
}

function requireClip() {
  if (!requireTeacher()) return false;
  if (!currentSession) {
    showTipKind("warning", "请先开始上课。");
    return false;
  }
  if (!currentClip) {
    showTipKind("warning", "请选择片段。");
    return false;
  }
  return true;
}

async function main() {
  installShotTag();
  clearBanner();
  const { user } = getAuth();
  if (user) el("who").textContent = `已登录：${user.name}（${user.role}）`;

  await refreshScenes();
  await refreshLessons();

  el("btnLogin").onclick = async () => {
    const u = el("u").value.trim();
    const p = el("p").value.trim();
    const data = await api("/login", { method: "POST", body: JSON.stringify({ username: u, password: p }) });
    setAuth(data.token, data.user);
    el("who").textContent = `已登录：${data.user.name}（${data.user.role}）`;
    showBanner(`登录成功：${data.user.role}`);
  };

  el("btnAddLesson").onclick = async () => {
    if (!requireTeacher()) return;
    const title = `Unit ${(Math.floor(Math.random() * 6) + 1)} 听力训练`;
    const sceneId = el("sceneSelect").value;
    const data = await api("/lessons", { method: "POST", body: JSON.stringify({ title, scene_id: sceneId, teacher_id: "u_teacher", book_unit: "Demo" }) });
    currentLesson = data.item;
    await refreshLessons();
    showBanner(`已新增课时：${currentLesson.title}`);
  };

  el("btnEditLesson").onclick = async () => showTipKind("warning", "演示版：编辑课时入口（可扩展为表单）。");
  el("btnDeleteLesson").onclick = async () => showTipKind("danger", "演示版：删除课时确认（示例）。");

  el("btnStart").onclick = async () => {
    if (!requireTeacher()) return;
    if (!currentLesson) return;
    const data = await api(`/lessons/${currentLesson.id}/start`, { method: "POST", body: JSON.stringify({}) });
    currentSession = data.session;
    since = 0;
    el("timeline").innerHTML = "";
    await ensureSessionPolicy();
    pollEvents();
    showBanner(`课堂已开始：session=${currentSession.id}`);
  };

  el("btnEnd").onclick = async () => {
    if (!requireTeacher()) return;
    if (!currentSession) return;
    await api(`/sessions/${currentSession.id}/end`, { method: "POST", body: JSON.stringify({}) });
    showBanner("已结束上课");
    currentSession = null;
  };

  el("btnPlay").onclick = async () => {
    if (!requireClip()) return;
    await api(`/sessions/${currentSession.id}/event`, { method: "POST", body: JSON.stringify({ action: "play", actor_user_id: "u_teacher", target: "all_students", payload: { clip_id: currentClip.id, label: currentClip.label } }) });
  };
  el("btnPause").onclick = async () => {
    if (!requireTeacher() || !currentSession) return;
    await api(`/sessions/${currentSession.id}/event`, { method: "POST", body: JSON.stringify({ action: "pause", actor_user_id: "u_teacher", target: "all_students", payload: {} }) });
  };
  el("btnLoop").onclick = async () => {
    if (!requireClip()) return;
    await api(`/sessions/${currentSession.id}/event`, { method: "POST", body: JSON.stringify({ action: "ab_loop", actor_user_id: "u_teacher", target: "all_students", payload: { clip_id: currentClip.id, a_ms: currentClip.start_ms, b_ms: currentClip.end_ms } }) });
  };
  el("btnSpeed").onclick = async () => {
    if (!requireClip()) return;
    await api(`/sessions/${currentSession.id}/event`, { method: "POST", body: JSON.stringify({ action: "speed", actor_user_id: "u_teacher", target: "all_students", payload: { clip_id: currentClip.id, speed: 1.2 } }) });
  };

  el("btnAddClip").onclick = async () => showTipKind("warning", "演示版：新增片段入口（可扩展为表单）。");
  el("btnEditClip").onclick = async () => showTipKind("warning", "演示版：编辑片段入口（可扩展为表单）。");
  el("btnDeleteClip").onclick = async () => showTipKind("warning", "演示版：删除片段确认（示例）。");
}

main().catch((err) => {
  console.error(err);
  showTipKind("warning", "页面初始化失败：" + err.message);
});

