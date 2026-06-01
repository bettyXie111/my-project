export function safeText(text) {
  return String(text ?? "").replace(/[&<>"']/g, (ch) => {
    const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
    return map[ch] || ch;
  });
}

export function fmtIsoDateTime(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function fmtBadge(label, tone) {
  const color = tone === "ok" ? "rgba(108,192,111,0.18)" : tone === "warn" ? "rgba(231,185,92,0.18)" : "rgba(229,124,124,0.18)";
  const border = tone === "ok" ? "rgba(108,192,111,0.45)" : tone === "warn" ? "rgba(231,185,92,0.45)" : "rgba(229,124,124,0.45)";
  return `<span style="padding:3px 8px;border-radius:999px;border:1px solid ${border};background:${color};font-size:12px;">${safeText(label)}</span>`;
}

