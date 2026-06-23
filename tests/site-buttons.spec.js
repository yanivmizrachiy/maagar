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

function escapeRegExp(text) {
  return String(text).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

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

async function expectTouchTarget(locator, minHeight = 40) {
  const box = await locator.boundingBox();
  expect(box).toBeTruthy();
  expect(box.height).toBeGreaterThanOrEqual(minHeight);
}

async function expectRealActionLinks(page) {
  const badLinks = await page.locator('.acts a.act').evaluateAll(links => links
    .map(a => ({ text: a.textContent.trim(), href: (a.getAttribute('href') || '').trim() }))
    .filter(item => !item.href || item.href === '#'));
  expect(badLinks).toEqual([]);

  const duplicateTargets = await page.locator('.acts').evaluateAll(groups => {
    const duplicates = [];
    for (const group of groups) {
      const seen = new Set();
      for (const a of group.querySelectorAll('a.act')) {
        const href = (a.getAttribute('href') || '').trim();
        if (seen.has(href)) duplicates.push(href);
        seen.add(href);
      }
    }
    return duplicates;
  });
  expect(duplicateTargets).toEqual([]);
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
    await expectRealActionLinks(page);

    await expectTouchTarget(page.locator('#clear'));
    await expectTouchTarget(page.locator('.act').first(), 42);

    await page.locator('#q').fill('משוואות');
    await expect(page.locator('#q')).toHaveValue('משוואות');
    await page.locator('#clear').click();
    await expect(page.locator('#q')).toHaveValue('');
    await expectRealActionLinks(page);

    const firstGradeChip = page.locator('[data-k="g"]').nth(1);
    if (await firstGradeChip.count()) {
      await expectTouchTarget(firstGradeChip);
      await firstGradeChip.click();
      await expect(firstGradeChip).toHaveClass(/on/);
      await expectRealActionLinks(page);
    }

    await expect(page.locator('#copy-view-link')).toBeVisible();
    await expectTouchTarget(page.locator('#copy-view-link'));
    await page.locator('#copy-view-link').click();
    await expect(page.locator('#share-toast')).toContainText('תצוגה');
    await expect(page.locator('#share-view-whatsapp')).toHaveAttribute('href', /wa\.me/);

    await expect(page.locator('#site-help-open')).toBeVisible();
    await expectTouchTarget(page.locator('#site-help-open'));
    await page.locator('#site-help-open').click();
    await expect(page.locator('#site-help-panel')).toHaveClass(/open/);
    await expect(page.locator('#site-help-panel')).toContainText('עזרה מהירה');
    await page.locator('#site-help-close').click();
    await expect(page.locator('#site-help-panel')).not.toHaveClass(/open/);

    const viewButton = page.locator('[data-view]').first();
    await expect(viewButton).toBeVisible();
    await expectTouchTarget(viewButton, 42);
    const fileId = await viewButton.getAttribute('data-view');
    expect(fileId).toBeTruthy();
    const safeFileId = escapeRegExp(fileId);
    await viewButton.click();
    await expect(page).toHaveURL(new RegExp(`[?&]file=${safeFileId}`));
    await expect(page.locator('#modal')).toBeVisible();
    await expect(page.locator('#mo')).toHaveAttribute('href', /.+/);
    await expect(page.locator('#md')).toHaveAttribute('href', /.+/);
    await expect(page.locator('#copy-modal-file-link')).toBeVisible();
    await expect(page.locator('#share-modal-file-whatsapp')).toBeVisible();
    await expectTouchTarget(page.locator('#copy-modal-file-link'), 38);
    await expectTouchTarget(page.locator('#share-modal-file-whatsapp'), 38);
    await expect(page.locator('#share-modal-file-whatsapp')).toHaveAttribute('href', /wa\.me/);
    await expect(page.locator('#share-modal-file-whatsapp')).toHaveAttribute('href', new RegExp(escapeRegExp(encodeURIComponent(`file=${fileId}`))));
    await page.locator('#copy-modal-file-link').click();
    await expect(page.locator('#share-toast')).toContainText('קובץ');
    await page.locator('#x').click();
    await expect(page.locator('#modal')).not.toBeVisible();

    await page.setViewportSize({ width: 390, height: 850 });
    await expectTouchTarget(page.locator('.act').first(), 44);
    await expectTouchTarget(page.locator('#clear'), 42);
    await expectRealActionLinks(page);

    expect(pageErrors).toEqual([]);
  } finally {
    await context.close();
    await new Promise(resolve => server.close(resolve));
  }
});
