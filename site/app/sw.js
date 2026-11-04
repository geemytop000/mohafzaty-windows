/* محفظتي برو — تخزين مؤقت لفتح البرنامج بدون إنترنت */
const V = 'wl-v2.2.6';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'favicon.svg', '../favicon.ico'];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(V).then(function (c) { return Promise.all(SHELL.map(function (u) { return c.add(u).catch(function () {}); })); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k !== V; }).map(function (k) { return caches.delete(k); })); }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  const r = e.request;
  if (r.method !== 'GET') return;
  const u = new URL(r.url);
  const sameOrigin = u.origin === self.location.origin;
  const staticCdn = /(^|\.)gstatic\.com$|(^|\.)cdnjs\.cloudflare\.com$|(^|\.)fonts\.googleapis\.com$/.test(u.hostname);
  if (sameOrigin) {
    /* الشبكة أولًا (عشان التحديثات توصل)، والنسخة المحفوظة لو مفيش إنترنت */
    e.respondWith(fetch(r).then(function (res) { const cp = res.clone(); if (res.ok) caches.open(V).then(function (c) { c.put(r, cp); }); return res; }).catch(function () { return caches.match(r).then(function (m) { return m || caches.match('index.html'); }); }));
  } else if (staticCdn) {
    e.respondWith(caches.match(r).then(function (m) { const net = fetch(r).then(function (res) { const cp = res.clone(); caches.open(V).then(function (c) { c.put(r, cp); }); return res; }).catch(function () { return m; }); return m || net; }));
  }
  /* باقي الطلبات (Firebase Auth / Firestore) بتعدي مباشرة من غير تدخل */
});
