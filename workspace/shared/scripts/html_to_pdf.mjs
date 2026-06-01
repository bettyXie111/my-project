import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const defaultEdgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

function resolvePlaywrightEntry() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE_PATH) {
    candidates.push(path.resolve(process.env.PLAYWRIGHT_MODULE_PATH));
  }
  let current = path.resolve(process.cwd());
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

function toFileUrl(filePath) {
  const normalized = path.resolve(filePath).replace(/\\/g, "/");
  return `file:///${normalized}`;
}

async function run() {
  const [inputHtml, outputPdf] = process.argv.slice(2);
  if (!inputHtml || !outputPdf) {
    throw new Error("Usage: node html_to_pdf.mjs <input.html> <output.pdf>");
  }

  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.EDGE_EXECUTABLE_PATH || defaultEdgePath,
  });

  try {
    const page = await browser.newPage({
      viewport: { width: 1280, height: 960 },
    });
    await page.goto(toFileUrl(inputHtml), { waitUntil: "load" });
    await page.waitForTimeout(800);
    await page.pdf({
      path: path.resolve(outputPdf),
      format: "A4",
      printBackground: true,
      margin: {
        top: "16mm",
        right: "14mm",
        bottom: "16mm",
        left: "14mm",
      },
    });
  } finally {
    await browser.close();
  }
}

run().catch((error) => {
  console.error(error);
  process.exit(1);
});
