import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawn } from "node:child_process";
import { chromium } from "playwright";

const root = process.env.PROJECT_ROOT ? path.resolve(process.env.PROJECT_ROOT) : process.cwd();
const frontendDir = path.join(root, "frontend");
const outDir = path.join(root, "copyright-application-materials", "images");
const host = process.env.SCREENSHOT_HOST || "127.0.0.1";
const port = process.env.SCREENSHOT_PORT || "4173";
const baseUrl = `http://${host}:${port}`;

fs.mkdirSync(outDir, { recursive: true });

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForServer(url, timeoutMs = 90000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.status < 500) return;
    } catch {}
    await sleep(800);
  }
  throw new Error(`Server not ready: ${url}`);
}

function ensureFrontendProject() {
  const pkg = path.join(frontendDir, "package.json");
  if (!fs.existsSync(pkg)) {
    throw new Error(`frontend/package.json not found: ${pkg}`);
  }
}

async function capture() {
  ensureFrontendProject();
  const isWin = process.platform === "win32";
  const cmd = isWin ? "cmd.exe" : "npm";
  const args = isWin
    ? ["/c", "npm", "run", "dev", "--", "--host", host, "--port", String(port), "--strictPort"]
    : ["run", "dev", "--", "--host", host, "--port", String(port), "--strictPort"];

  const dev = spawn(cmd, args, {
    cwd: frontendDir,
    stdio: "pipe",
    shell: false,
  });

  let ready = false;
  dev.stdout.on("data", (buf) => {
    const t = buf.toString();
    if (t.includes(`${host}:${port}`) || t.toLowerCase().includes("ready")) ready = true;
  });

  try {
    if (!ready) await waitForServer(`${baseUrl}/login`);

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 980 } });

    await page.goto(`${baseUrl}/login`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(outDir, "fig-1-1-login.png"), fullPage: true });

    await page.goto(`${baseUrl}/`, { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(outDir, "fig-2-1-home-full.png"), fullPage: true });

    const cards = page.locator(".section-card");
    if ((await cards.count()) > 0) {
      await cards.nth(0).screenshot({ path: path.join(outDir, "fig-3-1-module-a.png") });
    }

    const dropdown = page.locator("select,[role='combobox']").first();
    if (await dropdown.count()) {
      await dropdown.click();
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(outDir, "fig-3-2-dropdown.png"), fullPage: false });
    }

    const checkbox = page.locator("input[type='checkbox']").first();
    if (await checkbox.count()) {
      await checkbox.check({ force: true });
      await page.waitForTimeout(200);
      await page.screenshot({ path: path.join(outDir, "fig-3-3-checkbox-batch.png"), fullPage: false });
    }

    await browser.close();
  } finally {
    dev.kill();
  }
}

capture().catch((err) => {
  console.error(err);
  process.exit(1);
});
