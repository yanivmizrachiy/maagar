const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');

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

test('site action buttons are real and stable', async () => {
  const indexHtml = readText('index.html');
  const siteJs = readText('assets/site.js');
  const helpJs = readText('assets/site-help.js');
  const shareJs = readText('assets/site-share.js');
  const viewShareJs = readText('assets/site-view-share.js');
  const modalShareJs = readText('assets/site-modal-share.js');
  const metadata = readJson('metadata/index.json');

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
  expect(siteJs).toContain('צפייה מוטמעת · הורדה ישירה זמינה');
  expect(siteJs).toContain('data-download');
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
  const badValues = strings.filter(value => value === '#' || value === 'javascript:void(0)' || value.toLowerCase() === 'demo');
  expect(badValues).toEqual([]);
});
