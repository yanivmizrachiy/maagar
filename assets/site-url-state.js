(() => {
  // Keeps the drill-down state (grade -> category/domain -> topic, plus unit,
  // search and sort) in the URL so refresh/back/deep links restore the view.
  const PARAMS = { q: 'q', g: 'grade', u: 'unit', c: 'category', topic: 'topic', s: 'sort' };
  const SORT_VALUES = new Set(['smart', 'recent', 'title', 'type']);
  const UNIT_VALUES = new Set(['all', '3-unit', '4-unit', '5-unit']);
  let applying = false;

  function cleanSort(value) { return SORT_VALUES.has(value) ? value : 'smart'; }
  function cleanUnit(value) { return UNIT_VALUES.has(value) ? value : 'all'; }

  function readParams() {
    try {
      const p = new URL(location.href).searchParams;
      return {
        q: p.get(PARAMS.q) || '',
        g: p.get(PARAMS.g) || 'all',
        u: cleanUnit(p.get(PARAMS.u) || 'all'),
        c: p.get(PARAMS.c) || 'all',
        topic: p.get(PARAMS.topic) || '',
        s: cleanSort(p.get(PARAMS.s) || 'smart'),
      };
    } catch {
      return { q: '', g: 'all', u: 'all', c: 'all', topic: '', s: 'smart' };
    }
  }

  function activeDomain() {
    const btn = document.querySelector('[data-domain].on');
    return btn?.dataset?.domain || 'all';
  }
  function activeTopic() {
    const btn = document.querySelector('[data-topic].on');
    return btn?.dataset?.topic || '';
  }
  function activeUnit() {
    const btn = document.querySelector('[data-unit].on');
    return cleanUnit(btn?.dataset?.unit || 'all');
  }
  function activeSort() {
    const btn = document.querySelector('[data-sort].on');
    return cleanSort(btn?.dataset?.sort || 'smart');
  }

  let lastKnown = { g: 'all', c: 'all', topic: '' };

  function writeParams() {
    if (applying || !history.replaceState) return;
    try {
      const url = new URL(location.href);
      const q = document.getElementById('q')?.value || '';
      const u = activeUnit();
      const c = activeDomain() !== 'all' ? activeDomain() : lastKnown.c;
      const topic = activeTopic() || lastKnown.topic;
      const g = lastKnown.g;
      const s = activeSort();
      q ? url.searchParams.set(PARAMS.q, q) : url.searchParams.delete(PARAMS.q);
      g !== 'all' ? url.searchParams.set(PARAMS.g, g) : url.searchParams.delete(PARAMS.g);
      u !== 'all' ? url.searchParams.set(PARAMS.u, u) : url.searchParams.delete(PARAMS.u);
      c !== 'all' ? url.searchParams.set(PARAMS.c, c) : url.searchParams.delete(PARAMS.c);
      topic ? url.searchParams.set(PARAMS.topic, topic) : url.searchParams.delete(PARAMS.topic);
      s !== 'smart' ? url.searchParams.set(PARAMS.s, s) : url.searchParams.delete(PARAMS.s);
      history.replaceState(null, '', url.toString());
    } catch {}
  }

  function trackClicks() {
    document.addEventListener('click', event => {
      const grade = event.target.closest('[data-grade-go]');
      if (grade) { lastKnown = { g: grade.dataset.gradeGo || 'all', c: 'all', topic: '' }; }
      const domain = event.target.closest('[data-domain]');
      if (domain) { lastKnown.c = domain.dataset.domain || 'all'; lastKnown.topic = ''; }
      const topic = event.target.closest('[data-topic]');
      if (topic) { lastKnown.topic = topic.dataset.topic || ''; }
      const back = event.target.closest('[data-back]');
      if (back) {
        if (lastKnown.topic) lastKnown.topic = '';
        else if (lastKnown.c !== 'all') lastKnown.c = 'all';
        else lastKnown.g = 'all';
      }
      setTimeout(writeParams, 0);
    }, true);
  }

  function clickData(selector, attr, value, skipValue) {
    if (!value || value === skipValue) return;
    const chips = [...document.querySelectorAll(selector)];
    const chip = chips.find(btn => (btn.dataset[attr] || '') === value);
    if (chip && !chip.classList.contains('on')) chip.click();
  }
  function clickGrade(value) { clickData('[data-grade-go]', 'gradeGo', value, 'all'); }
  function clickDomain(value) { clickData('[data-domain]', 'domain', value, 'all'); }
  function clickTopic(value) { clickData('[data-topic]', 'topic', value, ''); }
  function clickUnit(value) { clickData('[data-unit]', 'unit', cleanUnit(value), 'all'); }
  function clickSort(value) { clickData('[data-sort]', 'sort', cleanSort(value), 'smart'); }

  let userInteracted = false;
  let restored = false;

  function applyParams() {
    if (restored || userInteracted) return;
    restored = true;
    const params = readParams();
    applying = true;
    const input = document.getElementById('q');
    if (input && params.q && input.value !== params.q) {
      input.value = params.q;
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    lastKnown = { g: params.g, c: params.c, topic: params.topic };
    setTimeout(() => {
      if (userInteracted) { applying = false; return; }
      clickGrade(params.g);
      setTimeout(() => {
        clickUnit(params.u);
        clickDomain(params.c);
        setTimeout(() => {
          clickTopic(params.topic);
          clickSort(params.s);
          applying = false;
          writeParams();
        }, 120);
      }, 120);
    }, 60);
  }

  function bind() {
    const input = document.getElementById('q');
    if (input && input.dataset.urlStateReady !== '1') {
      input.dataset.urlStateReady = '1';
      input.addEventListener('input', () => setTimeout(writeParams, 0));
    }
  }

  function hasStateParams() {
    const p = readParams();
    return !!(p.q || p.topic || p.g !== 'all' || p.c !== 'all' || p.u !== 'all' || p.s !== 'smart');
  }

  // Restore once, after the async metadata fetch has rendered the gateway.
  // A user click before that point cancels the restore (no fighting the user).
  function restoreWhenReady(tries) {
    if (restored || userInteracted) return;
    if (document.querySelector('[data-grade-go]')) { applyParams(); return; }
    if (tries <= 0) return;
    setTimeout(() => restoreWhenReady(tries - 1), 100);
  }

  document.addEventListener('DOMContentLoaded', () => {
    bind();
    trackClicks();
    document.addEventListener('click', event => {
      if (!applying && event.target.closest('[data-grade-go],[data-domain],[data-topic],[data-unit],[data-sort],[data-back]')) userInteracted = true;
    }, true);
    if (hasStateParams()) restoreWhenReady(40);
  });
})();
