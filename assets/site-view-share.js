(() => {
  function currentViewLink() {
    try {
      const url = new URL(location.href);
      url.searchParams.delete('file');
      url.hash = '';
      return url.toString();
    } catch {
      return location.href;
    }
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
    clearTimeout(window.__viewShareToastTimer);
    window.__viewShareToastTimer = setTimeout(() => { el.style.display = 'none'; }, 1800);
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
    const bar = document.querySelector('.bar');
    if (!bar || document.getElementById('copy-view-link')) return;

    const copy = document.createElement('button');
    copy.id = 'copy-view-link';
    copy.type = 'button';
    copy.className = 'btn';
    copy.textContent = '🔗 העתק תצוגה';
    copy.addEventListener('click', async () => {
      try {
        await copyText(currentViewLink());
        toast('קישור לתצוגה הנוכחית הועתק');
      } catch {
        toast('לא הצלחתי להעתיק את התצוגה');
      }
    });

    const wa = document.createElement('a');
    wa.id = 'share-view-whatsapp';
    wa.className = 'btn';
    wa.textContent = '🟢 שתף תצוגה';
    wa.target = '_blank';
    wa.rel = 'noopener noreferrer';
    wa.addEventListener('click', () => {
      wa.href = 'https://wa.me/?text=' + encodeURIComponent('מאגר מתמטיקה - תצוגה מסוננת\n' + currentViewLink());
    });

    bar.appendChild(copy);
    bar.appendChild(wa);
  }

  document.addEventListener('DOMContentLoaded', ensureButtons);
  const observer = new MutationObserver(ensureButtons);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  setTimeout(ensureButtons, 500);
})();
