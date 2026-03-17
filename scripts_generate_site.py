#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import html
import json
import re
import shutil

ROOT = Path('.').resolve()
SRC = ROOT / 'letteratura'
OUT = ROOT
AUTHORS_DIR = OUT / 'autori'
ASSETS = OUT / 'assets'

for folder in [AUTHORS_DIR, ASSETS / 'css', ASSETS / 'js', ASSETS / 'images', ASSETS / 'data']:
    folder.mkdir(parents=True, exist_ok=True)

# Clean only generated author pages.
if AUTHORS_DIR.exists():
    for child in AUTHORS_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)


def slugify(value: str) -> str:
    value = value.strip().lower()
    table = str.maketrans({
        'à': 'a', 'á': 'a', 'è': 'e', 'é': 'e', 'ì': 'i', 'í': 'i', 'ò': 'o', 'ó': 'o', 'ù': 'u', 'ú': 'u',
        '’': '', "'": '', '"': ''
    })
    value = value.translate(table)
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-') or 'pagina'


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('#'):
            return s.lstrip('#').strip()
    match = re.search(r'^TIPO:\s*(.+)$', text, flags=re.MULTILINE)
    if match:
        return match.group(1).strip()
    return fallback.replace('-', ' ').replace('_', ' ').strip().title()


def markdown_to_html(markdown: str):
    out: list[str] = []
    headings: list[dict[str, str | int]] = []
    paragraph: list[str] = []
    in_ul = False

    def close_ul_if_open():
        nonlocal in_ul
        if in_ul:
            out.append('</ul>')
            in_ul = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{html.escape(' '.join(paragraph))}</p>")
            paragraph = []

    for raw in markdown.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            flush_paragraph()
            close_ul_if_open()
            continue
        if s.startswith('AUTORE:') or s.startswith('TIPO:'):
            continue
        if re.match(r'^#{1,6}\s+', s):
            flush_paragraph()
            close_ul_if_open()
            level = len(s) - len(s.lstrip('#'))
            text = s[level:].strip()
            hid = slugify(text)
            headings.append({'id': hid, 'title': text, 'level': level})
            out.append(f"<h{level} id=\"{hid}\">{html.escape(text)}</h{level}>")
            continue
        if re.match(r'^[\-*]\s+', s):
            flush_paragraph()
            if not in_ul:
                out.append('<ul>')
                in_ul = True
            item = re.sub(r'^[\-*]\s+', '', s)
            out.append(f"<li>{html.escape(item)}</li>")
            continue
        paragraph.append(s)

    flush_paragraph()
    close_ul_if_open()
    return '\n'.join(out), headings


def rel(current_depth: int, target: str) -> str:
    prefix = '../' * current_depth
    return f"{prefix}{target}"


authors = []
for author_dir in sorted(SRC.iterdir()):
    if not author_dir.is_dir():
        continue
    markdown_files = sorted(author_dir.rglob('*.md'))
    if not markdown_files:
        continue

    author_name = author_dir.name
    author_slug = slugify(author_name)
    lessons = []

    for md in markdown_files:
        content = md.read_text(encoding='utf-8')
        title = extract_title(content, md.stem)
        body_html, headings = markdown_to_html(content)
        words = len(re.findall(r'\w+', content))
        lessons.append({
            'title': title,
            'slug': slugify(md.stem),
            'html': body_html,
            'headings': headings,
            'source': str(md.relative_to(ROOT)),
            'minutes': max(1, round(words / 180)),
        })

    intro = (
        f"Un percorso su {author_name} con lezioni ordinate, materiali originali mantenuti "
        "e interfaccia ottimizzata per studio su desktop, tablet e iPad."
    )
    authors.append({'name': author_name, 'slug': author_slug, 'intro': intro, 'lessons': lessons})

css = """
:root {
  --bg: #f3efe8;
  --surface: #fffdfa;
  --surface-2: #f9f4ea;
  --text: #1d2430;
  --muted: #5f6776;
  --line: #e4d9c6;
  --accent: #87411f;
  --shadow: 0 10px 30px rgba(44, 31, 17, 0.08);
  --max: 78ch;
  --fontScale: 1;
}
[data-theme='dark'] {
  --bg: #0f131a;
  --surface: #181f2a;
  --surface-2: #1f2836;
  --text: #ecf1f9;
  --muted: #acb6c8;
  --line: #2d3747;
  --accent: #d5a66e;
  --shadow: 0 12px 26px rgba(0, 0, 0, 0.35);
}
[data-theme='sepia'] {
  --bg: #f3e9d5;
  --surface: #fff8e9;
  --surface-2: #f8edd8;
  --text: #3f3427;
  --muted: #70604f;
  --line: #e6d3b2;
  --accent: #9f5c1f;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
  background: radial-gradient(circle at top right, var(--surface-2) 0%, var(--bg) 45%);
  color: var(--text);
  font-size: calc(17px * var(--fontScale));
  line-height: 1.68;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.wrap { width: min(1120px, 92%); margin-inline: auto; }
.topbar {
  position: sticky; top: 0; z-index: 50;
  background: color-mix(in srgb, var(--bg), transparent 10%);
  border-bottom: 1px solid var(--line);
  backdrop-filter: blur(10px);
}
.topbar-inner { display: flex; align-items: center; justify-content: space-between; gap: .8rem; padding: .75rem 0; }
.brand { color: var(--text); font-weight: 700; letter-spacing: .2px; }
.controls { display: flex; flex-wrap: wrap; gap: .4rem; justify-content: flex-end; }
button, .btn {
  border: 1px solid var(--line);
  background: var(--surface);
  color: var(--text);
  border-radius: 12px;
  padding: .45rem .75rem;
  cursor: pointer;
}
.hero { padding: 2.5rem 0 1.4rem; }
.hero h1 { margin: 0 0 .35rem; font-size: clamp(1.8rem, 4.5vw, 2.8rem); }
.hero p { margin: 0; color: var(--muted); max-width: 72ch; }
.search { width: 100%; margin-top: 1.1rem; border: 1px solid var(--line); background: var(--surface); color: var(--text); border-radius: 12px; padding: .78rem .9rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(255px, 1fr)); gap: 1rem; }
.card {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, var(--surface), color-mix(in srgb, var(--surface), var(--surface-2) 25%));
  border-radius: 18px;
  padding: 1rem;
  box-shadow: var(--shadow);
}
.cover {
  height: 88px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: linear-gradient(135deg, color-mix(in srgb, var(--accent), white 72%), color-mix(in srgb, var(--surface), var(--accent) 8%));
  margin-bottom: .8rem;
}
.meta { color: var(--muted); font-size: .9rem; }
.main-grid { display: grid; grid-template-columns: 280px 1fr; gap: 1.2rem; }
.sidebar {
  position: sticky; top: 4.4rem; align-self: start;
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: 16px;
  padding: 1rem;
  max-height: 82vh;
  overflow: auto;
}
.content {
  border: 1px solid var(--line);
  background: var(--surface);
  border-radius: 16px;
  padding: 1.35rem;
  max-width: var(--max);
}
.crumbs { color: var(--muted); font-size: .9rem; margin-bottom: .6rem; }
.content h1, .content h2, .content h3 { line-height: 1.28; }
.content p { margin: .75rem 0; }
.content ul { margin: .55rem 0 .9rem 1.2rem; }
.toc a.active { font-weight: 700; text-decoration: underline; }
.lesson-nav { margin-top: 1.2rem; display: flex; justify-content: space-between; gap: .6rem; flex-wrap: wrap; }
.note { width: 100%; min-height: 130px; border-radius: 12px; border: 1px solid var(--line); background: var(--surface-2); color: var(--text); padding: .65rem; }
.footer-note { color: var(--muted); font-size: .9rem; margin: 1.7rem 0 2.1rem; }
#toTop { position: fixed; right: 16px; bottom: 16px; display: none; }
@media (max-width: 920px) {
  .main-grid { grid-template-columns: 1fr; }
  .sidebar { position: static; max-height: none; }
}
""".strip()
(ASSETS / 'css' / 'styles.css').write_text(css, encoding='utf-8')

js = """
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
const m=document.body.dataset.lesson; if(m){try{const d=JSON.parse(m); d.url=location.href; localStorage.setItem('lastLesson',JSON.stringify(d));}catch{}}
const resume=$('#resumeBox'); if(resume){const x=localStorage.getItem('lastLesson'); if(x){try{const d=JSON.parse(x); resume.innerHTML=`<a class='btn' href='${d.url}'>Continua da dove eri rimasto: ${d.title} · ${d.author}</a>`;}catch{}}}
const tocLinks=$$('.toc a'); if(tocLinks.length){const io=new IntersectionObserver((es)=>es.forEach(e=>{if(e.isIntersecting){tocLinks.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id));}}),{rootMargin:'-35% 0px -55% 0px'}); tocLinks.forEach(l=>{const t=$(l.getAttribute('href')); if(t) io.observe(t);});}
const copy=$('#copyLink'); if(copy){copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href); copy.textContent='Link copiato'; setTimeout(()=>copy.textContent='Copia link',1200);}catch{copy.textContent='Copia non disponibile';}});}
if('serviceWorker' in navigator){window.addEventListener('load',()=>{const p=document.body.dataset.sw||'./sw.js'; navigator.serviceWorker.register(p).catch(()=>{});});}
""".strip()
(ASSETS / 'js' / 'app.js').write_text(js, encoding='utf-8')

manifest = {
    'name': 'Letteratura Italiana PWA',
    'short_name': 'Letteratura',
    'start_url': './index.html',
    'display': 'standalone',
    'background_color': '#f3efe8',
    'theme_color': '#87411f',
    'lang': 'it',
    'icons': [
        {'src': './assets/images/icon.svg', 'sizes': 'any', 'type': 'image/svg+xml', 'purpose': 'any maskable'}
    ]
}
(OUT / 'manifest.webmanifest').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')

icon = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect width='512' height='512' rx='92' fill='#87411f'/><path d='M126 132h188a58 58 0 0 1 58 58v194H184a58 58 0 0 0-58 58V132z' fill='#ffefd6'/><path d='M386 132v310a58 58 0 0 0-58-58H140' fill='none' stroke='#3a1a09' stroke-width='18'/></svg>"""
(ASSETS / 'images' / 'icon.svg').write_text(icon, encoding='utf-8')

sw = """
const CACHE='letteratura-pwa-v2';
const CORE=['./','./index.html','./assets/css/styles.css','./assets/js/app.js','./manifest.webmanifest','./assets/images/icon.svg'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim();});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return; e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const c=resp.clone(); caches.open(CACHE).then(cache=>cache.put(e.request,c)); return resp;}).catch(()=>caches.match('./index.html'))));});
""".strip()
(OUT / 'sw.js').write_text(sw, encoding='utf-8')


def page_shell(title: str, content: str, depth: int = 0, body_attrs: str = '') -> str:
    css_href = rel(depth, 'assets/css/styles.css')
    js_href = rel(depth, 'assets/js/app.js')
    manifest_href = rel(depth, 'manifest.webmanifest')
    icon_href = rel(depth, 'assets/images/icon.svg')
    home_href = rel(depth, 'index.html')
    return f"""<!doctype html>
<html lang='it'>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1'>
  <title>{html.escape(title)}</title>
  <meta name='description' content='PWA di letteratura italiana'>
  <link rel='manifest' href='{manifest_href}'>
  <link rel='icon' href='{icon_href}' type='image/svg+xml'>
  <link rel='stylesheet' href='{css_href}'>
  <meta name='theme-color' content='#87411f'>
</head>
<body data-sw='{rel(depth, "sw.js")}' {body_attrs}>
<header class='topbar'>
  <div class='wrap topbar-inner'>
    <a class='brand' href='{home_href}'>Letteratura Italiana · PWA</a>
    <div class='controls'>
      <button onclick="setTheme('light')">Chiaro</button>
      <button onclick="setTheme('dark')">Scuro</button>
      <button onclick="setTheme('sepia')">Seppia</button>
      <button onclick='fontAdjust(.08)'>A+</button>
      <button onclick='fontAdjust(-.08)'>A-</button>
    </div>
  </div>
</header>
{content}
<button id='toTop' class='btn' onclick='window.scrollTo({{top:0,behavior:"smooth"}})'>↑</button>
<script src='{js_href}'></script>
</body>
</html>"""


cards = []
catalog = {'authors': []}
for author in authors:
    author_url = f"autori/{author['slug']}/index.html"
    cards.append(f"""
<article class='card searchable' data-search='{(author['name'] + ' ' + author['intro']).lower()}'>
  <div class='cover' aria-hidden='true'></div>
  <div class='meta'>Autore</div>
  <h3>{html.escape(author['name'])}</h3>
  <p>{html.escape(author['intro'])}</p>
  <a class='btn' href='{author_url}'>Entra</a>
</article>""")
    catalog['authors'].append({
        'name': author['name'],
        'slug': author['slug'],
        'lessons': [{'title': l['title'], 'url': f"autori/{author['slug']}/{l['slug']}.html"} for l in author['lessons']]
    })

home_content = f"""
<main class='wrap'>
  <section class='hero'>
    <h1>Letteratura italiana — archivio didattico</h1>
    <p>Indice generale autori → indice autore → lezione singola. Navigazione chiara, leggibilità elevata e supporto offline.</p>
    <div id='resumeBox' style='margin-top:.95rem;'></div>
    <input id='search' class='search' placeholder='Cerca autore o parola chiave...'>
  </section>
  <section class='grid'>
    {''.join(cards)}
  </section>
  <p class='footer-note'>I contenuti didattici originali nelle cartelle sorgente sono stati mantenuti e solo riformattati per il web.</p>
</main>
"""
(OUT / 'index.html').write_text(page_shell('Letteratura Italiana PWA', home_content, depth=0), encoding='utf-8')

for author in authors:
    folder = AUTHORS_DIR / author['slug']
    folder.mkdir(parents=True, exist_ok=True)
    lesson_rows = []

    for lesson in author['lessons']:
        lesson_rows.append(
            f"<li class='searchable' data-search='{(lesson['title'] + ' ' + author['name']).lower()}'><a href='./{lesson['slug']}.html'>{html.escape(lesson['title'])}</a> <span class='meta'>· {lesson['minutes']} min</span></li>"
        )

    author_content = f"""
<main class='wrap'>
  <section class='hero'>
    <div class='meta'>Autore</div>
    <h1>{html.escape(author['name'])}</h1>
    <p>{html.escape(author['intro'])}</p>
    <input id='search' class='search' placeholder='Filtra lezioni di {html.escape(author['name'])}...'>
  </section>
  <section class='card'>
    <h2>Indice lezioni</h2>
    <ol>{''.join(lesson_rows)}</ol>
  </section>
  <p class='footer-note'><a href='../../index.html'>← Torna all'indice generale</a></p>
</main>
"""
    (folder / 'index.html').write_text(page_shell(f"{author['name']} · indice", author_content, depth=2), encoding='utf-8')

    for i, lesson in enumerate(author['lessons']):
        prev_btn = f"<a class='btn' href='./{author['lessons'][i-1]['slug']}.html'>← Precedente</a>" if i > 0 else '<span></span>'
        next_btn = f"<a class='btn' href='./{author['lessons'][i+1]['slug']}.html'>Successiva →</a>" if i < len(author['lessons']) - 1 else '<span></span>'
        toc = ''.join([f"<li><a href='#{h['id']}'>{html.escape(h['title'])}</a></li>" for h in lesson['headings'] if h['level'] <= 3]) or '<li>Nessun titolo rilevato</li>'

        lesson_content = f"""
<main class='wrap main-grid'>
  <aside class='sidebar'>
    <h3>Indice interno</h3>
    <ol class='toc'>{toc}</ol>
    <h3>Note personali</h3>
    <textarea id='localNote' class='note' placeholder='Scrivi qui le tue note (salvate solo sul tuo dispositivo)'></textarea>
  </aside>
  <article class='content'>
    <div class='crumbs'><a href='../../index.html'>Home</a> / <a href='./index.html'>{html.escape(author['name'])}</a> / {html.escape(lesson['title'])}</div>
    <h1>{html.escape(lesson['title'])}</h1>
    <p class='meta'>Autore: {html.escape(author['name'])} · Tempo di lettura: {lesson['minutes']} min · Fonte: <code>{html.escape(lesson['source'])}</code></p>
    <button id='copyLink' class='btn'>Copia link</button>
    {lesson['html']}
    <div class='lesson-nav'>{prev_btn}<a class='btn' href='./index.html'>Torna all'autore</a>{next_btn}</div>
  </article>
</main>
"""

        lesson_meta = html.escape(json.dumps({'title': lesson['title'], 'author': author['name'], 'url': f"autori/{author['slug']}/{lesson['slug']}.html"}, ensure_ascii=False))
        page = page_shell(f"{lesson['title']} · {author['name']}", lesson_content, depth=2, body_attrs=f"data-lesson='{lesson_meta}'")
        (folder / f"{lesson['slug']}.html").write_text(page, encoding='utf-8')

(ASSETS / 'data' / 'catalog.json').write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding='utf-8')

print(f"Rigenerazione completata: {len(authors)} autori")
