const API = "/api";

export function el(id) {
  return document.getElementById(id);
}

export function qs(sel) {
  return document.querySelector(sel);
}

export function qsa(sel) {
  return Array.from(document.querySelectorAll(sel));
}

export function fmtTs(ms) {
  return new Date(ms).toLocaleTimeString();
}

export function getAuth() {
  const raw = localStorage.getItem("demo_auth");
  if (!raw) return { token: null, user: null };
  try {
    const parsed = JSON.parse(raw);
    return { token: parsed.token || null, user: parsed.user || null };
  } catch {
    return { token: null, user: null };
  }
}

export function setAuth(token, user) {
  localStorage.setItem("demo_auth", JSON.stringify({ token, user }));
}

export function clearAuth() {
  localStorage.removeItem("demo_auth");
}

export async function api(path, opts = {}) {
  const { token } = getAuth();
  const res = await fetch(API + path, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      ...(opts.headers || {}),
      ...(token ? { Authorization: token } : {}),
    },
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || `HTTP ${res.status}`);
  }
  return res.json();
}

export function ensureModal() {
  let shell = document.getElementById("modal");
  if (shell) return shell;
  shell = document.createElement("div");
  shell.id = "modal";
  shell.className = "modal-shell hidden";
  shell.innerHTML = `
    <div class="modal-mask"></div>
    <div class="modal" id="modalBox">
      <div class="modal-title" id="modalTitle">提示</div>
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
    },
  };
  return shell;
}

export function showTipKind(kind, text) {
  ensureModal();
  const shell = document.getElementById("modal");
  if (shell) {
    shell.classList.remove("kind-danger", "kind-warning");
    if (kind === "danger") shell.classList.add("kind-danger");
    if (kind === "warning") shell.classList.add("kind-warning");
  }
  const box = el("modalBox");
  const title = el("modalTitle");
  if (box) {
    box.classList.remove("danger", "warning");
    if (kind) box.classList.add(kind);
  }
  if (title) {
    title.textContent = kind === "danger" ? "确认删除" : kind === "warning" ? "确认操作" : "提示";
  }
  window.__rkModal.open(text);
}

export function showBanner(text) {
  const b = el("banner");
  if (!b) return;
  b.textContent = text;
  b.classList.remove("hidden");
}

export function clearBanner() {
  const b = el("banner");
  if (!b) return;
  b.textContent = "";
  b.classList.add("hidden");
}

export function installShotTag() {
  window.__shotTag = (text) => {
    const t = String(text || "").trim();
    const m = t.match(/^截图(\\d{2})/);
    if (m) {
      document.body.dataset.shot = m[1];
    }
    const b = el("banner");
    if (b) {
      b.className = b.className.replace(/\\btag-\\d{2}\\b/g, "").trim();
      if (m) {
        b.classList.add(`tag-${m[1]}`);
        const pal = {
          "01": { bg: "#ecfeff", primary: "#0891b2" },
          "02": { bg: "#eff6ff", primary: "#2563eb" },
          "03": { bg: "#f0fdf4", primary: "#16a34a" },
          "04": { bg: "#fff7ed", primary: "#ea580c" },
          "05": { bg: "#fdf2f8", primary: "#db2777" },
          "06": { bg: "#f5f3ff", primary: "#7c3aed" },
          "07": { bg: "#fef2f2", primary: "#dc2626" },
          "08": { bg: "#fffbeb", primary: "#d97706" },
          "09": { bg: "#f8fafc", primary: "#334155" },
          "10": { bg: "#f1f5f9", primary: "#0f172a" },
          "11": { bg: "#eef2ff", primary: "#4f46e5" },
          "12": { bg: "#ecfccb", primary: "#65a30d" },
        }[m[1]];
        if (pal) {
          document.documentElement.style.setProperty("--bg", pal.bg);
          document.documentElement.style.setProperty("--primary", pal.primary);
        }
      }
    }
    showBanner(t);
  };
}
