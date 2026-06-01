import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const root = process.cwd();
const outDir = process.env.SCREENSHOT_OUT_DIR
  ? path.resolve(process.env.SCREENSHOT_OUT_DIR)
  : path.join(root, "images");
const baseUrl = process.env.SCREENSHOT_BASE_URL || "http://127.0.0.1:8010";
const edgePath = process.env.EDGE_EXECUTABLE_PATH || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

fs.mkdirSync(outDir, { recursive: true });

async function login(page, username = "admin", password = "admin123") {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(900);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click("#login-form button[type='submit']");
  await page.waitForTimeout(1500);
}

async function captureRoute(page, hash, filename) {
  await page.goto(`${baseUrl}/#${hash}`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1400);
  await page.screenshot({ path: path.join(outDir, filename), fullPage: true });
}

async function run() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: edgePath,
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 980 } });
  try {
    await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outDir, "fig-1-1-login-full.png"), fullPage: true });
    await login(page);
    await page.screenshot({ path: path.join(outDir, "fig-2-1-dashboard-full.png"), fullPage: true });
    const routes = [
      ["sections", "fig-3-1-sections.png"],
      ["analysis", "fig-3-2-analysis.png"],
      ["designs", "fig-3-3-designs.png"],
      ["alarms", "fig-3-4-alerts.png"],
      ["reports", "fig-3-5-reports.png"],
    ];
    for (const [hash, filename] of routes) {
      await captureRoute(page, hash, filename);
    }
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});

