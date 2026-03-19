const CACHE='lit-pwa-v2';

const scopeUrl=new URL(self.registration.scope);
const BASE=scopeUrl.pathname.endsWith('/')?scopeUrl.pathname:`${scopeUrl.pathname}/`;
const CORE=['index.html','assets/css/styles.css','assets/js/app.js','manifest.webmanifest','assets/images/icon.svg'].map(p=>new URL(p,scopeUrl).toString());

self.addEventListener('install',e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)));
  self.skipWaiting();
});

self.addEventListener('activate',e=>{
  e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));
  self.clients.claim();
});

self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const reqUrl=new URL(e.request.url);
  if(reqUrl.origin!==location.origin)return;

  const isDoc=e.request.mode==='navigate';
  if(isDoc){
    e.respondWith(fetch(e.request).then(resp=>{
      const copy=resp.clone();
      caches.open(CACHE).then(cache=>cache.put(e.request,copy));
      return resp;
    }).catch(()=>caches.match(e.request).then(r=>r||caches.match(new URL('index.html',scopeUrl).toString()))));
    return;
  }

  e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request).then(resp=>{
    if(resp && resp.ok){
      const copy=resp.clone();
      caches.open(CACHE).then(cache=>cache.put(e.request,copy));
    }
    return resp;
  })));
});
