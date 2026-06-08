#!/usr/bin/env node
import { chromium } from "playwright";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [input, output, ...args] = process.argv.slice(2);

if (!input || !output) {
  console.error("Usage: node scripts/render_pdf.mjs input.html output.pdf --format landscape-16x9|portrait-a4");
  process.exit(1);
}

const formatIndex = args.indexOf("--format");
const format = formatIndex >= 0 ? args[formatIndex + 1] : "landscape-16x9";

const formats = {
  "landscape-16x9": {
    width: "13.333in",
    height: "7.5in",
    printBackground: true,
    preferCSSPageSize: true,
  },
  "portrait-a4": {
    format: "A4",
    landscape: false,
    printBackground: true,
    preferCSSPageSize: true,
  },
};

if (!formats[format]) {
  console.error(`Unknown format: ${format}`);
  console.error("Expected: landscape-16x9 or portrait-a4");
  process.exit(1);
}

const inputUrl = pathToFileURL(path.resolve(input)).href;
const outputPath = path.resolve(output);

const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage();
  await page.goto(inputUrl, { waitUntil: "networkidle" });
  await page.pdf({ path: outputPath, ...formats[format] });
  console.log(outputPath);
} finally {
  await browser.close();
}
