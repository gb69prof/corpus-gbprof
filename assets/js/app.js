const $ = (s,p=document)=>p.querySelector(s);
const $$ = (s,p=document)=>[...p.querySelectorAll(s)];
const root=document.documentElement;

function safeParse(raw,fallback={}){
  if(!raw)return fallback;
  try{return JSON.parse(raw);}catch{return fallback;}
}

function getBasePath(){
  const script=document.currentScript||$('script[src*="assets/js/app.js"]');
  if(script){
    try{
      const u=new URL(script.getAttribute('src')||script.src,location.href);
      return u.pathname.replace(/assets\/js\/app\.js$/, '');
    }catch{}
  }
  const parts=location.pathname.split('/').filter(Boolean);
  return parts.length?`/${parts[0]}/`:'/';
}

const basePath=getBasePath();

function toAppUrl(path=''){
  if(!path)return `${basePath}index.html`;
  if(/^https?:\/\//.test(path))return path;
  const clean=path.replace(/^\.?\/?/, '');
  return `${basePath}${clean}`;
}

const storage={
  get(key){
    try{return localStorage.getItem(key);}catch{return null;}
  },
  set(key,value){
    try{localStorage.setItem(key,value);}catch{}
  }
};

const prefs=safeParse(storage.get('litPrefs'));
if(prefs.theme)root.setAttribute('data-theme',prefs.theme);
if(prefs.fontScale)root.style.setProperty('--fontScale',prefs.fontScale);
function savePrefs(){storage.set('litPrefs',JSON.stringify({theme:root.getAttribute('data-theme')||'light',fontScale:parseFloat(getComputedStyle(root).getPropertyValue('--fontScale'))||1}))}
window.setTheme=(t)=>{root.setAttribute('data-theme',t);savePrefs()}
window.fontAdjust=(d)=>{const cur=parseFloat(getComputedStyle(root).getPropertyValue('--fontScale'))||1;const next=Math.min(1.3,Math.max(.9,cur+d));root.style.setProperty('--fontScale',next);savePrefs()}
const search=$('#search');if(search){search.addEventListener('input',e=>{$$('.searchable').forEach(el=>{const searchableText=(el.dataset.search||el.textContent||'').toLowerCase();el.style.display=searchableText.includes(e.target.value.toLowerCase())?'':'none'})})}
const toTop=$('#toTop'); if(toTop){window.addEventListener('scroll',()=>toTop.style.display=window.scrollY>500?'block':'none')}
const note=$('#localNote'); if(note){const k='note:'+location.pathname; note.value=storage.get(k)||''; note.addEventListener('input',()=>storage.set(k,note.value));}
const lessonMeta=document.body.dataset.lesson;
if(lessonMeta){
  const parsed=safeParse(lessonMeta,null);
  if(parsed)storage.set('lastLesson',JSON.stringify({...parsed,url:location.pathname}));
}
const resume=$('#resumeBox');if(resume){const d=safeParse(storage.get('lastLesson'),null);if(d&&d.url&&d.title&&d.author){resume.innerHTML=`<a class=btn href="${toAppUrl(d.url)}">Continua: ${d.title} · ${d.author}</a>`}}
const tocLinks=$$('.toc a');if(tocLinks.length){const io=new IntersectionObserver((entries)=>{entries.forEach(entry=>{if(entry.isIntersecting){tocLinks.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+entry.target.id))}})},{rootMargin:'-35% 0px -55% 0px'});tocLinks.forEach(l=>{const t=$(l.getAttribute('href'));if(t)io.observe(t)})}
const copy=$('#copyLink'); if(copy){copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);copy.textContent='Link copiato'}catch{copy.textContent='Copia non disponibile'}setTimeout(()=>copy.textContent='Copia link',1300)})}
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register(`${basePath}sw.js`,{scope:basePath}))}
