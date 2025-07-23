const CACHE_NAME = 'soodava-v1.0.0';
const STATIC_CACHE = 'soodava-static-v1.0.0';
const DYNAMIC_CACHE = 'soodava-dynamic-v1.0.0';

// فایل‌های استاتیک که باید کش بشن
const STATIC_FILES = [
  '/',
  '/static/css/site-styles.css',
  '/static/css/mobile-enhancements.css',
  '/static/css/button-hierarchy.css',
  '/static/js/site-enhancements.js',
  '/static/js/mobile-enhancements.js',
  '/static/logo-1.png',
  '/static/manifest.json',
  '/static/browserconfig.xml',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// نصب Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker نصب شد');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('فایل‌های استاتیک کش شدند');
        return cache.addAll(STATIC_FILES);
      })
      .catch(error => {
        console.log('خطا در کش کردن فایل‌ها:', error);
      })
  );
});

// فعال‌سازی Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker فعال شد');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('کش قدیمی حذف شد:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// مدیریت درخواست‌ها
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // برای درخواست‌های API و دیتابیس، همیشه از شبکه استفاده کن
  if (url.pathname.startsWith('/admin/') || 
      url.pathname.startsWith('/api/') ||
      url.pathname.includes('.php') ||
      request.method !== 'GET') {
    event.respondWith(fetch(request));
    return;
  }

  // برای فایل‌های استاتیک، از کش استفاده کن
  if (STATIC_FILES.includes(url.pathname) || 
      url.pathname.startsWith('/static/') ||
      url.pathname.startsWith('/media/')) {
    event.respondWith(
      caches.match(request)
        .then(response => {
          if (response) {
            return response;
          }
          return fetch(request).then(response => {
            if (response.status === 200) {
              const responseClone = response.clone();
              caches.open(DYNAMIC_CACHE).then(cache => {
                cache.put(request, responseClone);
              });
            }
            return response;
          });
        })
    );
    return;
  }

  // برای صفحات HTML، استراتژی Network First
  if (request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request);
        })
    );
    return;
  }

  // برای سایر درخواست‌ها، Cache First
  event.respondWith(
    caches.match(request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(request).then(response => {
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(DYNAMIC_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        });
      })
  );
});

// پیام‌های Service Worker
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
}); 