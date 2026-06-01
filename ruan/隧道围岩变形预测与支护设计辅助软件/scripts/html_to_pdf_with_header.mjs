import path from "node:path";
import { chromium } from "playwright";

const defaultEdgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";

function toFileUrl(filePath) {
  const normalized = path.resolve(filePath).replace(/\\/g, "/");
  return `file:///${normalized}`;
}

function escapeHtml(text) {
  return text
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function run() {
  const [inputHtml, outputPdf] = process.argv.slice(2);
  if (!inputHtml || !outputPdf) {
    throw new Error("Usage: node html_to_pdf_with_header.mjs <input.html> <output.pdf>");
  }

  const headerText = escapeHtml(process.env.PDF_HEADER_TEXT || "");
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
      displayHeaderFooter: true,
      headerTemplate: `
        <div style="width:100%; font-size:9px; color:#000; text-align:center; padding:0 14mm;">
          ${headerText}
        </div>
      `,
      footerTemplate: `
        <div style="width:100%; font-size:9px; color:#000; text-align:right; padding:0 14mm;">
          <span class="pageNumber"></span>
        </div>
      `,
      margin: {
        top: "18mm",
        right: "14mm",
        bottom: "18mm",
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
