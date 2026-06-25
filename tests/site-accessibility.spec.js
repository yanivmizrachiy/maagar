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
  '.svg': 'image/svg+xml; charset=utf-8',
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

test('accessibility helpers, app icon and keyboard shortcuts are active', async ({ browser }) => {
  const { server, url } = await startServer();
  const context = await browser.newContext({ baseURL: url, viewport: { width: 390, height: 850 } });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));

  try {
    await page.goto(url);
    await expect(page.locator('.brand')).toContainText('מאגר מתמטיקה');
    await expect(page.locator('link[rel="icon"][href="assets/icon.svg"]')).toHaveCount(1);

    await expect(page.locator('#skip-to-maagar')).toHaveAttribute('href', '#app');
    await page.locator('#skip-to-maagar').focus();
    await page.keyboard.press('Enter');
    await expect(page.locator('#app')).toBeFocused();

    await expect(page.locator('.top')).toHaveAttribute('role', 'banner');
    await expect(page.locator('.bar')).toHaveAttribute('role', 'search');
    await expect(page.locator('#q')).toHaveAttribute('aria-label', /חיפוש/);
    await expect(page.locator('#clear')).toHaveAttribute('aria-label', /נקה/);
    await expect(page.locator('#app')).toHaveAttribute('aria-live', 'polite');

    await page.locator('body').click();
    await page.keyboard.press('/');
    await expect(page.locator('#q')).toBeFocused();
    await page.keyboard.press('Escape');

    const viewButton = page.locator('[data-view]').first();
    await expect(viewButton).toBeVisible({ timeout: 15000 });
    await viewButton.click();
    await expect(page.locator('#modal')).toHaveAttribute('aria-labelledby', 'mt');
    await expect(page.locator('#modal')).toHaveAttribute('aria-describedby', 'ms');
    await expect(page.locator('#x')).toHaveAttribute('aria-label', /סגור/);
    await expect(page.locator('#modal')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.locator('#modal')).not.toBeVisible();

    expect(pageErrors).toEqual([]);
  } finally {
    await context.close();
    await new Promise(resolve => server.close(resolve));
  }
});
