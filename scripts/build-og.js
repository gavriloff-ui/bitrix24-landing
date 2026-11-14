#!/usr/bin/env node
/**
 * Собирает превью для соцсетей и поиска: brand/og-cover.png (1200×630).
 *
 * Требует установленного Chrome (PUPPETEER_EXECUTABLE_PATH) и шрифта Manrope.
 * Запуск: node scripts/build-og.js
 */
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const TEMPLATE = path.join(ROOT, 'scripts', 'og-template.html');
const OUT = path.join(ROOT, 'brand', 'og-cover.png');

function findChrome() {
  if (process.env.PUPPETEER_EXECUTABLE_PATH) return process.env.PUPPETEER_EXECUTABLE_PATH;
  const cache = path.join(process.env.HOME || '/root', '.cache', 'puppeteer');
  if (fs.existsSync(cache)) {
    const dir = fs.readdirSync(cache).find((d) => d.startsWith('chrome'));
    if (dir) {
      const p = path.join(cache, dir, 'chrome-linux64', 'chrome');
      if (fs.existsSync(p)) return p;
      const shell = path.join(cache, dir, 'chrome-headless-shell-linux64', 'chrome-headless-shell');
      if (fs.existsSync(shell)) return shell;
    }
  }
  return 'google-chrome';
}

function loadPuppeteer() {
  try {
    return require('puppeteer');
  } catch (e) {
    try {
      return require('puppeteer-core');
    } catch (e2) {
      console.error('Нужен puppeteer: npm i -D puppeteer  (или puppeteer-core + свой Chrome)');
      process.exit(1);
    }
  }
}

(async () => {
  const puppeteer = loadPuppeteer();
  const browser = await puppeteer.launch({
    headless: 'shell',
    executablePath: findChrome(),
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none'],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
  await page.goto('file://' + TEMPLATE, { waitUntil: 'networkidle0' });
  await page.evaluate(() => document.fonts.ready);
  await new Promise((r) => setTimeout(r, 400));
  await page.screenshot({ path: OUT });
  await browser.close();

  const size = execSync(`python3 -c "from PIL import Image; im=Image.open('${OUT}'); print(im.size)"`).toString().trim();
  console.log(`og-cover.png готов: ${size}`);
})();
