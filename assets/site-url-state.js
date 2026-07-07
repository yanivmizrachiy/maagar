(() => {
  const GRADES = ['all', '7', '8', '9', 'high-school'];
  const CATEGORIES = ['all', 'algebra', 'geometry', 'summaries', 'exams', 'uncategorized'];
  const UNITS = ['all', '3-unit', '4-unit', '5-unit'];
  const SORTS = ['smart', 'recent', 'title', 'type'];

  function clean(value, allowed, fallback) { return allowed.includes(value) ? value : fallback; }
  function cleanGrade(value) { return clean(value || 'all', GRADES, 'all'); }
  function cleanCategory(value) { return clean(value || 'all', CATEGORIES, 'all'); }
  function cleanSort(value) { return clean(value || 'smart', SORTS, 'smart'); }
  function cleanUnit(value) { return clean(value || 'all', UNITS, 'all'); }

  function activeGrade() { try { return typeof S !== 'undefined' ? S.g || 'all' : 'all'; } catch { return 'all'; } }
  function activeDomain() { try { return typeof S !== 'undefined' ? S.c || 'all' : 'all'; } catch { return 'all'; } }
  function activeSort() { try { return typeof S !== 'undefined' ? cleanSort(S.sort || 'smart') : 'smart'; } catch { return 'smart'; } }
  function activeUnit() { try { return typeof S !== 'undefined' ? cleanUnit(S.u || 'all') : 'all'; } catch { return 'all'; } }

  function writeParams() {
    try {
      const url = new URL(location.href);
      const q = document.getElementById('q')?.value || '';
      const grade = activeGrade();
      const category = activeDomain();
      const unit = activeUnit();
      const sort = activeSort();
      q ? url.searchParams.set('q', q) : url.searchParams.delete('q');
      grade !== 'all' ? url.searchParams.set('grade', grade) : url.searchParams.delete('grade');
      category !== 'all' ? url.searchParams.set('category', category) : url.searchParams.delete('category');
      unit !== 'all' ? url.searchParams.set('unit', unit) : url.searchParams.delete('unit');
      sort !== 'smart' ? url.searchParams.set('sort', sort) : url.searchParams.delete('sort');
      history.replaceState(null, '', url.toString());
    } catch {}
  }

  function readInitialParams() {
    try {
      const searchParams = new URL(location.href).searchParams;
      return {
        grade: cleanGrade(searchParams.get('grade')),
        category: cleanCategory(searchParams.get('category')),
        unit: cleanUnit(searchParams.get('unit')),
        sort: cleanSort(searchParams.get('sort')),
        q: searchParams.get('q') || '',
      };
    } catch {
      return { grade: 'all', category: 'all', unit: 'all', sort: 'smart', q: '' };
    }
  }

  function hasInitialState(params) {
    return params.grade !== 'all' || params.category !== 'all' || params.unit !== 'all' || params.sort !== 'smart' || !!params.q;
  }

  function applyInitialParams(params, attempt = 0) {
    if (!hasInitialState(params)) return;
    try {
      if (typeof S === 'undefined' || typeof render !== 'function' || !S.files || !S.files.length) {
        if (attempt < 50) setTimeout(() => applyInitialParams(params, attempt + 1), 100);
        return;
      }
      const q = document.getElementById('q');
      S.g = params.grade;
      S.u = params.unit;
      S.c = params.category;
      S.t = 'all';
      S.exam = 'all';
      S.topic = '';
      S.sort = params.sort;
      S.q = params.q;
      if (q) q.value = params.q;
      render();
      writeParams();
    } catch {
      if (attempt < 50) setTimeout(() => applyInitialParams(params, attempt + 1), 100);
    }
  }

  const initialParams = readInitialParams();
  document.addEventListener('click', event => {
    if (event.target.closest('[data-grade-go],[data-domain],[data-unit],[data-sort],[data-back]')) setTimeout(writeParams, 0);
  }, true);
  document.addEventListener('input', event => { if (event.target?.id === 'q') setTimeout(writeParams, 0); }, true);
  document.addEventListener('DOMContentLoaded', () => applyInitialParams(initialParams));
  setTimeout(() => applyInitialParams(initialParams), 250);
})();
