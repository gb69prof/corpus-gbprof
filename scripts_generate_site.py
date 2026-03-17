#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re, html, json, shutil

ROOT = Path('.').resolve()
SRC = ROOT / 'letteratura'
OUT = ROOT
ASSETS = OUT / 'assets'
CSS = ASSETS / 'css'
JS = ASSETS / 'js'
IMG = ASSETS / 'images'
DATA = ASSETS / 'data'
AUTHORS_DIR = OUT / 'autori'

for p in [CSS, JS, IMG, DATA, AUTHORS_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# clean generated author pages
if AUTHORS_DIR.exists():
    for child in AUTHORS_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)


def slugify(value: str) -> str:
    value = value.lower().strip()
    repl = {
        'à':'a','è':'e','é':'e','ì':'i','ò':'o','ù':'u','’':'',"'":'', '“':'','”':'',
    }
    for k,v in repl.items():
        value = value.replace(k,v)
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'pagina'


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('#'):
            return s.lstrip('#').strip()
    m = re.search(r'^TIPO:\s*(.+)$', text, re.M)
    if m:
        return m.group(1).strip().title()
    return fallback.replace('-', ' ').replace('_', ' ').strip().title()


def markdown_to_html(md: str):
    lines = md.splitlines()
    out = []
    headings = []
    para = []

    def flush_para():
        nonlocal para
        if para:
            txt = ' '.join(x.strip() for x in para if x.strip())
            if txt:
                out.append(f"<p>{html.escape(txt)}</p>")
            para = []

    for raw in lines:
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush_para();
            continue
        if s.startswith('AUTORE:') or s.startswith('TIPO:'):
            continue
        if re.match(r'#{1,6}\s+', s):
            flush_para()
            level = len(s) - len(s.lstrip('#'))
            text = s[level:].strip()
            hid = slugify(text)
            headings.append({'id': hid, 'title': text, 'level': level})
            out.append(f'<h{level} id="{hid}">{html.escape(text)}</h{level}>')
        elif re.match(r'^[\-*]\s+', s):
            flush_para()
            item = re.sub(r'^[\-*]\s+','',s)
            if not out or not out[-1].startswith('<ul'):
                out.append('<ul>')
            out.append(f'<li>{html.escape(item)}</li>')
        else:
            if out and out[-1] == '</ul>':
                pass
            para.append(s)
    flush_para()

    # fix ul closures
    fixed=[]
    in_ul=False
    for token in out:
        if token == '<ul>':
            if in_ul:
                fixed.append('</ul>')
            in_ul=True
            fixed.append(token)
        elif token.startswith('<li>'):
            if not in_ul:
                fixed.append('<ul>'); in_ul=True
            fixed.append(token)
        else:
            if in_ul:
                fixed.append('</ul>'); in_ul=False
            fixed.append(token)
    if in_ul:
        fixed.append('</ul>')
    return '\n'.join(fixed), headings

authors = []
for d in sorted(SRC.iterdir()):
    if not d.is_dir():
        continue
    md_files = sorted([p for p in d.rglob('*.md')])
    if not md_files:
        continue
    author = d.name
    author_slug = slugify(author)
    lessons = []
    for md_file in md_files:
        rel = md_file.relative_to(ROOT)
        text = md_file.read_text(encoding='utf-8')
        base = md_file.stem
        title = extract_title(text, base)
        lesson_slug = slugify(base)
        lesson_html, headings = markdown_to_html(text)
        words = len(re.findall(r'\w+', re.sub(r'`[^`]*`', '', text)))
        minutes = max(1, round(words/180))
        lessons.append({
            'title': title,
            'slug': lesson_slug,
            'source': str(rel),
            'html': lesson_html,
            'headings': headings,
            'words': words,
            'minutes': minutes,
        })

    if not lessons:
        continue
    intro = f"Percorso dedicato a {author}. Lezioni organizzate in modo progressivo, con materiali originali riformattati per una lettura chiara e consultabile anche offline."
    authors.append({'name': author, 'slug': author_slug, 'intro': intro, 'lessons': lessons})


styles = """
:root{--bg:#f6f2ea;--panel:#fffdf8;--text:#1f2430;--muted:#5f6775;--accent:#8f3e19;--line:#e6ddce;--max:76ch;--fontScale:1}
[data-theme='dark']{--bg:#101319;--panel:#171c25;--text:#e8edf5;--muted:#a5afc2;--accent:#d9a86a;--line:#293140}
[data-theme='sepia']{--bg:#f4ecd8;--panel:#fff8e8;--text:#3e3426;--muted:#6e5f4e;--accent:#9a5c1f;--line:#e7d8bd}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif;background:var(--bg);color:var(--text);font-size:calc(17px * var(--fontScale));line-height:1.65}
a{color:var(--accent);text-decoration:none}.wrap{width:min(1100px,92%);margin:0 auto}.top{position:sticky;top:0;background:color-mix(in srgb,var(--bg),transparent 8%);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);z-index:40}.top .wrap{display:flex;align-items:center;justify-content:space-between;padding:.7rem 0;gap:.8rem}.brand{font-weight:700;color:var(--text)}.controls button{margin-left:.4rem}.btn,button{border:1px solid var(--line);background:var(--panel);color:var(--text);padding:.45rem .75rem;border-radius:10px;cursor:pointer}
.hero{padding:2.5rem 0 1.5rem}.hero h1{font-size:clamp(1.7rem,4vw,2.7rem);margin:.2rem 0}.hero p{color:var(--muted);max-width:70ch}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1rem}.card{background:var(--panel);border:1px solid var(--line);padding:1rem;border-radius:16px;display:flex;flex-direction:column;gap:.6rem}.tag{font-size:.82rem;color:var(--muted)}.search{width:100%;padding:.8rem;border-radius:12px;border:1px solid var(--line);background:var(--panel);color:var(--text);margin:1rem 0 1.4rem}
.main-grid{display:grid;grid-template-columns:250px 1fr;gap:1.2rem}.sidebar{position:sticky;top:4.2rem;align-self:start;background:var(--panel);border:1px solid var(--line);padding:1rem;border-radius:14px;max-height:80vh;overflow:auto}.lesson{max-width:var(--max);background:var(--panel);border:1px solid var(--line);padding:1.4rem;border-radius:16px}.lesson h1,.lesson h2,.lesson h3{line-height:1.3}.crumbs{font-size:.9rem;color:var(--muted);margin-bottom:.8rem}.muted{color:var(--muted)}.lesson-nav{display:flex;justify-content:space-between;gap:.5rem;margin-top:1rem;flex-wrap:wrap}.toc a.active{font-weight:700;text-decoration:underline}.foot{margin:2rem 0;color:var(--muted);font-size:.9rem}.note{width:100%;min-height:120px;background:var(--bg);border:1px solid var(--line);border-radius:12px;padding:.6rem;color:var(--text)}#toTop{position:fixed;right:16px;bottom:18px;display:none}
@media(max-width:860px){.main-grid{grid-template-columns:1fr}.sidebar{position:static;max-height:none}.controls{display:flex;flex-wrap:wrap;justify-content:flex-end}}
""".strip()
(CSS / 'styles.css').write_text(styles, encoding='utf-8')

app_js = """
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
""".strip()
(JS / 'app.js').write_text(app_js, encoding='utf-8')


def layout(title, body, desc='PWA di letteratura italiana'):
    return f"""<!doctype html><html lang='it'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{html.escape(title)}</title><meta name='description' content='{html.escape(desc)}'>
<link rel='manifest' href='/manifest.webmanifest'><link rel='icon' href='/assets/images/icon.svg' type='image/svg+xml'>
<link rel='stylesheet' href='/assets/css/styles.css'><meta name='theme-color' content='#8f3e19'>
</head><body>{body}<button id='toTop' class='btn' onclick='window.scrollTo({{top:0,behavior:"smooth"}})'>↑</button><script src='/assets/js/app.js'></script></body></html>"""

header = """<header class='top'><div class='wrap'><a class='brand' href='/'>Letteratura Italiana · PWA</a><div class='controls'>
<button onclick="setTheme('light')">Chiaro</button><button onclick="setTheme('dark')">Scuro</button><button onclick="setTheme('sepia')">Seppia</button>
<button onclick='fontAdjust(.08)'>A+</button><button onclick='fontAdjust(-.08)'>A-</button></div></div></header>"""

home_cards=[]
catalog={'authors':[]}
for a in authors:
    home_cards.append(f"<article class='card searchable' data-search='{(a['name']+' '+a['intro']).lower()}'><div class='tag'>Autore</div><h3>{html.escape(a['name'])}</h3><p>{html.escape(a['intro'])}</p><a class='btn' href='/autori/{a['slug']}/'>Entra</a></article>")
    catalog['authors'].append({'name':a['name'],'slug':a['slug'],'lessons':[{'title':l['title'],'url':f"/autori/{a['slug']}/{l['slug']}.html"} for l in a['lessons']]})

home_body = header + f"""<main class='wrap'><section class='hero'><h1>Archivio di Letteratura Italiana</h1><p>Indice generale autori → pagine indice → lezioni singole. Esperienza ottimizzata per desktop, tablet, smartphone e uso offline.</p><div id='resumeBox'></div><input id='search' class='search' placeholder='Cerca autore o tema...'></section><section class='grid'>{''.join(home_cards)}</section><p class='foot'>Materiali didattici originali mantenuti e riorganizzati in formato web.</p></main>"""
(OUT / 'index.html').write_text(layout('Letteratura Italiana PWA',home_body), encoding='utf-8')

for a in authors:
    ad = AUTHORS_DIR / a['slug']
    ad.mkdir(parents=True, exist_ok=True)
    lesson_items=[]
    for i,l in enumerate(a['lessons']):
        lesson_items.append(f"<li class='searchable' data-search='{(l['title']+a['name']).lower()}'><a href='/autori/{a['slug']}/{l['slug']}.html'>{html.escape(l['title'])}</a> <span class='muted'>· {l['minutes']} min</span></li>")
    idx_body = header + f"""<main class='wrap'><section class='hero'><div class='tag'>Autore</div><h1>{html.escape(a['name'])}</h1><p>{html.escape(a['intro'])}</p><input id='search' class='search' placeholder='Filtra lezioni di {html.escape(a['name'])}...'></section><section class='card'><h2>Indice lezioni</h2><ol>{''.join(lesson_items)}</ol></section><p class='foot'><a href='/'>← Torna all'indice generale</a></p></main>"""
    (ad/'index.html').write_text(layout(f"{a['name']} · indice", idx_body), encoding='utf-8')

    for i,l in enumerate(a['lessons']):
        prev_link = f"<a class='btn' href='/autori/{a['slug']}/{a['lessons'][i-1]['slug']}.html'>← Precedente</a>" if i>0 else "<span></span>"
        next_link = f"<a class='btn' href='/autori/{a['slug']}/{a['lessons'][i+1]['slug']}.html'>Successiva →</a>" if i < len(a['lessons'])-1 else "<span></span>"
        toc = ''.join([f"<li><a href='#{h['id']}'>{html.escape(h['title'])}</a></li>" for h in l['headings'] if h['level']<=3])
        sidebar = f"<aside class='sidebar'><h3>Indice interno</h3><ol class='toc'>{toc or '<li>Nessun titolo interno rilevato</li>'}</ol><h3>Note</h3><textarea id='localNote' class='note' placeholder='Annotazioni private su questa lezione'></textarea></aside>"
        content = f"<article class='lesson'><div class='crumbs'><a href='/'>Home</a> / <a href='/autori/{a['slug']}/'>{html.escape(a['name'])}</a> / {html.escape(l['title'])}</div><h1>{html.escape(l['title'])}</h1><p class='muted'>Autore: {html.escape(a['name'])} · Tempo di lettura stimato: {l['minutes']} min · Fonte: <code>{html.escape(l['source'])}</code></p><button id='copyLink' class='btn'>Copia link</button>{l['html']}<div class='lesson-nav'>{prev_link}<a class='btn' href='/autori/{a['slug']}/'>Torna all\'autore</a>{next_link}</div></article>"
        main = header + f"<main class='wrap main-grid'>{sidebar}{content}</main>"
        body = layout(f"{l['title']} · {a['name']}", main)
        body = body.replace('<body>', f"<body data-lesson='{html.escape(json.dumps({'title': l['title'], 'author': a['name'], 'url': f'/autori/{a['slug']}/{l['slug']}.html'}))}'>")
        (ad / f"{l['slug']}.html").write_text(body, encoding='utf-8')

(DATA/'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')

(IMG/'icon.svg').write_text("""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect width='512' height='512' rx='100' fill='#8f3e19'/><path d='M122 140h188a60 60 0 0 1 60 60v196H182a60 60 0 0 0-60 60V140z' fill='#fff3e0'/><path d='M390 140v316a60 60 0 0 0-60-60H142' fill='none' stroke='#2f170a' stroke-width='20'/></svg>""",encoding='utf-8')

manifest = {
  'name':'Letteratura Italiana PWA','short_name':'Letteratura','start_url':'/index.html','display':'standalone','background_color':'#f6f2ea','theme_color':'#8f3e19','lang':'it','icons':[{'src':'/assets/images/icon.svg','sizes':'any','type':'image/svg+xml','purpose':'any maskable'}]
}
(OUT/'manifest.webmanifest').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

sw = """
const CACHE='lit-pwa-v1';
const CORE=['/','/index.html','/assets/css/styles.css','/assets/js/app.js','/manifest.webmanifest','/assets/images/icon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return; e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const c=resp.clone(); caches.open(CACHE).then(cache=>cache.put(e.request,c)); return resp;}).catch(()=>caches.match('/index.html'))));});
""".strip()
(OUT/'sw.js').write_text(sw, encoding='utf-8')

print(f"Generated {len(authors)} autori")
