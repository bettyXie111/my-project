import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const outDir = path.join(root, "images");
const baseUrl = String(process.env.SCREENSHOT_BASE_URL || "").trim();
const edgePath = String(process.env.EDGE_EXECUTABLE_PATH || "").trim();

if (!baseUrl) {
  throw new Error("Missing SCREENSHOT_BASE_URL env var.");
}
if (!edgePath) {
  throw new Error("Missing EDGE_EXECUTABLE_PATH env var.");
}

function resolvePlaywrightEntry() {
  const candidate = path.resolve(root, "..", "node_modules", "playwright", "index.mjs");
  if (fs.existsSync(candidate)) return candidate;
  const alt = path.resolve(root, "..", "..", "node_modules", "playwright", "index.mjs");
  if (fs.existsSync(alt)) return alt;
  throw new Error("Cannot locate playwright/index.mjs under workspace node_modules.");
}

const playwrightEntry = resolvePlaywrightEntry();
const { chromium } = await import(pathToFileURL(playwrightEntry).href);

fs.mkdirSync(outDir, { recursive: true });

function freshPath(filename) {
  const p = path.join(outDir, filename);
  try {
    fs.rmSync(p, { force: true });
  } catch {
    // ignore
  }
  return p;
}

function alignCreationTimeToWriteTime() {
  // Explorer "日期" column may be configured as "创建日期". When a file is overwritten in-place,
  // CreationTime can stay old. Aligning avoids "not latest" confusion.
  const cmd = [
    "-NoProfile",
    "-NonInteractive",
    "-Command",
    [
      `$dir='${outDir.replace(/'/g, "''")}';`,
      "Get-ChildItem -LiteralPath $dir -Filter *.png | ForEach-Object {",
      "$_.CreationTime = $_.LastWriteTime;",
      "}",
      "Write-Output 'creation_time_aligned'",
    ].join(" "),
  ];
  spawnSync("powershell", cmd, { stdio: "ignore" });
}

async function loginAs(page, username) {
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await page.goto(`${baseUrl}teacher.html`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#sceneSelect", { timeout: 10000 });
  await page.fill("#u", username);
  await page.fill("#p", "demo");
  await page.click("#btnLogin");
  await page.waitForTimeout(600);
}

async function selectScene(page, index) {
  const sel = page.locator("#sceneSelect");
  await sel.selectOption({ index });
  await page.waitForTimeout(300);
  await page.waitForSelector(".device", { timeout: 10000 });
}

async function selectFirstLesson(page) {
  await page.waitForTimeout(300);
  const lesson = page.locator("#lessonSelect");
  await page.waitForFunction(() => {
    const el = document.getElementById("lessonSelect");
    return !!el && el.querySelectorAll("option").length > 0;
  });
  const count = await lesson.locator("option").count();
  if (count > 0) {
    await lesson.selectOption({ index: 0 });
  }
  await page.waitForTimeout(300);
  await page.waitForSelector(".clip", { timeout: 10000 });
}

async function selectFirstClip(page) {
  await page.waitForSelector(".clip", { timeout: 10000 });
  const clip = page.locator(".clip").first();
  await clip.click();
  await page.waitForTimeout(300);
}

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: edgePath });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

  // 01: login form (before login) — visually distinct from post-login.
  await page.goto(`${baseUrl}teacher.html`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#btnLogin", { timeout: 10000 });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图01：登录页（未登录状态）"));
  await page.screenshot({ path: freshPath("01_login.png"), fullPage: true });

  // 02: after login (teacher)
  await loginAs(page, "teacher");
  await page.waitForFunction(() => {
    const who = document.getElementById("who");
    return who && who.textContent && who.textContent.includes("teacher");
  });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图02：登录成功与场景选择"));
  await page.screenshot({ path: freshPath("02_scene_select.png"), fullPage: true });

  await selectScene(page, 1);
  await selectScene(page, 2);
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图03：设备面板（不同场景）"));
  await page.locator("#devices").screenshot({ path: freshPath("03_devices.png") });

  await selectFirstLesson(page);
  await page.click("#btnAddLesson");
  await page.waitForTimeout(600);
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图04：新增课时后的列表"));
  await page.locator(".card:has(#lessonSelect)").screenshot({ path: freshPath("04_lessons.png") });

  // Ensure clip region is visible and capture after selecting a clip
  await selectFirstLesson(page);
  await selectFirstClip(page);
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图05：片段列表与选中高亮"));
  await page.screenshot({ path: freshPath("05_clips.png"), fullPage: true });

  await page.click("#btnStart");
  await page.waitForTimeout(600);
  await page.waitForSelector("#policy", { timeout: 10000 });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图06：开始上课（会话策略）"));
  await page.locator("#policy").screenshot({ path: freshPath("06_start.png") });

  await selectFirstClip(page);
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图07：课堂控制台按钮区（已选片段）"));
  await page.locator(".controls").first().screenshot({ path: freshPath("07_controls.png") });

  await page.click("#btnPlay");
  await page.waitForTimeout(300);
  await page.click("#btnLoop");
  await page.waitForTimeout(300);
  await page.click("#btnSpeed");
  await page.waitForTimeout(300);
  await page.waitForFunction(() => {
    const tl = document.getElementById("timeline");
    return tl && tl.querySelectorAll(".evt").length >= 2;
  });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图08：时间轴日志（已有事件）"));
  await page.screenshot({ path: freshPath("08_timeline.png"), fullPage: true });

  await page.click("#btnDeleteLesson");
  await page.waitForSelector("#modal:not(.hidden)", { timeout: 3000 });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图09：删除课时确认提示"));
  await page.screenshot({ path: freshPath("09_confirm_delete_lesson.png"), fullPage: true });
  await page.evaluate(() => window.__rkModal?.closeModal?.());
  await page.waitForTimeout(250);

  await page.click("#btnDeleteClip");
  await page.waitForSelector("#modal:not(.hidden)", { timeout: 3000 });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图10：删除片段确认提示"));
  await page.screenshot({ path: freshPath("10_confirm_delete_clip.png"), fullPage: true });

  // 11: admin policy editor
  await page.goto(`${baseUrl}admin.html`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#sceneSelect", { timeout: 10000 });
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图11：管理端策略配置"));
  await page.screenshot({ path: freshPath("11_admin_policy.png"), fullPage: true });

  // 12: student follow view (use currentSession if available)
  await page.goto(`${baseUrl}student.html`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#sessionId", { timeout: 10000 });
  // If no session id, still capture the student page layout.
  await page.waitForFunction(() => typeof window.__shotTag === "function");
  await page.evaluate(() => window.__shotTag("截图12：学生端跟随入口"));
  await page.screenshot({ path: freshPath("12_student_follow.png"), fullPage: true });

  await browser.close();
  alignCreationTimeToWriteTime();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
