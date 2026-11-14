#!/usr/bin/env node
/**
 * Добавляет к ссылке на site.css версию по хешу файла:
 * assets/css/site.css?v=1a2b3c4d
 *
 * Так браузер не покажет старый CSS после деплоя. Запускается после сборки
 * Tailwind (npm run build); трогает index.html, privacy.html, offer.html и 404.html.
 */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const CSS = path.join(ROOT, 'assets', 'css', 'site.css');
const PAGES = ['index.html', 'privacy.html', 'offer.html', '404.html'];

const hash = crypto.createHash('sha1').update(fs.readFileSync(CSS)).digest('hex').slice(0, 8);
let updated = 0;

for (const page of PAGES) {
  const file = path.join(ROOT, page);
  if (!fs.existsSync(file)) continue;

  const before = fs.readFileSync(file, 'utf8');
  const after = before.replace(/assets\/css\/site\.css(?:\?v=[a-f0-9]+)?/g, `assets/css/site.css?v=${hash}`);

  if (after !== before) {
    fs.writeFileSync(file, after);
    updated += 1;
  }
}

console.log(`site.css?v=${hash} — обновлено страниц: ${updated}`);
