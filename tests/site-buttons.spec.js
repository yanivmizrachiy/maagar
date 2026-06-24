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

function collectUrls(value, urls = []) {
  if (Array.isArray(value)) {
    for (const item of value) collectUrls(item, urls);
    return urls;
  }
  if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (/url|href|download|preview|embed|link/i.test(key) && typeof item === 'string') urls.push(item.trim());
      collectUrls(item, urls);
    }
  }
  return urls;
}

test('site action buttons are real and stable', async () => {
  const indexHtml = readText('index.html');
  const siteJs = readText('assets/site.js');
  const helpJs = readText('assets/site-help.js');
  const metadata = readJson('metadata/index.json');

  expect(indexHtml).toContain('assets/site.js');
  expect(indexHtml).toContain('assets/site-help.js');
  expect(indexHtml).toContain('assets/site-share.js');
  expect(indexHtml).toContain('assets/site-modal-share.js');

  expect(siteJs).toContain('data-view');
  expect(siteJs).toMatch(/download/);
  expect(siteJs).toMatch(/whatsapp|wa\.me/i);
  expect(siteJs).toContain('share-toast');

  expect(helpJs).toContain('aria-disabled');
  expect(helpJs).toContain('אין קישור פעיל');
  expect(helpJs).toContain('hasAttribute(\'download\')');
  expect(helpJs).toContain('noopener noreferrer');

  const urls = collectUrls(metadata).filter(Boolean);
  expect(urls.length).toBeGreaterThan(0);
  expect(urls.some(url => /^https?:\/\//.test(url))).toBeTruthy();

  const badUrls = urls.filter(url => url === '#' || url === 'javascript:void(0)' || url.toLowerCase() === 'demo');
  expect(badUrls).toEqual([]);

  const hasDownloadCandidate = urls.some(url => /export=download|download|uc\?export=download|\.pdf(\?|$)/i.test(url));
  expect(hasDownloadCandidate).toBeTruthy();
});
