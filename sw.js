const CACHE_NAME = 'audiox-v1';
const ASSETS_TO_CACHE = [
    './MusicX.html',
    './manifest.json'
];

// Instala o Service Worker e guarda os arquivos em Cache
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Intercepta as requisições para o app funcionar offline
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});