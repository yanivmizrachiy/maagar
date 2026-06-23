(() => {
  function getFileIdFromUrl() {
    try {
      return new URL(location.href).searchParams.get('file') || '';
    } catch {
      return '';
    }
  }

  function setFileIdInUrl(fileId) {
    if (!fileId || !history.replaceState) return;
    try {
      const url = new URL(location.href);
      url.searchParams.set('file', fileId);
      history.replaceState(null, '', url.toString());
    } catch {}
  }

  function linkForFile(fileId) {
    try {
      const url = new URL(location.href);
      url.searchParams.set('file', fileId);
      url.hash = '';
      return url.toString();
    } catch {
      return location.href;
    }
  }

  function findViewButton(fileId) {
    const buttons = document.querySelectorAll('[data-view]');
    for (const btn of buttons) {
      if ((btn.dataset.view || '') === fileId) return btn;
    }
    return null;
  }

  function openRequestedFile() {
    const fileId = getFileIdFromUrl();
    if (!fileId) return false;
    const btn = findViewButton(fileId);
    if (!btn) return false;
    btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTimeout(() => btn.click(), 250);
    return true;
  }

  function enhanceViewButtons() {
    document.querySelectorAll('[data-view]').forEach(btn => {
      if (btn.dataset.deepLinkReady === '1') return;
      btn.dataset.deepLinkReady = '1';
      btn.addEventListener('click', () => setFileIdInUrl(btn.dataset.view || ''));
    });
  }

  window.maagarFileLink = linkForFile;

  const observer = new MutationObserver(() => {
    enhanceViewButtons();
    if (!window.__maagarDeepLinkOpened) {
      window.__maagarDeepLinkOpened = openRequestedFile();
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', () => {
    enhanceViewButtons();
    setTimeout(() => {
      window.__maagarDeepLinkOpened = openRequestedFile();
    }, 650);
  });
})();
