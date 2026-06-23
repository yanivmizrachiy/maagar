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

  function modalWhatsAppHref() {
    const text = `${currentFileTitle()}\n${currentFileLink()}`;
    return 'https://wa.me/?text=' + encodeURIComponent(text);
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

  function updateWhatsApp() {
    const wa = document.getElementById('share-modal-file-whatsapp');
    if (wa) wa.href = modalWhatsAppHref();
  }

  function ensureButtons() {
    const actions = document.querySelector('#modal .ma');
    if (!actions || document.getElementById('copy-modal-file-link')) {
      updateWhatsApp();
      return;
    }

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
      updateWhatsApp();
    });

    const wa = document.createElement('a');
    wa.id = 'share-modal-file-whatsapp';
    wa.className = 'act';
    wa.target = '_blank';
    wa.rel = 'noopener noreferrer';
    wa.textContent = '🟢 WhatsApp';
    wa.href = modalWhatsAppHref();
    wa.addEventListener('focus', updateWhatsApp);
    wa.addEventListener('pointerdown', updateWhatsApp);
    wa.addEventListener('click', updateWhatsApp);

    const close = document.getElementById('x');
    actions.insertBefore(copy, close);
    actions.insertBefore(wa, close);
    updateWhatsApp();
  }

  document.addEventListener('DOMContentLoaded', ensureButtons);
  const observer = new MutationObserver(ensureButtons);
  observer.observe(document.documentElement, { childList: true, subtree: true, attributes: true });
  setTimeout(ensureButtons, 500);
})();
