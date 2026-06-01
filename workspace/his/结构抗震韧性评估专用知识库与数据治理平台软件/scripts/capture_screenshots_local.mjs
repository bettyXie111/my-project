import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const root = process.cwd();
const outDir = process.env.SCREENSHOT_OUT_DIR
  ? path.resolve(process.env.SCREENSHOT_OUT_DIR)
  : path.join(root, "copyright-application-materials", "images");
const baseUrl = process.env.SCREENSHOT_BASE_URL || "http://127.0.0.1:8000";
const edgePath = process.env.EDGE_EXECUTABLE_PATH || "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

function resolvePlaywrightEntry() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE_PATH) {
    candidates.push(path.resolve(process.env.PLAYWRIGHT_MODULE_PATH));
  }
  let current = path.resolve(root);
  while (true) {
    candidates.push(path.join(current, "node_modules", "playwright", "index.mjs"));
    const parent = path.dirname(current);
    if (parent === current) {
      break;
    }
    current = parent;
  }
  const hit = candidates.find((candidate) => fs.existsSync(candidate));
  if (!hit) {
    throw new Error("Cannot locate playwright/index.mjs. Install playwright under E:\\copyRight\\workspace\\node_modules or set PLAYWRIGHT_MODULE_PATH.");
  }
  return hit;
}

const playwrightEntry = resolvePlaywrightEntry();
const { chromium } = await import(pathToFileURL(playwrightEntry).href);

fs.mkdirSync(outDir, { recursive: true });

const defaultPlan = [
  { figure: "图1-1", filename: "fig-1-1-login-full.png", page: "login" },
  { figure: "图2-1", filename: "fig-2-1-home-full.png", page: "home" },
  { figure: "图3-1", filename: "fig-3-1-zones.png", hash: "zones" },
  { figure: "图3-2", filename: "fig-3-2-stations.png", hash: "stations" },
  { figure: "图3-2a", filename: "fig-3-2a-stations-create-modal.png", hash: "stations", action: "create", modal: "true" },
  { figure: "图3-2b", filename: "fig-3-2b-stations-edit-modal.png", hash: "stations", action: "edit", modal: "true" },
  { figure: "图3-2c", filename: "fig-3-2c-stations-view-modal.png", hash: "stations", action: "view", modal: "true" },
  { figure: "图3-2d", filename: "fig-3-2d-stations-delete-modal.png", hash: "stations", action: "delete", modal: "true" },
  { figure: "图3-3", filename: "fig-3-3-inspections.png", hash: "inspections" },
  { figure: "图3-4", filename: "fig-3-4-alerts.png", hash: "alerts" },
  { figure: "图3-5", filename: "fig-3-5-irrigation.png", hash: "irrigation" },
  { figure: "图3-6", filename: "fig-3-6-reports.png", hash: "reports" },
];
const minScreenshotCount = 12;

function loadScreenshotPlan() {
  if (!process.env.SCREENSHOT_PLAN_JSON) {
    return defaultPlan;
  }
  const raw = JSON.parse(process.env.SCREENSHOT_PLAN_JSON);
  if (!Array.isArray(raw) || raw.length < minScreenshotCount) {
    throw new Error(`SCREENSHOT_PLAN_JSON must contain at least ${minScreenshotCount} items.`);
  }
  return raw.map((item, index) => {
    if (!item || typeof item !== "object") {
      throw new Error(`Invalid screenshot plan item #${index + 1}.`);
    }
    const figure = String(item.figure || "").trim();
    const filename = String(item.filename || "").trim();
    const page = String(item.page || "").trim().toLowerCase();
    const hash = String(item.hash || "").trim().replace(/^#/, "");
    const routePath = String(item.path || "").trim();
    const action = String(item.action || "").trim().toLowerCase();
    const modal = String(item.modal || "").trim().toLowerCase();
    const clickSelector = String(item.clickSelector || "").trim();
    const waitSelector = String(item.waitSelector || "").trim();
    if (!figure || !filename) {
      throw new Error(`Screenshot plan item #${index + 1} missing figure or filename.`);
    }
    if (page) {
      if (!["login", "home"].includes(page)) {
        throw new Error(`Unsupported screenshot plan page '${page}'.`);
      }
      if (hash || routePath) {
        throw new Error(`Screenshot plan item #${index + 1} cannot mix page with hash/path.`);
      }
    } else if ((hash && routePath) || (!hash && !routePath)) {
      throw new Error(`Screenshot plan item #${index + 1} must define one of page/hash/path.`);
    }
    if (action && !["create", "edit", "delete", "view"].includes(action)) {
      throw new Error(`Unsupported screenshot plan action '${action}' in item #${index + 1}.`);
    }
    if (modal && !["true", "false"].includes(modal)) {
      throw new Error(`Invalid screenshot plan modal value '${modal}' in item #${index + 1}.`);
    }
    if (modal === "true" && !action) {
      throw new Error(`Screenshot plan item #${index + 1} modal=true requires action=create/edit/delete/view.`);
    }
    if (action && modal !== "true") {
      throw new Error(`Screenshot plan item #${index + 1} action requires modal=true.`);
    }
    if (clickSelector && modal !== "true") {
      throw new Error(`Screenshot plan item #${index + 1} clickSelector requires modal=true.`);
    }
    if (waitSelector && modal !== "true") {
      throw new Error(`Screenshot plan item #${index + 1} waitSelector requires modal=true.`);
    }
    return { figure, filename, page, hash, path: routePath, action, modal, clickSelector, waitSelector };
  });
}

function resolveEntryUrl(entry) {
  if (entry.page === "login" || entry.page === "home") {
    return baseUrl;
  }
  if (entry.hash) {
    return `${baseUrl}/#${entry.hash}`;
  }
  return new URL(entry.path, baseUrl).href;
}

async function login(page, username = "admin", password = "admin123") {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);
  await page.fill('input[name="username"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('#login-form button[type="submit"]');
  await page.waitForTimeout(1500);
}

async function openModalForAction(page, { action, clickSelector, waitSelector }) {
  // If a previous screenshot left the modal open, close it first to avoid mask intercepting clicks.
  await page.evaluate(() => window.__rkModal?.closeModal?.()).catch(() => {});
  await page.waitForTimeout(150);
  if (clickSelector) {
    await page.click(clickSelector, { timeout: 6000 });
  } else {
  const textMap = {
    create: "新增",
    edit: "编辑",
    delete: "删除",
    view: "查看",
  };
  const label = textMap[action];
  const candidates = [
    `button:has-text("${label}")`,
    `a:has-text("${label}")`,
    `[role="button"]:has-text("${label}")`,
    `text=${label}`,
  ];
  let clicked = false;
  for (const selector of candidates) {
    const handle = await page.$(selector);
    if (!handle) continue;
    await handle.click({ timeout: 2000 }).catch(() => {});
    clicked = true;
    break;
  }
  if (!clicked) {
    throw new Error(`Cannot find clickable element for modal action '${action}' (${label}).`);
  }
  }
  const modalSelectors = [
    '#modal.modal-shell.modal [role="dialog"]',
    '#modal.modal-shell.modal',
    '[role="dialog"]',
    ".ant-modal",
    ".el-dialog",
    ".MuiDialog-root",
    ".ivu-modal",
  ];
  const locator = waitSelector ? waitSelector : modalSelectors.join(", ");
  await page.waitForSelector(locator, { state: "visible", timeout: 8000 });
}

async function run() {
  const screenshotPlan = loadScreenshotPlan();
  const browser = await chromium.launch({
    headless: true,
    executablePath: edgePath,
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

  let loggedIn = false;
  for (const entry of screenshotPlan) {
    if (entry.page !== "login" && !loggedIn) {
      await login(page);
      loggedIn = true;
    }
    await page.goto(resolveEntryUrl(entry), { waitUntil: "domcontentloaded" });
    await page.waitForTimeout(entry.page === "login" ? 1200 : 1500);
    if (entry.modal === "true") {
      await openModalForAction(page, entry);
      await page.waitForTimeout(600);
    }
    await page.screenshot({ path: path.join(outDir, entry.filename), fullPage: true });
    if (entry.modal === "true") {
      await page.evaluate(() => window.__rkModal?.closeModal?.()).catch(() => {});
      await page.waitForTimeout(200);
    }
  }

  await browser.close();
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
