(() => {
  const PARAMS = { q: 'q', g: 'grade', u: 'unit', c: 'category', t: 'type', e: 'exam', s: 'sort' };
  const SORT_VALUES = new Set(['smart', 'recent', 'title', 'type']);
  const EXAM_VALUES = new Set(['all', 'end', 'mid', 'start', 'skill']);
  const UNIT_VALUES = new Set(['all', '3-unit', '4-unit', '5-unit']);
  let applying = false;

  function cleanSort(value) { return SORT_VALUES.has(value) ? value : 'smart'; }
  function cleanExam(value) { return EXAM_VALUES.has(value) ? value : 'all'; }
  function cleanUnit(value) { return UNIT_VALUES.has(value) ? value : 'all'; }

  function readParams() {
    try {
      const p = new URL(location.href).searchParams;
      return {
        q: p.get(PARAMS.q) || '',
        g: p.get(PARAMS.g) || 'all',
        u: cleanUnit(p.get(PARAMS.u) || 'all'),
        c: p.get(PARAMS.c) || 'all',
        t: p.get(PARAMS.t) || 'all',
        e: cleanExam(p.get(PARAMS.e) || 'all'),
        s: cleanSort(p.get(PARAMS.s) || 'smart'),
      };
    } catch {
      return { q: '', g: 'all', u: 'all', c: 'all', t: 'all', e: 'all', s: 'smart' };
    }
  }

  function activeValue(key) {
    const btn = document.querySelector(`[data-k="${key}"].on`);
    return btn?.dataset?.v || 'all';
  }
  function activeGrade() {
    const btn = document.querySelector('[data-grade-go].on');
    return btn?.dataset?.gradeGo || 'all';
  }
  function activeUnit() {
    const btn = document.querySelector('[data-unit].on');
    return cleanUnit(btn?.dataset?.unit || 'all');
  }
  function activeExam() {
    const btn = document.querySelector('[data-exam].on');
    return cleanExam(btn?.dataset?.exam || 'all');
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
      const g = activeGrade();
      const u = activeUnit();
      const c = activeValue('c');
      const t = activeValue('t');
      const e = activeExam();
      const s = activeSort();
      q ? url.searchParams.set(PARAMS.q, q) : url.searchParams.delete(PARAMS.q);
      g !== 'all' ? url.searchParams.set(PARAMS.g, g) : url.searchParams.delete(PARAMS.g);
      u !== 'all' ? url.searchParams.set(PARAMS.u, u) : url.searchParams.delete(PARAMS.u);
      c !== 'all' ? url.searchParams.set(PARAMS.c, c) : url.searchParams.delete(PARAMS.c);
      t !== 'all' ? url.searchParams.set(PARAMS.t, t) : url.searchParams.delete(PARAMS.t);
      e !== 'all' ? url.searchParams.set(PARAMS.e, e) : url.searchParams.delete(PARAMS.e);
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
  function clickData(selector, attr, value, skipValue) {
    if (!value || value === skipValue) return;
    const chips = [...document.querySelectorAll(selector)];
    const chip = chips.find(btn => (btn.dataset[attr] || '') === value);
    if (chip && !chip.classList.contains('on')) chip.click();
  }
  function clickGrade(value) { clickData('[data-grade-go]', 'gradeGo', value, 'all'); }
  function clickUnit(value) { clickData('[data-unit]', 'unit', cleanUnit(value), 'all'); }
  function clickExam(value) { clickData('[data-exam]', 'exam', cleanExam(value), 'all'); }
  function clickSort(value) { clickData('[data-sort]', 'sort', cleanSort(value), 'smart'); }

  function applyParams() {
    const params = readParams();
    applying = true;
    const input = document.getElementById('q');
    if (input && params.q && input.value !== params.q) {
      input.value = params.q;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    setTimeout(() => {
      clickGrade(params.g);
      setTimeout(() => {
        clickUnit(params.u);
        clickChip('c', params.c);
        clickChip('t', params.t);
        clickExam(params.e);
        clickSort(params.s);
        applying = false;
        writeParams();
      }, 100);
    }, 220);
  }

  function bind() {
    const input = document.getElementById('q');
    if (input && input.dataset.urlStateReady !== '1') {
      input.dataset.urlStateReady = '1';
      input.addEventListener('input', writeParams);
    }
    document.querySelectorAll('[data-k], [data-grade-go], [data-unit], [data-domain], [data-exam], [data-sort]').forEach(btn => {
      if (btn.dataset.urlStateReady === '1') return;
      btn.dataset.urlStateReady = '1';
      btn.addEventListener('click', () => setTimeout(writeParams, 0));
    });
  }

  const observer = new MutationObserver(bind);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener('DOMContentLoaded', () => { applyParams(); bind(); });
  setTimeout(() => { applyParams(); bind(); }, 700);
})();
