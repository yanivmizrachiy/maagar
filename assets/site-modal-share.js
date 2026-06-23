(() => {
  function currentFileLink() {
    try {
      const url = new URL(location.href);
      url.hash = '';
      return url.toString();
    } catch {
      return location.href;
    }
  }

  function currentFileTitle() {
    return document.getElementById('mt')?.textContent?.trim() || 'קובץ מהמאגר';
  }

  function toast(text) {
    let el = document.getElementById('share-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'share-toast';
      el.style.cssText = 'position:fixed;left:14px;bottom:14px;z-index:999;background:#0f172a;color:white;border:1px solid #ffffff33;border-radius:14px;padding:10px 14px;font:700 14px Arial;box-shadow:0 8px 24px #0008;display:none';
      document.body.appendChild(el);
    }
    el.textContent = text;
    el.style.display = 'block';
    clearTimeout(window.__modalShareToastTimer);
    window.__modalShareToastTimer = setTimeout(() => { el.style.display = 'none'; }, 1800);
  }

  async function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  }

  function ensureButtons() {
    const actions = document.querySelector('#modal .ma');
    if (!actions || document.getElementById('copy-modal-file-link')) return;

    const copy = document.createElement('button');
    copy.id = 'copy-modal-file-link';
    copy.type = 'button';
    copy.className = 'act';
    copy.textContent = '🔗 העתק קישור';
    copy.addEventListener('click', async () => {
      try {
        await copyText(currentFileLink());
        toast('קישור לקובץ הועתק');
      } catch {
        toast('לא הצלחתי להעתיק קישור לקובץ');
      }
    });

    const wa = document.createElement('a');
    wa.id = 'share-modal-file-whatsapp';
    wa.className = 'act';
    wa.target = '_blank';
    wa.rel = 'noopener noreferrer';
    wa.textContent = '🟢 WhatsApp';
    wa.addEventListener('click', () => {
      const text = `${currentFileTitle()}\n${currentFileLink()}`;
      wa.href = 'https://wa.me/?text=' + encodeURIComponent(text);
    });

    const close = document.getElementById('x');
    actions.insertBefore(copy, close);
    actions.insertBefore(wa, close);
  }

  document.addEventListener('DOMContentLoaded', ensureButtons);
  const observer = new MutationObserver(ensureButtons);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  setTimeout(ensureButtons, 500);
})();
