/* ============================================================
   FED-SPA service worker.
   Cache-first for the app shell + data, network refresh in the
   background. Annual data updates reach installed users on
   their next launch without losing offline access.
   ============================================================ */

const CACHE = 'fedspa-v1';

const SHELL = [
  'index.html',
  'offline.html',
  'manifest.webmanifest',
  'css/style.css',
  'css/dark-theme.css',
  'css/responsive.css',
  'js/ui.js',
  'js/search.js',
  'js/crypto.js',
  'js/app.js',
  'data/licensed.json',
  'data/unlicensed.encrypted.json',
  'icons/icon-192.png',
  'icons/icon-512.png',
  'icons/maskable-512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  // Navigations: try network, fall back to shell/offline page.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() =>
        caches.match('index.html').then((r) => r || caches.match('offline.html'))
      )
    );
    return;
  }

  // Everything else: cache-first, refresh in background.
  event.respondWith(
    caches.match(req).then((cached) => {
      const fresh = fetch(req).then((res) => {
        if (res && res.ok && new URL(req.url).origin === location.origin) {
          const copy = res.clone();
          caches.open(CACHE).then((cache) => cache.put(req, copy));
        }
        return res;
      }).catch(() => cached);
      return cached || fresh;
    })
  );
});
