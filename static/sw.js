// Service Worker — クワガタ採集スポット検索
// キャッシュ戦略: Cache First（静的アセット） / Network First（ページ）

const CACHE_NAME = 'beetle-finder-v1';
const CACHE_VERSION = '2026-05-30';

// 静的アセット（Cache First）
const STATIC_ASSETS = [
  '/static/icon-192.png',
  '/static/icon-512.png',
  '/static/apple-touch-icon.png',
  '/static/manifest.json',
  '/static/ogp_main.png',
  '/static/img/icon-kuwagata.jpg',
];

// キャッシュしないパス（APIは常にネットワーク）
const NETWORK_ONLY = [
  '/api/',
  '/health',
  '/sitemap.xml',
  '/robots.txt',
  '/feed.xml',
];

// インストール: 静的アセットを事前キャッシュ
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] 事前キャッシュの一部が失敗:', err);
      });
    })
  );
  self.skipWaiting();
});

// アクティベート: 古いキャッシュを削除
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// フェッチ: キャッシュ戦略
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // 外部リクエスト（Amazon・Google等）はそのまま
  if (url.origin !== self.location.origin) return;

  // APIは常にネットワーク
  if (NETWORK_ONLY.some(path => url.pathname.startsWith(path))) return;

  // 静的ファイル（/static/）: Cache First
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTMLページ: Network First（オフライン時はキャッシュ）
  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
