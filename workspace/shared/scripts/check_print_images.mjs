import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const htmlPath = process.argv[2];
if (!htmlPath) {
  console.error("Usage: node check_print_images.mjs <html_path>");
  process.exit(2);
}
if (!fs.existsSync(htmlPath)) {
  console.error(`HTML not found: ${htmlPath}`);
  process.exit(2);
}

const root = process.cwd();
const edgePath = process.env.EDGE_EXECUTABLE_PATH || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

function resolvePlaywrightEntry() {
  const candidates = [];
  let current = path.resolve(root);
  while (true) {
    candidates.push(path.join(current, "node_modules", "playwright", "index.mjs"));
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }
  const hit = candidates.find((candidate) => fs.existsSync(candidate));
  if (!hit) {
    throw new Error("Cannot locate playwright/index.mjs. Install playwright under E:\\copyRight\\workspace\\node_modules.");
  }
  return hit;
}

const playwrightEntry = resolvePlaywrightEntry();
const { chromium } = await import(pathToFileURL(playwrightEntry).href);

const browser = await chromium.launch({ headless: true, executablePath: edgePath });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });

try {
  await page.goto(pathToFileURL(path.resolve(htmlPath)).href, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(800);

  const result = await page.evaluate(() => {
    const imgs = Array.from(document.images || []);
    const problems = [];

    function px(val) {
      const n = Number(String(val).replace("px", "").trim());
      return Number.isFinite(n) ? n : NaN;
    }

    for (const img of imgs) {
      const style = window.getComputedStyle(img);
      const rect = img.getBoundingClientRect();
      const maxH = px(style.maxHeight);
      const fit = (style.objectFit || "").toLowerCase();
      const display = (style.display || "").toLowerCase();
      const visible = rect.width > 1 && rect.height > 1;

      if (!visible) continue;
      if (!Number.isFinite(maxH)) {
        problems.push({ kind: "img_max_height_missing", src: img.getAttribute("src") || "", maxHeight: style.maxHeight });
        continue;
      }
      if (rect.height - maxH > 2) {
        problems.push({ kind: "img_exceeds_max_height", src: img.getAttribute("src") || "", rectH: rect.height, maxH });
      }
      if (fit && fit !== "contain") {
        problems.push({ kind: "img_object_fit_not_contain", src: img.getAttribute("src") || "", objectFit: style.objectFit });
      }
      if (display && display !== "block") {
        // not a hard error; but record for debugging if everything else passes.
      }
    }

    return { imgCount: imgs.length, problems };
  });

  if (result.problems.length) {
    console.error("FAIL: print image layout gate failed.");
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }
  console.log(`PASS: print image layout gate ok (images=${result.imgCount}).`);
} finally {
  await page.close().catch(() => {});
  await browser.close().catch(() => {});
}
