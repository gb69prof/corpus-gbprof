const $ = (s,p=document)=>p.querySelector(s);
const $$ = (s,p=document)=>[...p.querySelectorAll(s)];
const root=document.documentElement;
const prefs=JSON.parse(localStorage.getItem('litPrefs')||'{}');
if(prefs.theme)root.setAttribute('data-theme',prefs.theme);
if(prefs.fontScale)root.style.setProperty('--fontScale',prefs.fontScale);
function savePrefs(){localStorage.setItem('litPrefs',JSON.stringify({theme:root.getAttribute('data-theme')||'light',fontScale:parseFloat(getComputedStyle(root).getPropertyValue('--fontScale'))||1}))}
window.setTheme=(t)=>{root.setAttribute('data-theme',t);savePrefs()}
window.fontAdjust=(d)=>{const cur=parseFloat(getComputedStyle(root).getPropertyValue('--fontScale'))||1;const next=Math.min(1.3,Math.max(.9,cur+d));root.style.setProperty('--fontScale',next);savePrefs()}
const search=$('#search');if(search){search.addEventListener('input',e=>{$$('.searchable').forEach(el=>{el.style.display=el.dataset.search.includes(e.target.value.toLowerCase())?'':'none'})})}
const toTop=$('#toTop'); if(toTop){window.addEventListener('scroll',()=>toTop.style.display=window.scrollY>500?'block':'none')}
const note=$('#localNote'); if(note){const k='note:'+location.pathname; note.value=localStorage.getItem(k)||''; note.addEventListener('input',()=>localStorage.setItem(k,note.value));}
const lessonMeta=document.body.dataset.lesson;if(lessonMeta){localStorage.setItem('lastLesson',lessonMeta)}
const resume=$('#resumeBox');if(resume){const raw=localStorage.getItem('lastLesson');if(raw){const d=JSON.parse(raw);resume.innerHTML=`<a class=btn href="${d.url}">Continua: ${d.title} · ${d.author}</a>`}}
const tocLinks=$$('.toc a');if(tocLinks.length){const io=new IntersectionObserver((entries)=>{entries.forEach(entry=>{if(entry.isIntersecting){tocLinks.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+entry.target.id))}})},{rootMargin:'-35% 0px -55% 0px'});tocLinks.forEach(l=>{const t=$(l.getAttribute('href'));if(t)io.observe(t)})}
const copy=$('#copyLink'); if(copy){copy.addEventListener('click',async()=>{await navigator.clipboard.writeText(location.href);copy.textContent='Link copiato';setTimeout(()=>copy.textContent='Copia link',1300)})}
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js'))}