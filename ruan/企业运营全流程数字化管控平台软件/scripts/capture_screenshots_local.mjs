import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const root = process.cwd();
const outDir = process.env.SCREENSHOT_OUT_DIR
  ? path.resolve(process.env.SCREENSHOT_OUT_DIR)
  : path.join(root, "copyright-application-materials", "images");
const baseUrl = process.env.SCREENSHOT_BASE_URL || "http://127.0.0.1:8000";
const edgePath = process.env.EDGE_EXECUTABLE_PATH || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

fs.mkdirSync(outDir, { recursive: true });

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function login(page, username = "admin", password = "admin123") {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click("#login-form button[type='submit']");
  await page.waitForTimeout(1500);
}

async function run() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: edgePath,
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(outDir, "fig-1-1-login-full.png"), fullPage: true });

  await login(page);
  await page.screenshot({ path: path.join(outDir, "fig-2-1-home-full.png"), fullPage: true });

  const routes = [
    ["masterdata", "fig-3-1-masterdata-list.png"],
    ["procurement", "fig-3-2-procurement-create.png"],
    ["workflow", "fig-3-3-workflow-todo.png"],
    ["sales", "fig-3-4-sales-contract.png"],
    ["finance", "fig-3-5-finance-budget.png"],
    ["audit", "fig-3-6-audit-notice.png"],
  ];

  for (const [hash, name] of routes) {
    await page.goto(`${baseUrl}/#${hash}`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1500);
    await page.screenshot({ path: path.join(outDir, name), fullPage: true });
  }

  await browser.close();
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
