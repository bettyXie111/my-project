import { api, clearBanner, el, getAuth, installShotTag, setAuth, showBanner, showTipKind } from "./shared.js";

let scenes = [];
let currentScene = null;

function loadPolicyToForm(scene) {
  const c = scene.capabilities || {};
  el("c_force_sync").checked = !!c.force_sync;
  el("c_student_seek").checked = !!c.student_seek;
  el("c_student_speed").checked = !!c.student_speed;
  el("c_student_loop").checked = !!c.student_loop;
}

function formPolicy() {
  return {
    force_sync: el("c_force_sync").checked,
    student_seek: el("c_student_seek").checked,
    student_speed: el("c_student_speed").checked,
    student_loop: el("c_student_loop").checked,
  };
}

async function refreshScenes() {
  const data = await api("/scenes");
  scenes = data.items;
  const sel = el("sceneSelect");
  sel.innerHTML = "";
  scenes.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.id;
    opt.textContent = s.name;
    sel.appendChild(opt);
  });
  currentScene = scenes[0] || null;
  if (currentScene) sel.value = currentScene.id;
  sel.onchange = async () => {
    currentScene = scenes.find((x) => x.id === sel.value) || null;
    if (currentScene) loadPolicyToForm(currentScene);
    await refreshDevices();
  };
  if (currentScene) loadPolicyToForm(currentScene);
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

async function main() {
  installShotTag();
  clearBanner();
  const { user } = getAuth();
  if (user) el("who").textContent = `已登录：${user.name}（${user.role}）`;

  await refreshScenes();

  el("btnLogin").onclick = async () => {
    const u = el("u").value.trim();
    const p = el("p").value.trim();
    const data = await api("/login", { method: "POST", body: JSON.stringify({ username: u, password: p }) });
    setAuth(data.token, data.user);
    el("who").textContent = `已登录：${data.user.name}（${data.user.role}）`;
    showBanner(`登录成功：${data.user.role}`);
  };

  el("btnSave").onclick = async () => {
    if (!currentScene) return;
    const payload = { capabilities: formPolicy() };
    const data = await api(`/scenes/${currentScene.id}`, { method: "PATCH", body: JSON.stringify(payload) });
    scenes = scenes.map((x) => (x.id === data.item.id ? data.item : x));
    currentScene = data.item;
    loadPolicyToForm(currentScene);
    showBanner(`已保存策略：${currentScene.name}`);
  };
}

main().catch((err) => {
  console.error(err);
  showTipKind("warning", "页面初始化失败：" + err.message);
});

