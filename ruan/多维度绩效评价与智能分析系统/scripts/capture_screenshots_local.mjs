import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright";

const root = process.cwd();
const outDir = path.join(root, "images");
const baseUrl = "http://127.0.0.1:8000";
const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

fs.mkdirSync(outDir, { recursive: true });

async function login(page, username = "admin", password = "admin123") {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click("#login-form button[type='submit']");
  await page.waitForTimeout(1800);
}

async function run() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: edgePath,
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);
  await page.screenshot({ path: path.join(outDir, "01-login.png"), fullPage: true });

  await login(page);
  await page.screenshot({ path: path.join(outDir, "02-dashboard.png"), fullPage: true });

  const routes = [
    ["masterdata", "03-masterdata.png"],
    ["plans", "04-plans.png"],
    ["reviews", "05-reviews.png"],
    ["analytics", "06-analytics.png"],
    ["workflow", "07-workflow.png"],
    ["audit", "08-audit.png"],
  ];

  for (const [hash, name] of routes) {
    await page.goto(`${baseUrl}/#${hash}`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1800);
    await page.screenshot({ path: path.join(outDir, name), fullPage: true });
  }

  await browser.close();
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
