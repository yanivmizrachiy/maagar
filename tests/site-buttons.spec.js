const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const ACTIVE_SITE_FILES = [
  'index.html',
  'assets/site.js',
  'assets/site.css',
  'assets/site-url-state.js',
  'assets/site-deeplink.js',
  'assets/site-share.js',
  'assets/site-view-share.js',
  'assets/site-modal-share.js',
  'assets/site-help.js',
];

function readText(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

function readJson(relativePath) {
  return JSON.parse(readText(relativePath));
}

function collectStrings(value, strings = []) {
  if (Array.isArray(value)) {
    for (const item of value) collectStrings(item, strings);
    return strings;
  }
  if (value && typeof value === 'object') {
    for (const item of Object.values(value)) collectStrings(item, strings);
    return strings;
  }
  if (typeof value === 'string') strings.push(value.trim());
  return strings;
}

function expectNoVisibleDemoText(label, text) {
  const normalized = String(text || '').replace(/placeholder="[^"]*"/g, '').replace(/placeholder='[^']*'/g, '');
  const forbidden = [/\bdemo\b/i, /\bdummy\b/i, /\bmock\b/i, /\blorem\b/i, /\bfake\b/i, /דמו/];
  const hits = [];
  for (const pattern of forbidden) {
    const match = normalized.match(pattern);
    if (match) hits.push(`${label}: ${match[0]}`);
  }
  expect(hits).toEqual([]);
}

test('site action buttons are real and stable', async () => {
  const indexHtml = readText('index.html');
  const siteJs = readText('assets/site.js');
  const helpJs = readText('assets/site-help.js');
  const shareJs = readText('assets/site-share.js');
  const viewShareJs = readText('assets/site-view-share.js');
  const modalShareJs = readText('assets/site-modal-share.js');
  const metadata = readJson('metadata/index.json');

  for (const file of ACTIVE_SITE_FILES) {
    expectNoVisibleDemoText(file, readText(file));
  }

  expect(indexHtml).toContain('assets/site.js');
  expect(indexHtml).toContain('assets/site-help.js');
  expect(indexHtml).toContain('assets/site-share.js');
  expect(indexHtml).toContain('assets/site-view-share.js');
  expect(indexHtml).toContain('assets/site-modal-share.js');

  expect(siteJs).toContain('data-view');
  expect(siteJs).toContain('downloadable(f)');
  expect(siteJs).toContain('downloadUrl(f)');
  expect(siteJs).toContain('downloadName(f)');
  expect(siteJs).toContain('downloadButton(f)');
  expect(siteJs).toContain('fast-download');
  expect(siteJs).toContain('הורדה מהירה');
  expect(siteJs).toContain('הורדה ישירה זמינה');
  expect(siteJs).toContain('data-download');
  expect(siteJs).toContain('groupLabel(f)');
  expect(siteJs).toContain('compareFiles');
  expect(siteJs).toContain('compareGroups');
  expect(siteJs).toContain('מיון: שכבה › תחום › נושא');
  expect(siteJs).toMatch(/\.\/\$\{f\.path\}/);

  const shareBundle = `${shareJs}\n${viewShareJs}\n${modalShareJs}`;
  expect(shareBundle).toMatch(/whatsapp|wa\.me/i);
  expect(shareBundle).toContain('share-toast');

  expect(helpJs).toContain('aria-disabled');
  expect(helpJs).toContain('אין קישור פעיל');
  expect(helpJs).toContain("hasAttribute('download')");
  expect(helpJs).toContain('noopener noreferrer');

  expect(Array.isArray(metadata.files)).toBeTruthy();
  expect(metadata.files.length).toBeGreaterThan(0);
  expect(metadata.files.some(file => file.path && /^files\//.test(file.path))).toBeTruthy();
  expect(metadata.files.some(file => file.download_ready === true)).toBeTruthy();
  expect(metadata.files.some(file => file.source_type === 'repo-file' && file.path && file.file_name && file.download_ready === true)).toBeTruthy();

  const strings = collectStrings(metadata).filter(Boolean);
  const badValues = strings.filter(value => value === '#' || value === 'javascript:void(0)' || value.toLowerCase() === 'demo' || /\bdummy\b|\bmock\b|\blorem\b|\bfake\b|דמו/i.test(value));
  expect(badValues).toEqual([]);
});
