const CACHE_NAME = 'afrihealth-v1.2';
const ASSETS = [
'./',
'./index.html',
'./manifest.json',
'https://cdn.tailwindcss.com',
'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
'https://cdn.jsdelivr.net/npm/chart.js'
];

self.addEventListener('install', (e) => {
e.waitUntil(
caches.open(CACHE_NAME)
.then((cache) => cache.addAll(ASSETS))
.then(() => self.skipWaiting())
);
});

self.addEventListener('activate', (e) => {
e.waitUntil(
caches.keys().then((keys) =>
Promise.all(keys.map((k) => k !== CACHE_NAME && caches.delete(k)))
).then(() => self.clients.claim())
);
});

self.addEventListener('fetch', (e) => {
if (e.request.method !== 'GET') return;
e.respondWith(
caches.match(e.request).then((cached) => cached || fetch(e.request).catch(() => cached))
);
});
