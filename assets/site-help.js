(() => {
  function ensureAppIcon() {
    if (document.querySelector('link[rel="icon"][href="assets/icon.svg"]')) return;
    const icon = document.createElement('link');
    icon.rel = 'icon';
    icon.href = 'assets/icon.svg';
    icon.type = 'image/svg+xml';
    document.head.appendChild(icon);
  }

  function ensureAccessibilityBasics() {
    const search = document.getElementById('q');
    const clear = document.getElementById('clear');
    const app = document.getElementById('app');
    const header = document.querySelector('.top');
    const bar = document.querySelector('.bar');
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('mt');
    const modalSub = document.getElementById('ms');
    const close = document.getElementById('x');

    if (header && !header.getAttribute('role')) header.setAttribute('role', 'banner');
    if (bar && !bar.getAttribute('role')) bar.setAttribute('role', 'search');
    if (bar && !bar.getAttribute('aria-label')) bar.setAttribute('aria-label', 'חיפוש וסינון במאגר מתמטיקה');
    if (search && !search.getAttribute('aria-label')) search.setAttribute('aria-label', 'חיפוש במאגר לפי שם, נושא, כיתה או סוג קובץ');
    if (clear && !clear.getAttribute('aria-label')) clear.setAttribute('aria-label', 'נקה חיפוש וסינונים');
    if (app && !app.getAttribute('tabindex')) app.setAttribute('tabindex', '-1');
    if (app && !app.getAttribute('aria-live')) app.setAttribute('aria-live', 'polite');
    if (modal && modalTitle) modal.setAttribute('aria-labelledby', modalTitle.id);
    if (modal && modalSub) modal.setAttribute('aria-describedby', modalSub.id);
    if (close) close.setAttribute('aria-label', 'סגור חלון צפייה');
  }

  function ensureSkipLink() {
    if (document.getElementById('skip-to-maagar')) return;
    const skip = document.createElement('a');
    skip.id = 'skip-to-maagar';
    skip.className = 'skip-link';
    skip.href = '#app';
    skip.textContent = 'דלג לתוכן המאגר';
    skip.addEventListener('click', () => setTimeout(() => document.getElementById('app')?.focus(), 20));
    document.body.insertBefore(skip, document.body.firstChild);
  }

  function ensureStyles() {
    if (document.getElementById('site-help-style')) return;
    const style = document.createElement('style');
    style.id = 'site-help-style';
    style.textContent = `
      .skip-link{position:fixed;right:12px;top:12px;z-index:1000;background:#ffffff;color:#07111f;border-radius:999px;padding:10px 14px;font:900 14px Arial,sans-serif;text-decoration:none;transform:translateY(-160%);transition:.16s ease;box-shadow:0 12px 32px #0008}
      .skip-link:focus{transform:translateY(0);outline:3px solid #93c5fd;outline-offset:2px}
      .act.disabled{opacity:.55;cursor:not-allowed;background:#64748b22!important;border-color:#94a3b855!important;color:#cbd5e1!important;box-shadow:none!important}
    `;
    document.head.appendChild(style);
  }

  function normalizeActionButtons() {
    document.querySelectorAll('button').forEach(btn => {
      if (!btn.getAttribute('type')) btn.setAttribute('type', 'button');
    });
    document.querySelectorAll('a[target="_blank"]').forEach(a => {
      a.rel = 'noopener noreferrer';
    });
    document.querySelectorAll('.acts').forEach(group => {
      const seen = new Set();
      group.querySelectorAll('a.act').forEach(a => {
        const target = (a.getAttribute('href') || '').trim();
        if (!target || target === '#') {
          const disabled = document.createElement('span');
          disabled.className = 'act disabled';
          disabled.setAttribute('aria-disabled', 'true');
          disabled.textContent = 'אין קישור פעיל';
          a.replaceWith(disabled);
          return;
        }
        const kind = a.hasAttribute('download') ? 'download' : 'open';
        const key = target + '|' + kind;
        if (seen.has(key)) a.remove();
        else seen.add(key);
      });
    });
  }

  function closeModal() {
    const modal = document.getElementById('modal');
    const close = document.getElementById('x');
    if (modal && getComputedStyle(modal).display !== 'none') close?.click();
  }

  function ensureKeyboardShortcuts() {
    if (window.__maagarKeyboardShortcutsReady) return;
    window.__maagarKeyboardShortcutsReady = true;
    document.addEventListener('keydown', (event) => {
      const active = document.activeElement;
      const typing = active && ['INPUT', 'TEXTAREA', 'SELECT'].includes(active.tagName);
      if (event.key === 'Escape') {
        closeModal();
      }
      if (!typing && event.key === '/') {
        event.preventDefault();
        document.getElementById('q')?.focus();
      }
    });
  }

  function boot() {
    ensureAppIcon();
    ensureStyles();
    ensureAccessibilityBasics();
    ensureSkipLink();
    ensureKeyboardShortcuts();
    normalizeActionButtons();
  }

  document.addEventListener('DOMContentLoaded', boot);
  const observer = new MutationObserver(boot);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  setTimeout(boot, 500);
})();
