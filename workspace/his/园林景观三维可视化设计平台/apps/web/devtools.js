function pretty(obj) {
  if (typeof obj === "string") return obj;
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

async function fetchText(path) {
  const res = await fetch(path);
  const ct = res.headers.get("content-type") || "";
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (ct.includes("application/json")) return pretty(await res.json());
  return await res.text();
}

function setOut(text) {
  const out = document.getElementById("out");
  if (!out) return;
  out.textContent = text;
}

async function bind() {
  const map = {
    "btn-health": "/api/health",
    "btn-report": "/api/report",
    "btn-manifest": "/api/web/manifest",
  };
  for (const [id, path] of Object.entries(map)) {
    document.getElementById(id)?.addEventListener("click", async () => {
      setOut(`请求中：${path}`);
      try {
        const text = await fetchText(path);
        setOut(text);
      } catch (e) {
        setOut(`请求失败：${path}\n${String(e)}`);
      }
    });
  }
}

window.addEventListener("DOMContentLoaded", bind);

