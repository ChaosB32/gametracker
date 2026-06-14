const CACHE_V = 'gt-v2';
const STATIC  = 'gt-static-v2';

const PRECACHE = [
  '/',
  '/jogos/',
  '/auth/login/',
  '/static/manifest.json',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
];

// Install
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(STATIC).then(c => c.addAll(PRECACHE).catch(() => {}))
      .then(() => self.skipWaiting())
  );
});

// Activate — clear old caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_V && k !== STATIC).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch strategy
self.addEventListener('fetch', e => {
  const { request: req } = e;
  const url = new URL(req.url);

  if (req.method !== 'GET') return;

  // API / insights — always network, never cache
  if (url.pathname.startsWith('/api/') || url.pathname.includes('/insights/') ||
      url.pathname.startsWith('/export/')) return;

  // Static assets — cache first
  if (url.pathname.startsWith('/static/') ||
      url.hostname.includes('googleapis') ||
      url.hostname.includes('gstatic') ||
      url.hostname.includes('jsdelivr') ||
      url.hostname.includes('tailwindcss')) {
    e.respondWith(
      caches.match(req).then(cached => cached || fetch(req).then(res => {
        if (res.ok) caches.open(STATIC).then(c => c.put(req, res.clone()));
        return res;
      }).catch(() => cached))
    );
    return;
  }

  // HTML pages — network first, cache fallback
  e.respondWith(
    fetch(req).then(res => {
      if (res.ok) caches.open(CACHE_V).then(c => c.put(req, res.clone()));
      return res;
    }).catch(() =>
      caches.match(req).then(cached => cached || caches.match('/'))
    )
  );
});
