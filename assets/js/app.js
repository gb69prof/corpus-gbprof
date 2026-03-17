const $ = (s,p=document)=>p.querySelector(s);
const $$ = (s,p=document)=>[...p.querySelectorAll(s)];
const root=document.documentElement;
const prefs=JSON.parse(localStorage.getItem('litPrefs')||'{}');
if(prefs.theme) root.setAttribute('data-theme',prefs.theme);
if(prefs.fontScale) root.style.setProperty('--fontScale',prefs.fontScale);
const save=()=>localStorage.setItem('litPrefs',JSON.stringify({theme:root.getAttribute('data-theme')||'light',fontScale:parseFloat(getComputedStyle(root).getPropertyValue('--fontScale'))||1}));
window.setTheme=(t)=>{root.setAttribute('data-theme',t);save();};
window.fontAdjust=(d)=>{const n=Math.max(.9,Math.min(1.35,(parseFloat(getComputedStyle(root).getPropertyValue('--fontScale'))||1)+d));root.style.setProperty('--fontScale',n);save();};
const search=$('#search'); if(search){search.addEventListener('input',e=>{$$('.searchable').forEach(el=>el.style.display=el.dataset.search.includes(e.target.value.toLowerCase())?'':'none');});}
const toTop=$('#toTop'); if(toTop){window.addEventListener('scroll',()=>toTop.style.display=window.scrollY>450?'block':'none');}
const note=$('#localNote'); if(note){const k='note:'+location.pathname; note.value=localStorage.getItem(k)||''; note.addEventListener('input',()=>localStorage.setItem(k,note.value));}
const m=document.body.dataset.lesson; if(m) localStorage.setItem('lastLesson',m);
const resume=$('#resumeBox'); if(resume){const x=localStorage.getItem('lastLesson'); if(x){const d=JSON.parse(x); resume.innerHTML=`<a class='btn' href='${d.url}'>Continua da dove eri rimasto: ${d.title} · ${d.author}</a>`;}}
const tocLinks=$$('.toc a'); if(tocLinks.length){const io=new IntersectionObserver((es)=>es.forEach(e=>{if(e.isIntersecting){tocLinks.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id));}}),{rootMargin:'-35% 0px -55% 0px'}); tocLinks.forEach(l=>{const t=$(l.getAttribute('href')); if(t) io.observe(t);});}
const copy=$('#copyLink'); if(copy){copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href); copy.textContent='Link copiato'; setTimeout(()=>copy.textContent='Copia link',1200);}catch{copy.textContent='Copia non disponibile';}});}
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('/sw.js').catch(()=>{}));}