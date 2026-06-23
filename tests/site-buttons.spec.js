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

test('all main site buttons work without JavaScript errors', async ({ browser }) => {
  const { server, url } = await startServer();
  const context = await browser.newContext({ baseURL: url });
  await context.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: url.slice(0, -1) });
  const page = await context.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));

  try {
    await page.goto(url);
    await expect(page.locator('.brand')).toContainText('מאגר מתמטיקה');
    await expect(page.locator('.file').first()).toBeVisible({ timeout: 15000 });

    await page.locator('#q').fill('משוואות');
    await expect(page.locator('#q')).toHaveValue('משוואות');
    await page.locator('#clear').click();
    await expect(page.locator('#q')).toHaveValue('');

    const firstGradeChip = page.locator('[data-k="g"]').nth(1);
    if (await firstGradeChip.count()) {
      await firstGradeChip.click();
      await expect(firstGradeChip).toHaveClass(/on/);
    }

    await expect(page.locator('#copy-view-link')).toBeVisible();
    await page.locator('#copy-view-link').click();
    await expect(page.locator('#share-toast')).toContainText('תצוגה');
    await expect(page.locator('#share-view-whatsapp')).toHaveAttribute('href', /wa\.me/);

    await expect(page.locator('#site-help-open')).toBeVisible();
    await page.locator('#site-help-open').click();
    await expect(page.locator('#site-help-panel')).toHaveClass(/open/);
    await expect(page.locator('#site-help-panel')).toContainText('עזרה מהירה');
    await page.locator('#site-help-close').click();
    await expect(page.locator('#site-help-panel')).not.toHaveClass(/open/);

    const viewButton = page.locator('[data-view]').first();
    await expect(viewButton).toBeVisible();
    await viewButton.click();
    await expect(page.locator('#modal')).toBeVisible();
    await expect(page.locator('#mo')).toHaveAttribute('href', /.+/);
    await expect(page.locator('#md')).toHaveAttribute('href', /.+/);
    await expect(page.locator('#copy-modal-file-link')).toBeVisible();
    await expect(page.locator('#share-modal-file-whatsapp')).toBeVisible();
    await expect(page.locator('#share-modal-file-whatsapp')).toHaveAttribute('href', /wa\.me/);
    await page.locator('#copy-modal-file-link').click();
    await expect(page.locator('#share-toast')).toContainText('קובץ');
    await page.locator('#x').click();
    await expect(page.locator('#modal')).not.toBeVisible();

    expect(pageErrors).toEqual([]);
  } finally {
    await context.close();
    await new Promise(resolve => server.close(resolve));
  }
});
