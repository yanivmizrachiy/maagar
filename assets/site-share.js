(() => {
  function abs(url) {
    try { return new URL(url, location.href).href; } catch { return url; }
  }

  function siteLinkForCard(card, fallbackUrl) {
    const viewBtn = card.querySelector('[data-view]');
    const fileId = viewBtn?.dataset?.view || '';
    if (fileId && typeof window.maagarFileLink === 'function') {
      return window.maagarFileLink(fileId);
    }
    return abs(fallbackUrl);
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
    clearTimeout(window.__shareToastTimer);
    window.__shareToastTimer = setTimeout(() => { el.style.display = 'none'; }, 1800);
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

  function enhanceCard(card) {
    if (card.dataset.shareEnhanced === '1') return;
    const actions = card.querySelector('.acts');
    if (!actions) return;
    const firstLink = actions.querySelector('a[href]');
    if (!firstLink) return;
    const title = (card.querySelector('.title')?.textContent || 'קובץ מהמאגר').trim();
    const link = siteLinkForCard(card, firstLink.getAttribute('href'));

    const copy = document.createElement('button');
    copy.type = 'button';
    copy.className = 'act';
    copy.textContent = '🔗 העתק קישור';
    copy.addEventListener('click', async () => {
      try {
        await copyText(link);
        toast('קישור לעמוד הקובץ הועתק');
      } catch {
        toast('לא הצלחתי להעתיק קישור');
      }
    });

    const whatsapp = document.createElement('a');
    whatsapp.className = 'act';
    whatsapp.textContent = '🟢 WhatsApp';
    whatsapp.target = '_blank';
    whatsapp.rel = 'noopener noreferrer';
    whatsapp.href = 'https://wa.me/?text=' + encodeURIComponent(title + '\n' + link);

    actions.appendChild(copy);
    actions.appendChild(whatsapp);
    card.dataset.shareEnhanced = '1';
  }

  function enhanceAll() {
    document.querySelectorAll('.file').forEach(enhanceCard);
  }

  const observer = new MutationObserver(enhanceAll);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', enhanceAll);
  setTimeout(enhanceAll, 500);
})();
