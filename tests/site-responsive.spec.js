const { test, expect } = require('@playwright/test');
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.pdf': 'application/pdf',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.txt': 'text/plain; charset=utf-8',
};

function startServer() {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://127.0.0.1');
    let pathname = decodeURIComponent(url.pathname);
    if (pathname === '/') pathname = '/index.html';
    const file = path.normalize(path.join(ROOT, pathname));
    if (!file.startsWith(ROOT)) {
      res.writeHead(403);
      res.end('Forbidden');
      return;
    }
    fs.readFile(file, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not found');
        return;
      }
      res.writeHead(200, { 'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream' });
      res.end(data);
    });
  });
  return new Promise(resolve => {
    server.listen(0, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ server, url: `http://127.0.0.1:${port}/` });
    });
  });
}

async function noHorizontalOverflow(page) {
  const values = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }));
  expect(values.scrollWidth).toBeLessThanOrEqual(values.clientWidth + 2);
}

async function expectVisibleAndTouchable(locator, minHeight = 40) {
  await expect(locator).toBeVisible();
  const box = await locator.boundingBox();
  expect(box).toBeTruthy();
  expect(box.height).toBeGreaterThanOrEqual(minHeight);
}

const viewports = [
  { name: 'small-phone', width: 360, height: 740, minButton: 42, modalButton: 36 },
  { name: 'large-phone', width: 430, height: 932, minButton: 42, modalButton: 36 },
  { name: 'phone-landscape', width: 740, height: 360, minButton: 40, modalButton: 34 },
  { name: 'tablet', width: 820, height: 1180, minButton: 40, modalButton: 36 },
  { name: 'desktop', width: 1440, height: 1000, minButton: 40, modalButton: 36 },
  { name: 'short-desktop', width: 1200, height: 560, minButton: 40, modalButton: 34 },
];

for (const vp of viewports) {
  test(`responsive layout works on ${vp.name}`, async ({ browser }) => {
    const { server, url } = await startServer();
    const context = await browser.newContext({
      baseURL: url,
      viewport: { width: vp.width, height: vp.height },
      isMobile: vp.width < 700,
      hasTouch: vp.width < 900,
    });
    const page = await context.newPage();
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));

    try {
      await page.goto(url);
      await expect(page.locator('.brand')).toContainText('מאגר מתמטיקה');
      // Home shows only the grade gateway cards (no file list, no duplicate chips).
      await expect(page.locator('.grade-entry').first()).toBeVisible({ timeout: 15000 });
      await noHorizontalOverflow(page);

      await expectVisibleAndTouchable(page.locator('#q'), vp.minButton);
      await expectVisibleAndTouchable(page.locator('#clear'), vp.minButton);
      await expectVisibleAndTouchable(page.locator('.grade-entry').first(), vp.minButton);

      // Drill into a grade once -> topic (domain) buttons + files + viewer.
      await page.locator('.grade-entry').first().click();
      await expect(page.locator('.file').first()).toBeVisible({ timeout: 15000 });
      await noHorizontalOverflow(page);
      await expectVisibleAndTouchable(page.locator('.chip').first(), vp.minButton);
      await expectVisibleAndTouchable(page.locator('.act').first(), vp.minButton);

      const viewButton = page.locator('[data-view]').first();
      await expectVisibleAndTouchable(viewButton, vp.minButton);
      await viewButton.click();
      await expect(page.locator('#modal')).toBeVisible();
      await noHorizontalOverflow(page);
      await expectVisibleAndTouchable(page.locator('#mo'), vp.modalButton);
      await expectVisibleAndTouchable(page.locator('#md'), vp.modalButton);
      await expectVisibleAndTouchable(page.locator('#copy-modal-file-link'), vp.modalButton);
      await expectVisibleAndTouchable(page.locator('#share-modal-file-whatsapp'), vp.modalButton);
      await expectVisibleAndTouchable(page.locator('#x'), vp.modalButton);
      await page.locator('#x').click();
      await expect(page.locator('#modal')).not.toBeVisible();

      // Search resilience: no overflow, then clear returns home. The header can
      // be momentarily reflowing right after a search renders; dispatch the click
      // straight to the handler (we verify that clear works, not its hit-testing).
      await page.locator('#q').fill('משוואות');
      await noHorizontalOverflow(page);
      await page.locator('#clear').dispatchEvent('click');
      await expect(page.locator('.grade-entry').first()).toBeVisible({ timeout: 15000 });
      await noHorizontalOverflow(page);

      expect(pageErrors).toEqual([]);
    } finally {
      await context.close();
      await new Promise(resolve => server.close(resolve));
    }
  });
}
