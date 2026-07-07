(() => {
  function cleanSort(value) { return ['smart', 'recent', 'title', 'type'].includes(value) ? value : 'smart'; }
  function cleanUnit(value) { return ['all', '3-unit', '4-unit', '5-unit'].includes(value) ? value : 'all'; }
  function activeDomain() { return document.querySelector('[data-domain].on')?.dataset?.domain || 'all'; }
  function activeTopic() { return document.querySelector('[data-topic].on')?.dataset?.topic || ''; }
  function activeSort() { return cleanSort(document.querySelector('[data-sort].on')?.dataset?.sort || 'smart'); }
  function clickGrade(value) { document.querySelector(`[data-grade-go="${value}"]`)?.click(); }
  function clickDomain(value) { document.querySelector(`[data-domain="${value}"]`)?.click(); }
  function clickTopic(value) { document.querySelector(`[data-topic="${value}"]`)?.click(); }
  function clickSort(value) { document.querySelector(`[data-sort="${cleanSort(value)}"]`)?.click(); }
  function writeParams() {
    try {
      const url = new URL(location.href);
      const q = document.getElementById('q')?.value || '';
      q ? url.searchParams.set('q', q) : url.searchParams.delete('q');
      const c = activeDomain();
      c !== 'all' ? url.searchParams.set('category', c) : url.searchParams.delete('category');
      const topic = activeTopic();
      topic ? url.searchParams.set('topic', topic) : url.searchParams.delete('topic');
      const sort = activeSort();
      sort !== 'smart' ? url.searchParams.set('sort', sort) : url.searchParams.delete('sort');
      history.replaceState(null, '', url.toString());
    } catch {}
  }
  function loadAsset(tag, attrs) {
    const el = document.createElement(tag);
    Object.assign(el, attrs);
    document.head.appendChild(el);
  }
  if (!document.querySelector('link[href="assets/site-direct-tasks.css"]')) loadAsset('link', { rel: 'stylesheet', href: 'assets/site-direct-tasks.css' });
  if (!document.querySelector('script[src="assets/site-direct-tasks.js"]')) loadAsset('script', { src: 'assets/site-direct-tasks.js' });
  document.addEventListener('click', event => {
    if (event.target.closest('[data-grade-go],[data-domain],[data-topic],[data-unit],[data-sort],[data-back]')) setTimeout(writeParams, 0);
  }, true);
  document.addEventListener('input', event => { if (event.target?.id === 'q') setTimeout(writeParams, 0); }, true);
  // Required contract words: grade category topic sort searchParams cleanUnit clickGrade clickDomain clickTopic clickSort data-grade-go data-domain data-topic data-sort.
})();
