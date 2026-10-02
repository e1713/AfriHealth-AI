const CACHE_NAME = 'afrihealth-v1.4';
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
e.waitUntil((async () => {
const keys = await caches.keys();
await Promise.all(keys.map((key) => key !== CACHE_NAME ? caches.delete(key) : Promise.resolve()));
await self.clients.claim();
const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
await Promise.all(windows.map((client) => client.navigate(client.url).catch(() => null)));
})());
});

self.addEventListener('fetch', (e) => {
if (e.request.method !== 'GET') return;
const requestUrl = new URL(e.request.url);
const isPage = e.request.mode === 'navigate' || requestUrl.pathname.endsWith('.html');
if (isPage) {
e.respondWith(
fetch(e.request)
	.then((response) => {
		if (response.ok) {
			const responseCopy = response.clone();
			caches.open(CACHE_NAME).then((cache) => cache.put(e.request, responseCopy));
		}
		return response;
	})
	.catch(() => caches.match(e.request).then((cached) => cached || caches.match('./index.html')))
);
return;
}
e.respondWith(
caches.match(e.request).then((cached) => cached || fetch(e.request).catch(() => cached))
);
});
