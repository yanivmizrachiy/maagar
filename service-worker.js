const CACHE_NAME = 'maagar-site-v1';
const APP_SHELL = [
  './',
  './index.html',
  './assets/site.css',
  './assets/site.js',
  './assets/site-url-state.js',
  './assets/site-deeplink.js',
  './assets/site-share.js',
  './assets/site-view-share.js',
  './assets/site-modal-share.js',
  './assets/site-help.js',
  './assets/icon.svg',
  './metadata/index.json',
  './metadata/taxonomy.json',
  './metadata/topic-map.json',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== location.origin) return;

  const isMetadata = url.pathname.includes('/metadata/');
  if (isMetadata) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        return response;
      });
    })
  );
});
