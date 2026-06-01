const API = "/api";

let currentUser = null;
let token = null;
let currentLesson = null;
let currentScene = null;
let currentSession = null;
let currentClip = null;
let since = 0;

function el(id){ return document.getElementById(id); }
function fmtTs(ms){ return new Date(ms).toLocaleTimeString(); }

function showBanner(text){
  const b = el("banner");
  if(!b) return;
  b.textContent = text;
  b.classList.remove("hidden");
}

function clearBanner(){
  const b = el("banner");
  if(!b) return;
  b.textContent = "";
  b.classList.add("hidden");
}

function ensureModal(){
  let shell = document.getElementById("modal");
  if(shell) return shell;
  shell = document.createElement("div");
  shell.id = "modal";
  shell.className = "modal-shell hidden";
  shell.innerHTML = `
    <div class="modal-mask"></div>
    <div class="modal" id="modalBox">
      <div class="modal-title">提示</div>
      <div class="modal-body" id="modalBody"></div>
      <div class="modal-actions">
        <button class="btn" id="modalCancel">取消</button>
        <button class="btn primary" id="modalOk">确定</button>
      </div>
    </div>`;
  document.body.appendChild(shell);
  const close = () => shell.classList.add("hidden");
  el("modalCancel").onclick = close;
  el("modalOk").onclick = close;
  window.__rkModal = {
    closeModal: close,
    open: (text) => {
      el("modalBody").textContent = text;
      shell.classList.remove("hidden");
    }
  };
  return shell;
}

function showTip(text){
  ensureModal();
  window.__rkModal.open(text);
}

function showTipKind(kind, text){
  ensureModal();
  const shell = document.getElementById("modal");
  if(shell){
    shell.classList.remove("kind-danger","kind-warning");
    if(kind === "danger") shell.classList.add("kind-danger");
    if(kind === "warning") shell.classList.add("kind-warning");
  }
  const box = el("modalBox");
  if(box){
    box.classList.remove("danger","warning");
    if(kind) box.classList.add(kind);
  }
  window.__rkModal.open(text);
}

async function api(path, opts={}){
  const res = await fetch(API + path, {
    ...opts,
    headers: {
      "Content-Type":"application/json",
      ...(opts.headers||{}),
      ...(token ? {"Authorization": token} : {}),
    }
  });
  if(!res.ok){
    const t = await res.text();
    throw new Error(t || ("HTTP " + res.status));
  }
  return res.json();
}

async function refreshScenes(){
  const data = await api("/scenes");
  const sel = el("sceneSelect");
  sel.innerHTML = "";
  data.items.forEach(s=>{
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    sel.appendChild(opt);
  });
  currentScene = data.items[0] || null;
  if(currentScene) sel.value = currentScene.id;
  sel.onchange = async () => {
    currentScene = data.items.find(x=>x.id===sel.value) || null;
    await refreshDevices();
  };
  await refreshDevices();
}

async function refreshDevices(){
  const data = await api("/devices" + (currentScene ? ("?scene_id=" + encodeURIComponent(currentScene.id)) : ""));
  const box = el("devices");
  box.innerHTML = "";
  data.items.forEach(d=>{
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

async function refreshLessons(){
  const data = await api("/lessons");
  const sel = el("lessonSelect");
  sel.innerHTML = "";
  data.items.forEach(l=>{
    const opt = document.createElement("option");
    opt.value = l.id;
    opt.textContent = l.title + "（" + l.scene_name + "）";
    sel.appendChild(opt);
  });
  currentLesson = data.items[0] || null;
  if(currentLesson) sel.value = currentLesson.id;
  sel.onchange = async () => {
    currentLesson = data.items.find(x=>x.id===sel.value) || null;
    await refreshClips();
  };
  await refreshClips();
}

async function refreshClips(){
  const box = el("clips");
  box.innerHTML = "";
  currentClip = null;
  if(!currentLesson) return;
  const data = await api(`/lessons/${currentLesson.id}/clips`);
  data.items.forEach(c=>{
    const d = document.createElement("div");
    d.className = "clip";
    d.innerHTML = `<div class="t">${c.label}</div><div class="m">${(c.end_ms-c.start_ms)/1000}s · 默认倍速 ${c.default_speed}x</div>`;
    d.onclick = () => {
      currentClip = c;
      document.querySelectorAll(".clip").forEach(x=>x.classList.remove("active"));
      d.classList.add("active");
      showBanner(`已选择片段：${c.label}`);
    };
    box.appendChild(d);
  });
}

function renderPolicy(policy){
  if(!policy){ el("policy").textContent = ""; return; }
  const p = policy.capabilities;
  el("policy").textContent = `场景策略：强制同步=${p.force_sync ? "是":"否"}；学生跳转=${p.student_seek ? "允许":"禁止"}；倍速=${p.student_speed ? "允许":"禁止"}；循环=${p.student_loop ? "允许":"禁止"}`;
}

function pushEvent(evt){
  const tl = el("timeline");
  const row = document.createElement("div");
  row.className = "evt";
  row.innerHTML = `<div class="dot"></div><div class="c"><div class="ts">${fmtTs(evt.created_at)}</div><div class="msg">${evt.action} · ${evt.summary}</div></div>`;
  tl.prepend(row);
}

async function pollEvents(){
  if(!currentSession) return;
  const data = await api(`/sessions/${currentSession.id}/events?since=${since}`);
  data.items.forEach(e=>{
    since = Math.max(since, e.seq);
    pushEvent(e);
  });
  setTimeout(pollEvents, 1200);
}

async function ensureSessionPolicy(){
  if(!currentSession) return;
  const data = await api(`/sessions/${currentSession.id}/policy`);
  renderPolicy(data.policy);
}

async function main(){
  await refreshScenes();
  await refreshLessons();
  clearBanner();

  window.__shotTag = (text) => {
    const t = String(text || "").trim();
    const b = el("banner");
    if(b){
      b.className = b.className.replace(/\btag-\d{2}\b/g, "").trim();
      const m = t.match(/^截图(\\d{2})/);
      if(m){
        b.classList.add(`tag-${m[1]}`);
      }
    }
    showBanner(t);
  };

  el("btnLogin").onclick = async () => {
    const u = el("u").value.trim();
    const p = el("p").value.trim();
    const data = await api("/login", {method:"POST", body:JSON.stringify({username:u, password:p})});
    token = data.token;
    currentUser = data.user;
    el("who").textContent = `已登录：${currentUser.name}（${currentUser.role}）`;
    showBanner(`登录成功：${currentUser.role}（用于截图与演示）`);
  };

  el("btnAddLesson").onclick = async () => {
    if(!currentUser || currentUser.role!=="teacher"){
      alert("请先用 teacher 登录创建课时");
      return;
    }
    const title = "Unit " + (Math.floor(Math.random()*6)+1) + " 听力训练";
    const sceneId = el("sceneSelect").value;
    const data = await api("/lessons", {method:"POST", body:JSON.stringify({title, scene_id:sceneId, teacher_id: currentUser.id, book_unit:"Demo"})});
    currentLesson = data.item;
    await refreshLessons();
    showBanner(`已新增课时：${currentLesson.title}`);
  };

  el("btnEditLesson").onclick = async () => {
    if(!currentLesson){ alert("请选择课时"); return; }
    showTip("演示版：编辑课时仅展示按钮与流程入口");
  };

  el("btnDeleteLesson").onclick = async () => {
    if(!currentLesson){ alert("请选择课时"); return; }
    showTipKind("danger","演示版：删除课时确认（演示）");
  };

  el("btnStart").onclick = async () => {
    if(!currentUser || currentUser.role!=="teacher"){
      alert("请先用 teacher 登录开始上课");
      return;
    }
    if(!currentLesson){ alert("请选择课时"); return; }
    const data = await api(`/lessons/${currentLesson.id}/start`, {method:"POST", body:JSON.stringify({})});
    currentSession = data.session;
    since = 0;
    el("timeline").innerHTML = "";
    await ensureSessionPolicy();
    pollEvents();
    showBanner(`课堂已开始：session=${currentSession.id}`);
  };

  function requireClip(){
    if(!currentClip){ alert("请选择片段"); return false; }
    if(!currentSession){ alert("请先开始上课"); return false; }
    if(!currentUser){ alert("请先登录"); return false; }
    return true;
  }

  el("btnPlay").onclick = async () => {
    if(!requireClip()) return;
    await api(`/sessions/${currentSession.id}/event`, {method:"POST", body:JSON.stringify({
      action:"play", actor_user_id: currentUser.id, target:"all_students",
      payload:{clip_id: currentClip.id, label: currentClip.label}
    })});
  };
  el("btnPause").onclick = async () => {
    if(!currentSession || !currentUser) return;
    await api(`/sessions/${currentSession.id}/event`, {method:"POST", body:JSON.stringify({action:"pause", actor_user_id: currentUser.id, target:"all_students", payload:{}})});
  };
  el("btnLoop").onclick = async () => {
    if(!requireClip()) return;
    await api(`/sessions/${currentSession.id}/event`, {method:"POST", body:JSON.stringify({action:"ab_loop", actor_user_id: currentUser.id, target:"all_students", payload:{clip_id: currentClip.id, a_ms: currentClip.start_ms, b_ms: currentClip.end_ms}})});
  };
  el("btnSpeed").onclick = async () => {
    if(!requireClip()) return;
    await api(`/sessions/${currentSession.id}/event`, {method:"POST", body:JSON.stringify({action:"speed", actor_user_id: currentUser.id, target:"all_students", payload:{clip_id: currentClip.id, speed: 1.2}})});
  };

  el("btnAddClip").onclick = async () => {
    if(!currentLesson){ alert("请选择课时"); return; }
    showTip("演示版：新增片段入口（可扩展为表单）");
  };
  el("btnEditClip").onclick = async () => {
    if(!currentClip){ alert("请选择片段"); return; }
    showTip("演示版：编辑片段入口（可扩展为表单）");
  };
  el("btnDeleteClip").onclick = async () => {
    if(!currentClip){ alert("请选择片段"); return; }
    showTipKind("warning","演示版：删除片段确认（演示）");
  };
}

main().catch(err=>{
  console.error(err);
  alert("页面初始化失败：" + err.message);
});
