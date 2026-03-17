const CACHE='lit-pwa-v1';
const CORE=['/','/index.html','/assets/css/styles.css','/assets/js/app.js','/manifest.webmanifest','/assets/images/icon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return; e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const c=resp.clone(); caches.open(CACHE).then(cache=>cache.put(e.request,c)); return resp;}).catch(()=>caches.match('/index.html'))));});