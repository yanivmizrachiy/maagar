(() => {
  const PARAMS = { q: 'q', g: 'grade', c: 'category', t: 'type', s: 'sort' };
  const SORT_VALUES = new Set(['smart', 'recent', 'title', 'type']);
  let applying = false;

  function cleanSort(value) {
    return SORT_VALUES.has(value) ? value : 'smart';
  }

  function readParams() {
    try {
      const p = new URL(location.href).searchParams;
      return {
        q: p.get(PARAMS.q) || '',
        g: p.get(PARAMS.g) || 'all',
        c: p.get(PARAMS.c) || 'all',
        t: p.get(PARAMS.t) || 'all',
        s: cleanSort(p.get(PARAMS.s) || 'smart'),
      };
    } catch {
      return { q: '', g: 'all', c: 'all', t: 'all', s: 'smart' };
    }
  }

  function activeValue(key) {
    const btn = document.querySelector(`[data-k="${key}"].on`);
    return btn?.dataset?.v || 'all';
  }

  function activeSort() {
    const btn = document.querySelector('[data-sort].on');
    return cleanSort(btn?.dataset?.sort || 'smart');
  }

  function writeParams() {
    if (applying || !history.replaceState) return;
    try {
      const url = new URL(location.href);
      const q = document.getElementById('q')?.value || '';
      const g = activeValue('g');
      const c = activeValue('c');
      const t = activeValue('t');
      const s = activeSort();

      q ? url.searchParams.set(PARAMS.q, q) : url.searchParams.delete(PARAMS.q);
      g !== 'all' ? url.searchParams.set(PARAMS.g, g) : url.searchParams.delete(PARAMS.g);
      c !== 'all' ? url.searchParams.set(PARAMS.c, c) : url.searchParams.delete(PARAMS.c);
      t !== 'all' ? url.searchParams.set(PARAMS.t, t) : url.searchParams.delete(PARAMS.t);
      s !== 'smart' ? url.searchParams.set(PARAMS.s, s) : url.searchParams.delete(PARAMS.s);
      history.replaceState(null, '', url.toString());
    } catch {}
  }

  function clickChip(key, value) {
    if (!value || value === 'all') return;
    const chips = [...document.querySelectorAll(`[data-k="${key}"]`)];
    const chip = chips.find(btn => (btn.dataset.v || '') === value);
    if (chip && !chip.classList.contains('on')) chip.click();
  }

  function clickSort(value) {
    const sort = cleanSort(value);
    if (sort === 'smart') return;
    const chips = [...document.querySelectorAll('[data-sort]')];
    const chip = chips.find(btn => (btn.dataset.sort || '') === sort);
    if (chip && !chip.classList.contains('on')) chip.click();
  }

  function applyParams() {
    const params = readParams();
    applying = true;
    const input = document.getElementById('q');
    if (input && params.q && input.value !== params.q) {
      input.value = params.q;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    setTimeout(() => {
      clickChip('g', params.g);
      clickChip('c', params.c);
      clickChip('t', params.t);
      clickSort(params.s);
      applying = false;
      writeParams();
    }, 250);
  }

  function bind() {
    const input = document.getElementById('q');
    if (input && input.dataset.urlStateReady !== '1') {
      input.dataset.urlStateReady = '1';
      input.addEventListener('input', writeParams);
    }
    document.querySelectorAll('[data-k]').forEach(btn => {
      if (btn.dataset.urlStateReady === '1') return;
      btn.dataset.urlStateReady = '1';
      btn.addEventListener('click', () => setTimeout(writeParams, 0));
    });
    document.querySelectorAll('[data-sort]').forEach(btn => {
      if (btn.dataset.urlStateReady === '1') return;
      btn.dataset.urlStateReady = '1';
      btn.addEventListener('click', () => setTimeout(writeParams, 0));
    });
  }

  const observer = new MutationObserver(bind);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', () => {
    applyParams();
    bind();
  });
  setTimeout(() => { applyParams(); bind(); }, 700);
})();
