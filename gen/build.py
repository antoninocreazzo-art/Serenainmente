#!/usr/bin/env python3
"""Genera il sito serenainmente.it (versione magazine, ottobre 2026) da gen/dati.json.
Il gestionale NON si rigenera qui: python3 gen/gestionale.py e poi ricalcolo con LibreOffice.
Uso:
  ANTEPRIMA:  OUT=/percorso/anteprima LINKS=rel python3 gen/build.py
  SITO:       python3 gen/build.py            (scrive nella cartella del sito)
Le foto vanno in assets/foto/<chiave>.webp (hero, chi, articoli, <slug-guida>): se mancano
compare un riquadro colorato con il segno di Serena."""
import json, os, re, html, datetime, shutil, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('OUT', ROOT)
REL = os.environ.get('LINKS') == 'rel'
PREVIEW = OUT != ROOT
D = json.load(open(os.path.join(ROOT, 'gen', 'dati.json'), encoding='utf-8'))
SITE = 'https://serenainmente.it'
IG = 'https://www.instagram.com/serenainmente/'
MAIL = 'serenainmente@gmail.com'
e = html.escape
MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
def data_it(s):
    d = datetime.date.fromisoformat(s); return f"{d.day} {MESI[d.month-1]} {d.year}"

# ---------- argomenti ----------
ARG = [
    ('salute', 'Salute e visite', 'Pediatra, specialisti, ricette e prenotazioni', 'steth', 't-salvia'),
    ('documenti', 'Documenti e burocrazia', 'Fascicolo sanitario, scelte, cambi e moduli', 'folder', 't-rosa'),
    ('organizzazione', 'Organizzazione e quotidianità', 'Cartellina, scadenze e settimana di famiglia', 'calendar', 't-malva'),
    ('crescita', 'Bambini e crescita', 'Sonno, routine e piccoli passi', 'sprout', 't-sabbia'),
]
ARGN = {a[0]: a for a in ARG}
GUIDA_ARG = {'domande-per-il-pediatra': 'salute', 'visita-specialistica-come-funziona': 'salute',
             'spostare-disdire-pagare-visita': 'salute', 'documenti-sanitari-dove-trovarli': 'documenti',
             'pediatra-e-medico-di-base': 'documenti', 'cartellina-di-famiglia': 'organizzazione',
             'routine-della-nanna': 'crescita'}
for g in D['guide']:
    g['arg'] = g.get('argomento') or GUIDA_ARG.get(g['slug'], 'organizzazione')
    testo = ' '.join([g['titolo'], g['sommario']] + g['perche'] + [a + ' ' + b for a, b in g['passi']] + g.get('errori', []) + g.get('checklist', []))
    g['min'] = max(2, round(len(testo.split()) / 200))
GUIDE = sorted(D['guide'], key=lambda g: g['data'], reverse=True)

# ---------- icone (linea, 24px) ----------
P = {
 'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
 'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
 'close': '<path d="M6 6l12 12M18 6 6 18"/>',
 'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 'arrow': '<path d="M5 12h14M13 6l6 6-6 6"/>',
 'insta': '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".8" fill="currentColor"/>',
 'book': '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
 'list': '<path d="M11 6h10M11 12h10M11 18h10"/><path d="m3 6 1.5 1.5L7 5M3 12l1.5 1.5L7 11M3 18l1.5 1.5L7 17"/>',
 'lock': '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
 'leaf': '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.1-6 2.4-.5 4.9-2 5.9-3"/>',
 'steth': '<path d="M5 3v6a5 5 0 0 0 10 0V3"/><path d="M10 14v2a5 5 0 0 0 10 0v-2"/><circle cx="20" cy="12" r="2"/>',
 'folder': '<path d="M3 6.5A2.5 2.5 0 0 1 5.5 4H9l2 2.5h7.5A2.5 2.5 0 0 1 21 9v8.5a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/>',
 'calendar': '<rect x="3" y="5" width="18" height="16" rx="2.5"/><path d="M16 3v4M8 3v4M3 10h18"/>',
 'sprout': '<path d="M7 21h10M12 21v-9"/><path d="M12 12c0-3.5 2.3-6 7-6 0 3.5-2.3 6-7 6Z"/><path d="M12 14c0-2.8-1.9-4.5-5.5-4.5 0 2.8 1.9 4.5 5.5 4.5Z"/>',
 'download': '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
 'check': '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
 'person': '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
 'mail': '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/>',
}
def ic(n, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[n]}</svg>'

# ---------- foto o riquadro ----------
TONI = ['rosa', 'salvia', 'sabbia', 'crema']
def foto(key, alt, cls='', tone=None, eager=False):
    if os.path.exists(os.path.join(ROOT, 'assets', 'foto', f'{key}.webp')):
        return (f'<img class="ph {cls}" src="~/assets/foto/{key}.webp" srcset="~/assets/foto/{key}-sm.webp 768w, ~/assets/foto/{key}.webp 1536w" '
                f'sizes="(min-width:900px) 50vw, 100vw" width="1536" height="1024" alt="{e(alt)}" {"" if eager else "loading=lazy"} decoding="async">')
    t = tone or TONI[sum(map(ord, key)) % len(TONI)]
    sun = ('<svg viewBox="0 0 200 120" aria-hidden="true"><path d="M58 78a42 42 0 0 1 84 0" fill="currentColor" opacity=".55"/>'
           '<path d="M40 80h120" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>'
           '<path d="M70 94h60" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity=".6"/></svg>')
    return f'<div class="ph ph-{t} {cls}" role="img" aria-label="{e(alt)}">{sun}</div>'

# ---------- pagina ----------
UMAMI = '<script defer src="https://cloud.umami.is/script.js" data-website-id="301edcb4-f5b2-444e-a1e5-8b8614d0100a" data-domains="serenainmente.it"></script>'
LOGO = '<img class="logo-mark" src="~/assets/brand/mark-96.png" alt="" width="36" height="36"><span>serenainmente</span>'
NAV = [('/guide/', 'Articoli e guide'), ('/risorse/', 'Risorse gratuite'), ('/chi-e-serena/', 'Chi è Serena'), ('/metodo/', 'Il nostro metodo')]

JS = r"""<script>
(function(){
var mobile=matchMedia('(pointer:coarse)').matches||/Android|iPhone|iPad/i.test(navigator.userAgent);
if(navigator.share&&mobile){
 document.querySelectorAll('[data-share]').forEach(function(b){b.hidden=false;b.onclick=function(){navigator.share({title:b.dataset.title,text:b.dataset.title,url:b.dataset.url}).catch(function(x){if(x&&x.name!=='AbortError')open('https://wa.me/?text='+encodeURIComponent(b.dataset.title+' '+b.dataset.url))})}});
 document.querySelectorAll('[data-sharetext]').forEach(function(b){b.hidden=false;b.onclick=function(){navigator.share({text:b.dataset.sharetext}).catch(function(){})}});
}
document.querySelectorAll('[data-copytext]').forEach(function(b){b.onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copytext).then(function(){b.textContent=b.dataset.done||'Copiato'})}});
try{document.querySelectorAll('input[data-ck]').forEach(function(c){var k='ck:'+c.dataset.ck;c.checked=localStorage.getItem(k)==='1';c.onchange=function(){localStorage.setItem(k,c.checked?'1':'0')}})}catch(x){}
// comparsa leggera delle sezioni
if('IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
 var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target)}})},{rootMargin:'0px 0px -8% 0px'});
 document.querySelectorAll('.rv').forEach(function(el){io.observe(el)});
}else{document.querySelectorAll('.rv').forEach(function(el){el.classList.add('in')})}
// frase che cambia in home, con «Vedi tutte»
var R=document.querySelector('[data-rot]');
if(R){
 var L=R.querySelectorAll('a'),k=0,stop=false,open=false,B=document.querySelector('.rot-all'),U=document.getElementById('tutte-domande');
 B.hidden=false;
 B.onclick=function(){open=!open;U.hidden=!open;R.hidden=open;B.setAttribute('aria-expanded',open);B.textContent=open?'Chiudi':'Vedi tutte'};
 if(!matchMedia('(prefers-reduced-motion: reduce)').matches){
  R.addEventListener('mouseenter',function(){stop=true});R.addEventListener('mouseleave',function(){stop=false});
  R.addEventListener('focusin',function(){stop=true});R.addEventListener('focusout',function(){stop=false});
  setInterval(function(){if(stop||open||document.hidden)return;var a=L[k];a.classList.add('out');
   setTimeout(function(){a.hidden=true;a.classList.remove('out');k=(k+1)%L.length;var b=L[k];b.classList.add('in0');b.hidden=false;
    requestAnimationFrame(function(){requestAnimationFrame(function(){b.classList.remove('in0')})})},380)},3400);
 }
}
// filtri e ricerca negli articoli
var grid=document.querySelector('[data-grid]');
if(grid){
 var q=document.querySelector('[data-q]'),chips=document.querySelectorAll('[data-arg]'),none=document.querySelector('[data-none]'),cur='tutti';
 var p=new URLSearchParams(location.search);if(p.get('q'))q.value=p.get('q');if(location.hash.length>1)cur=location.hash.slice(1);
 function run(){var t=(q.value||'').toLowerCase().trim(),n=0;
  grid.querySelectorAll('[data-a]').forEach(function(c){var ok=(cur==='tutti'||c.dataset.a===cur)&&(!t||c.dataset.t.indexOf(t)>-1);c.hidden=!ok;if(ok)n++});
  chips.forEach(function(ch){ch.setAttribute('aria-pressed',ch.dataset.arg===cur)});none.hidden=n>0}
 chips.forEach(function(ch){ch.onclick=function(){cur=ch.dataset.arg;history.replaceState(null,'',cur==='tutti'?location.pathname+location.search:'#'+cur);run()}});
 q.oninput=run;run();
}
})();
</script>"""

def page(path, title, desc, body, ld=None, cls=''):
    canon = SITE + path
    t = 'serenainmente · Serena, parole e idee per chi si prende cura della famiglia' if path == '/' else f'{title} · serenainmente'
    if path == '/' and not ld:
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebSite", "name": "serenainmente", "alternateName": ["Serena", "Serena in mente"], "url": SITE + "/"},
            {"@type": "Organization", "name": "Serena", "alternateName": "serenainmente", "url": SITE + "/",
             "logo": SITE + "/assets/brand/avatar-320.png", "sameAs": [IG]}]}
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''
    navl = ''.join(f'<a href="~{h}"{" aria-current=page" if path.startswith(h) else ""}>{l}</a>' for h, l in NAV)
    banner = '<div class="preview-bar">Anteprima del nuovo sito · non ancora pubblicata</div>' if PREVIEW else ''
    out = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(t)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="{'article' if path.startswith('/guide/') and path != '/guide/' else 'website'}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="it_IT">
<meta name="theme-color" content="#F8F4EF">
<meta name="google-site-verification" content="urb5XcUNd0QsSnqqtO49dSjLHeByMvfosPu2Gs2IMlY">
<link rel="icon" type="image/png" href="~/assets/brand/favicon-48.png">
<link rel="apple-touch-icon" href="~/assets/brand/apple-touch-icon.png">
<link rel="stylesheet" href="~/assets/stile2.css">
<script>document.documentElement.className='js'</script>
{'' if PREVIEW else UMAMI}
{ldj}
</head>
<body class="{cls}">
{banner}
<a class="skip" href="#contenuto">Vai al contenuto</a>
<header class="hd">
<div class="hd-in">
<a class="brand" href="~/" aria-label="serenainmente, pagina iniziale">{LOGO}</a>
<nav class="nav-d" aria-label="Menu principale">{navl}</nav>
<div class="hd-act">
<a class="icbtn" href="~/guide/#cerca" aria-label="Cerca negli articoli">{ic('search')}</a>
<a class="btn btn-sm btn-line ig-d" href="{IG}" rel="noopener" data-umami-event="instagram">{ic('insta')}Instagram</a>
<details class="mnav"><summary aria-label="Apri il menu"><span class="o">{ic('menu')}</span><span class="c">{ic('close')}</span></summary>
<nav aria-label="Menu">{navl}<a href="~/fonti/">Le fonti</a><a class="mig" href="{IG}" rel="noopener" data-umami-event="instagram">{ic('insta')} Seguici su Instagram</a></nav></details>
</div>
</div>
</header>
<main id="contenuto">
{body}
</main>
<footer class="ft">
<div class="ft-in">
<div class="ft-brand"><a class="brand" href="~/">{LOGO}</a><p>Guide pratiche con le loro fonti, strumenti gratuiti e parole in cui ritrovarsi, per chi si prende cura della famiglia.</p>
<a class="ft-ig" href="{IG}" rel="noopener" data-umami-event="instagram">{ic('insta')} @serenainmente</a></div>
<div><h2>Esplora</h2><ul><li><a href="~/guide/">Articoli e guide</a></li><li><a href="~/risorse/">Risorse gratuite</a></li><li><a href="~/gestionale/">Il gestionale di famiglia</a></li></ul></div>
<div><h2>Serena</h2><ul><li><a href="~/chi-e-serena/">Chi è Serena</a></li><li><a href="~/metodo/">Il nostro metodo</a></li><li><a href="~/fonti/">Le fonti</a></li><li><a href="~/privacy/">Privacy</a></li><li><a href="~/note-legali/">Note legali</a></li></ul></div>
<div><h2>Contatti</h2><ul><li><a href="mailto:{MAIL}">{MAIL}</a></li><li><a href="{IG}" rel="noopener">Messaggio su Instagram</a></li></ul></div>
</div>
<div class="ft-low"><p>Serena è ideata e curata da una persona, con supporto AI per testi, immagini e verifica delle fonti. Informazioni generali: non sostituiscono il parere del pediatra o del medico.</p>
<p>Questo sito non usa cookie e non raccoglie dati personali. © {datetime.date.today().year} serenainmente.it</p></div>
</footer>
{JS}
</body>
</html>
'''
    rel = '../' * len([x for x in path.strip('/').split('/') if x])
    def fix(m):
        attr, p = m.group(1), m.group(2)
        if not REL:
            return f'{attr}="/{p}'
        if p == '' or p.startswith('#'):
            return f'{attr}="{rel}index.html{p}'
        if re.match(r'[^?#]*/(\?|#|$)', p):
            base, _, tail = re.match(r'([^?#]*/)([?#]?)(.*)', p).groups()
            return f'{attr}="{rel}{base}index.html{_}{tail}'
        return f'{attr}="{rel}{p}'
    out = re.sub(r'(href|srcset|src|poster)="~/([^"]*)', fix, out)
    out = out.replace(' ~/assets/', ' ' + ('../' * len([x for x in path.strip('/').split('/') if x]) if REL else '/') + 'assets/')
    full = os.path.join(OUT, path.strip('/'), 'index.html') if path != '/' else os.path.join(OUT, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(out)
    return path

FONTI = {f['id']: f for f in D['fonti']}
def src_block(fid):
    f = FONTI[fid]; dom = f['url'].split('/')[2].replace('www.', '')
    return f'''<li class="src"><span class="org">{e(f['ente'])}, {e(str(f['anno']))}</span><span class="ttl">{e(f['titolo'])}</span><span class="type">{e(f['tipo'])}</span><a href="{e(f['url'])}" rel="noopener">Apri la fonte su {e(dom)} {ic('arrow','ic-s')}</a></li>'''

def share(path, title):
    url = SITE + path
    wa = 'https://wa.me/?text=' + e(urllib.parse.quote(f"{title} {url}"))
    return f'''<div class="share"><p>Ti è utile? Mandala a chi ne ha bisogno.</p>
<div class="row"><button class="btn" type="button" hidden data-share data-umami-event="condividi" data-title="{e(title)}" data-url="{url}">Condividi o salva in Note</button><a class="btn btn-line" href="{wa}" rel="noopener" data-umami-event="whatsapp">Manda su WhatsApp</a><button class="btn btn-line" type="button" data-copytext="{url}" data-done="Link copiato" data-umami-event="copia-link">Copia il link</button></div></div>'''

def card(g, eager=False):
    a = ARGN[g['arg']]
    t = e((g['titolo'] + ' ' + g['sommario'] + ' ' + a[1]).lower())
    return f'''<a class="acard" href="~/guide/{g['slug']}/" data-a="{g['arg']}" data-t="{t}">{foto(g['slug'], '', 'ac-img', eager=eager)}
<div class="ac-b"><span class="chip c-{a[4]}">{e(a[1])}</span><h3>{e(g['titolo'])}</h3><p>{e(g['sommario'])}</p>
<span class="meta">{ic('clock','ic-s')} {g['min']} min di lettura <span aria-hidden="true">·</span> {data_it(g['data'])}</span></div></a>'''

VALORI = [('book', 'Fonti aperte', 'Ogni dato con la sua fonte, da aprire'),
          ('list', 'Approccio pratico', 'Cose da fare oggi, in pochi minuti'),
          ('lock', 'Privacy rispettata', 'Niente cookie, niente profilazione'),
          ('leaf', 'Nessuna pubblicità', 'Nessuno sponsor dietro i consigli')]
def valori(cls=''):
    return f'<ul class="values {cls}" aria-label="I valori di Serena">' + ''.join(f'<li><span class="vic">{ic(i)}</span><span><b>{t}</b><small>{s}</small></span></li>' for i, t, s in VALORI) + '</ul>'

IGCARD = f'''<a class="igcard" href="{IG}" rel="noopener" data-umami-event="instagram"><img src="~/assets/brand/avatar-160.png" alt="Immagine del profilo Instagram di Serena: un sole che sorge" width="64" height="64"><span><b>@serenainmente</b><small>Ogni mattina alle 10 su Instagram</small></span><span class="go">Segui {ic('arrow','ic-s')}</span></a>'''

GEST = '~/scarica/gestionale-di-famiglia.xlsx'
SHEETS = D.get('gestionale_sheets_url')
def devices(cls=''):
    return f'''<div class="devices {cls}" aria-hidden="true">
<div class="laptop"><div class="scr"><img src="~/assets/gestionale/inizia.webp" alt="" loading="lazy"></div><div class="base"></div></div>
<div class="phone"><div class="pscr"><img src="~/assets/gestionale/inizia-telefono.webp" alt="" loading="lazy"></div></div>
</div>'''
GEST_PUNTI = ['Prima gli impegni: cosa, quando e per chi', 'Scrivi una volta, si aggiorna ovunque',
              'Funziona con Excel, Fogli Google e Numbers', 'Gratuito, e i tuoi dati restano tuoi']

pages = []

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
def checklist_xlsx(g):
    """Crea guide/<slug>/checklist.xlsx con la checklist della guida."""
    wb = Workbook(); ws = wb.active; ws.title = 'Checklist'
    malva, ink, rosa = '97606F', '3A2C30', 'F4E9EC'
    ws.column_dimensions['A'].width = 8; ws.column_dimensions['B'].width = 60; ws.column_dimensions['C'].width = 28
    ws['A1'] = g['titolo']; ws['A1'].font = Font(name='Georgia', size=16, bold=True, color=ink); ws.merge_cells('A1:C1')
    ws['A2'] = g['sommario']; ws['A2'].font = Font(size=11, italic=True, color='7A6569'); ws.merge_cells('A2:C2')
    ws.row_dimensions[1].height = 28; ws.row_dimensions[2].height = 20
    for col, t in zip('ABC', ['Fatto', 'Cosa', 'Note']):
        c = ws[f'{col}4']; c.value = t; c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=malva)
        c.alignment = Alignment(vertical='center'); ws.row_dimensions[4].height = 22
    thin = Side(style='thin', color='EADCDF')
    dv = DataValidation(type='list', formula1='"☐,☑"', allow_blank=True); ws.add_data_validation(dv)
    for i, item in enumerate(g.get('checklist', []), start=5):
        ws[f'A{i}'] = '☐'; ws[f'A{i}'].alignment = Alignment(horizontal='center', vertical='center'); ws[f'A{i}'].font = Font(size=14, color=malva)
        ws[f'B{i}'] = item; ws[f'B{i}'].alignment = Alignment(wrap_text=True, vertical='center'); ws.row_dimensions[i].height = 24
        dv.add(ws[f'A{i}'])
        for col in 'ABC':
            ws[f'{col}{i}'].border = Border(bottom=thin)
            if i % 2: ws[f'{col}{i}'].fill = PatternFill('solid', fgColor='FBF6F4')
    n = 5 + len(g.get('checklist', [])) + 1
    ws[f'B{n}'] = f"Da serenainmente.it/guide/{g['slug']}/ · {g['avvertenza']}"; ws[f'B{n}'].font = Font(size=9, color='7A6569'); ws[f'B{n}'].alignment = Alignment(wrap_text=True); ws.merge_cells(f'B{n}:C{n}'); ws.row_dimensions[n].height = 40
    ws.freeze_panes = 'A5'; ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = 'portrait'; ws.page_setup.fitToWidth = 1; ws.print_options.horizontalCentered = True
    d = os.path.join(ROOT, 'guide', g['slug']); os.makedirs(d, exist_ok=True)
    wb.save(os.path.join(d, 'checklist.xlsx'))


# ---------- guide (articoli) ----------
for g in GUIDE:
    a = ARGN[g['arg']]
    if g.get('checklist'): checklist_xlsx(g)
    steps = ''.join(f'<li><b>{e(s[0])}</b><span>{e(s[1])}</span></li>' for s in g['passi'])
    errori = ''.join(f'<li>{e(x)}</li>' for x in g.get('errori', []))
    check = ''.join(f'<li><label><input type="checkbox" data-ck="{g["slug"]}-{i}"><span class="cbx" aria-hidden="true">{ic("check","ic-s")}</span><span>{e(x)}</span></label></li>' for i, x in enumerate(g.get('checklist', [])))
    cktext = e(g['titolo'] + ' · checklist\n' + '\n'.join('☐ ' + x for x in g.get('checklist', [])) + '\nserenainmente.it/guide/' + g['slug'] + '/')
    fonti = ''.join(src_block(fid) for fid in g.get('fonti', []))
    nf = len(g.get('fonti', []))
    corr = [x for x in GUIDE if x is not g and x['arg'] == g['arg']] + [x for x in GUIDE if x is not g and x['arg'] != g['arg']]
    body = f'''<article class="art">
<header class="art-hd wrap-m">
<nav class="crumbs" aria-label="Percorso"><a href="~/guide/">Articoli e guide</a> <span aria-hidden="true">›</span> <a href="~/guide/#{a[0]}">{e(a[1])}</a></nav>
<span class="chip c-{a[4]}">{e(a[1])}</span>
<h1>{e(g['titolo'])}</h1>
<p class="lead">{e(g['sommario'])}</p>
<p class="meta">{ic('clock','ic-s')} {g['min']} min di lettura <span aria-hidden="true">·</span> Aggiornata il {data_it(g['data'])}{f' <span aria-hidden="true">·</span> {nf} {"fonte" if nf == 1 else "fonti"}' if nf else ''}</p>
</header>
<div class="wrap-m">{foto(g['slug'], '', 'art-img', eager=True)}</div>
<div class="art-body wrap-t">
<dl class="facts"><div><dt>Tempo</dt><dd>{e(g['tempo'])}</dd></div><div><dt>Cosa serve</dt><dd>{e(g['serve'])}</dd></div></dl>
<section><h2>Perché aiuta</h2>{''.join(f'<p>{e(p)}</p>' for p in g['perche'])}</section>
<section><h2>Come si fa</h2><ol class="steps">{steps}</ol></section>
{f'<section class="box box-rosa"><h2>Errori comuni</h2><ul class="plain">{errori}</ul></section>' if errori else ''}
{f'<section class="box box-salvia ck"><h2>Checklist</h2><ul class="check">{check}</ul><p class="small">Spunta qui: le spunte restano salvate su questo telefono o computer.</p><div class="row noprint"><button class="btn" type="button" hidden data-sharetext="{cktext}" data-umami-event="checklist-note">Salva in Note o Promemoria</button><button class="btn btn-line" type="button" data-copytext="{cktext}" data-done="Lista copiata" data-umami-event="checklist-copia">Copia la lista</button><a class="btn btn-line" href="~/guide/{g["slug"]}/checklist.xlsx" download data-umami-event="checklist-excel" data-umami-event-guida="{g["slug"]}">{ic("download","ic-s")} Excel</a><button class="btn btn-line" type="button" onclick="print()" data-umami-event="checklist-stampa">Stampa</button></div></section>' if check else ''}
{f'<section><h2>Fonti</h2><ul class="sources">{fonti}</ul></section>' if fonti else ''}
<aside class="box box-line"><b>Da sapere</b><p>{e(g['avvertenza'])}</p></aside>
{share(f"/guide/{g['slug']}/", g['titolo'])}
</div>
<section class="related wrap"><div class="sec-hd"><h2>Continua a leggere</h2><a class="more" href="~/guide/">Tutti gli articoli {ic('arrow','ic-s')}</a></div>
<div class="grid3">{''.join(card(x) for x in corr[:3])}</div></section>
</article>'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": g['titolo'], "description": g['sommario'],
          "datePublished": g['data'], "dateModified": g['data'], "inLanguage": "it", "articleSection": a[1],
          "author": {"@type": "Organization", "name": "Serena"},
          "publisher": {"@type": "Organization", "name": "Serena", "logo": {"@type": "ImageObject", "url": SITE + "/assets/brand/avatar-320.png"}}}
    pages.append(page(f"/guide/{g['slug']}/", g['titolo'], g['sommario'], body, ld))

# ---------- articoli e guide ----------
argc = {a[0]: sum(1 for g in GUIDE if g['arg'] == a[0]) for a in ARG}
chips = '<button type="button" class="fchip" data-arg="tutti" aria-pressed="true">Tutti</button>' + ''.join(
    f'<button type="button" class="fchip" data-arg="{a[0]}" aria-pressed="false">{e(a[1])}</button>' for a in ARG if argc[a[0]])
pages.append(page('/guide/', 'Articoli e guide', 'Guide pratiche e approfondimenti per la vita di famiglia, con le fonti quando servono.', f'''
<section class="ph-hd wrap">
<div class="ph-txt"><h1>Articoli e guide</h1><p class="lead">Piccoli metodi per giornate più leggere e le regole che nessuno ti spiega, con le fonti quando servono.</p></div>
{foto('articoli', '', 'ph-deco', tone='salvia')}
</section>
<section class="wrap list">
<div class="filters" id="cerca">
<label class="search">{ic('search')}<span class="sr">Cerca negli articoli</span><input type="search" data-q placeholder="Cerca: pediatra, ticket, nanna…" autocomplete="off"></label>
<div class="fchips" role="group" aria-label="Filtra per argomento">{chips}</div>
</div>
<div class="grid3" data-grid>{''.join(card(g, eager=i < 3) for i, g in enumerate(GUIDE))}</div>
<p class="none" data-none hidden>Nessun articolo trovato. Prova con un'altra parola o scegli «Tutti».</p>
</section>''', cls='p-list'))

# ---------- gestionale ----------
sheets_btn = f'<a class="btn btn-line" href="{e(SHEETS)}" rel="noopener" data-umami-event="gestionale-fogli">Apri in Fogli Google</a>' if SHEETS else ''
SCHEDE = [('Inizia da qui', 'Appena lo apri: le scadenze dei prossimi 30 giorni, le visite delle prossime due settimane, i documenti da rinnovare e la lista dei prossimi impegni, dal più vicino. Più sotto, quello che è rimasto indietro.'),
          ('Famiglia', 'I nomi di casa, scritti una volta sola: diventano il menu di tutte le altre schede. L\'età si calcola dalla data di nascita.'),
          ('Scadenze', 'Richiami, rinnovi, iscrizioni, pagamenti. Se si ripete ogni mese o ogni anno, la data si sposta da sola. Spunta «Fatto» e sparisce.'),
          ('Visite', 'Data, ora, per chi e dove; lo stato (programmata, completata, annullata); la data entro cui disdire, che puoi correggere se la tua struttura dice diverso; il ticket. Poi le domande da fare.'),
          ('Documenti', 'La cartellina: dove sta ogni documento, su carta e online, e quando scade. Due mesi prima compare tra gli impegni.'),
          ('Settimana, Contatti, Prime volte', 'La settimana fissa di tutti, i numeri utili da stampare, i ricordi scritti il giorno stesso.')]
pages.append(page('/gestionale/', 'Il gestionale di famiglia', 'Un file gratuito per organizzare documenti, scadenze, visite, la settimana e i ricordi della famiglia.', f'''
<section class="gs-hero wrap">
<div class="gs-txt"><span class="eyebrow">Risorsa gratuita</span><h1>Il gestionale di famiglia</h1>
<p class="lead">Apri il file e vedi subito cosa c'è da fare, entro quando e per chi. Visite, scadenze e documenti in un posto solo: si scrivono una volta e il resto si aggiorna da solo.</p>
<div class="row"><a class="btn" href="{GEST}" download data-umami-event="gestionale-excel">{ic('download','ic-s')} Scarica il file Excel</a>{sheets_btn}</div>
<p class="small">Dal telefono conviene Fogli Google: tocca «Apri in Fogli Google», poi «Crea una copia», e il file è tuo, nel tuo Drive. Nessun dato che inserisci arriva a noi.</p></div>
{devices()}
</section>
<section class="wrap gs-pts rv">{''.join(f'<div class="gp"><span class="vic">{ic("check")}</span><span>{p}</span></div>' for p in GEST_PUNTI)}</section>
<section class="wrap-t gs-body">
<figure class="vid rv"><video controls playsinline muted preload="metadata" poster="~/video/gestionale-tutorial.jpg" width="1080" height="1920" data-umami-event="gestionale-video"><source src="~/video/gestionale-tutorial.mp4" type="video/mp4"></video>
<figcaption><b>Come si usa, in un minuto.</b> Famiglia, visite, scadenze che si ripetono, la pagina «Inizia da qui» e la copia per il telefono. Il video è senza audio.</figcaption></figure>
<h2>Cosa c'è dentro</h2>
<ol class="steps">{''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in SCHEDE)}</ol>
<figure class="shot rv"><img src="~/assets/gestionale/visite.webp" alt="La scheda Visite: data, ora, per chi, medico o struttura, stato, data entro cui disdire e ticket" loading="lazy"><figcaption>La scheda Visite, con le righe di esempio che trovi nel file.</figcaption></figure>
<section class="box box-salvia"><h2>Come si usa</h2><ul class="plain"><li>Comincia dalla scheda Famiglia: scrivi i nomi di casa.</li><li>Le celle da compilare hanno il testo blu; quelle nere si calcolano da sole. Le righe di esempio vanno cancellate.</li><li>Sul computer aprilo con Excel; sul telefono usa la copia in Fogli Google.</li><li>Il file non manda notifiche: ti mostra cosa arriva ogni volta che lo apri.</li><li>Non è un archivio medico: scrivi solo quello che serve. Il file resta dove lo salvi tu, e nessun dato arriva a Serena.</li></ul></section>
<p class="small">Informazioni organizzative generali. Per vaccini, terapie e documenti sanitari il riferimento resta il pediatra, il medico o la ASL.</p>
{share('/gestionale/', 'Il gestionale di famiglia')}
</section>'''))

# ---------- risorse gratuite ----------
ck_rows = ''.join(f'''<li><a href="~/guide/{g['slug']}/"><b>{e(g['titolo'])}</b><span>{len(g['checklist'])} voci · {e(ARGN[g['arg']][1])}</span></a><a class="dl" href="~/guide/{g['slug']}/checklist.xlsx" download data-umami-event="checklist-excel" data-umami-event-guida="{g['slug']}" aria-label="Scarica la checklist in Excel">{ic('download')}</a></li>''' for g in GUIDE if g.get('checklist'))
STAMPABILI = [('settimana-sul-frigo', 'La settimana di tutti', 'Un foglio da attaccare al frigo: chi va dove, visite, chi accompagna'),
              ('domande-per-il-pediatra', 'Prima della visita dal pediatra', 'Cosa hai notato, le domande in ordine, cosa ha detto il medico'),
              ('lista-delle-medicine', 'La lista delle medicine, scritta insieme', 'Per chi segue un genitore o un nonno: da compilare a quattro mani')]
st_rows = ''.join(f'''<li><a href="~/scarica/{f}.pdf" download data-umami-event="stampabile" data-umami-event-file="{f}"><b>{e(t)}</b><span>PDF A4 · {e(d)}</span></a><a class="dl" href="~/scarica/{f}.pdf" download data-umami-event="stampabile" data-umami-event-file="{f}" aria-label="Scarica {e(t)} in PDF">{ic('download')}</a></li>''' for f, t, d in STAMPABILI)
pages.append(page('/risorse/', 'Risorse gratuite', 'Strumenti gratuiti per la famiglia: il gestionale di famiglia, fogli da stampare e le checklist delle guide.', f'''
<section class="ph-hd wrap"><div class="ph-txt"><h1>Risorse gratuite</h1><p class="lead">Strumenti da scaricare e usare subito. Gratuiti, senza registrazione: i tuoi dati restano sul tuo telefono o computer.</p></div></section>
<section class="wrap"><div class="gband rv">{devices('sm')}<div class="gb-txt"><span class="eyebrow">Il più usato</span><h2>Il gestionale di famiglia</h2><p>Uno strumento semplice per organizzare documenti, scadenze, visite e la settimana di tutti.</p><ul class="ticks">{''.join(f'<li>{ic("check","ic-s")}{p}</li>' for p in GEST_PUNTI[:3])}</ul><a class="btn" href="~/gestionale/">Scopri il gestionale {ic('arrow','ic-s')}</a></div></div></section>
<section class="wrap-t"><h2>Da stampare</h2><p class="lead-s">Fogli A4 in PDF, da stampare a casa e compilare a penna.</p><ul class="cklist">{st_rows}</ul></section>
<section class="wrap-t"><h2>Le checklist delle guide</h2><p class="lead-s">Ogni guida ha la sua lista: spuntala sul sito, salvala in Note o scaricala in Excel.</p><ul class="cklist">{ck_rows}</ul></section>'''))

# ---------- chi è serena ----------
CHI = {s[0]: s[1] for s in D['chi']['sezioni']}
QUOTE = 'Crediamo in una quotidianità più semplice, in famiglie più consapevoli, e in un po\' più di tempo per chi si prende cura degli altri.'
pages.append(page('/chi-e-serena/', 'Chi è Serena', D['chi']['sommario'], f'''
<section class="chi-hero wrap"><div class="ph-txt"><h1>Chi è Serena</h1><p class="lead">{e(D['chi']['sommario'])}</p></div>{foto('chi', '', 'chi-img', tone='sabbia', eager=True)}</section>
<section class="wrap-t prose">
<blockquote class="quote rv"><p>{QUOTE}</p></blockquote>
<h2>Perché nasce</h2><p>Chi si prende cura di una famiglia tiene a mente tutto: la visita da prenotare, il documento che scade, la domanda da fare al pediatra, la routine della sera. Serena nasce per alleggerire questo carico: informazioni affidabili, guide pratiche e strumenti utili, in parole semplici.</p>
<h2>Cosa facciamo</h2>{''.join(f'<p>{e(p)}</p>' for p in CHI['Cosa facciamo'])}
</section>
<section class="wrap rv"><h2 class="c">I nostri valori</h2>{valori('v-grid')}</section>
<section class="wrap-t prose">
<h2>Cosa non siamo</h2>{''.join(f'<p>{e(p)}</p>' for p in CHI['Cosa non siamo'])}
<h2>Trasparenza e indipendenza</h2><p>Serena è ideata e curata da una persona, con supporto AI per testi, immagini e verifica delle fonti: ogni pagina è letta e approvata prima di uscire. Non ci sono sponsor né pubblicità dietro ai consigli, e il sito non usa cookie. <a href="~/metodo/">Come lavoriamo, passo per passo</a>.</p>
<div class="row"><a class="btn" href="~/guide/">Leggi le guide</a><a class="btn btn-line" href="~/risorse/">Risorse gratuite</a></div>
{IGCARD}
</section>'''))

# ---------- il nostro metodo ----------
latest = sorted(D['post'], key=lambda x: x['data'], reverse=True)[:3]
pages.append(page('/metodo/', 'Il nostro metodo', 'Come nascono e si controllano i contenuti di Serena: fonti, intelligenza artificiale, revisione umana.', f'''
<section class="ph-hd wrap"><div class="ph-txt"><h1>Il nostro metodo</h1><p class="lead">Come nasce un contenuto di Serena, da dove vengono i dati e chi decide cosa pubblicare.</p></div></section>
<section class="wrap-t prose">
<ol class="steps big">
<li><b>Si parte da una domanda vera</b><span>Le cose che le famiglie si chiedono davvero: dove trovo un referto, cosa succede se salto una visita, quante ore deve dormire un bambino.</span></li>
<li><b>Si cercano le fonti</b><span>{e(CHI['Come lavoriamo'][1])}</span></li>
<li><b>Si scrive con il supporto AI</b><span>{e(CHI['Come lavoriamo'][0])}</span></li>
<li><b>Anche le immagini</b><span>Le fotografie del sito sono generate con strumenti AI e scelte da una persona: non ritraggono luoghi, oggetti o persone reali.</span></li>
<li><b>Si corregge quando serve</b><span>{e(CHI['Come lavoriamo'][2])}</span></li>
</ol>
<section class="box box-salvia"><h2>Il pediatra resta il riferimento</h2><p>Riportiamo cosa dicono linee guida e istituzioni, in parole semplici. Non diamo diagnosi né indicazioni sul singolo bambino: per quello c'è chi lo conosce.</p></section>
<h2>Le fonti dei post</h2><p>Ogni dato citato su Instagram ha la sua pagina con la fonte da aprire. Le più recenti:</p>
<ul class="postl">{''.join(f'<li><a href="~/fonti/{p["slug"]}/"><span class="date">{data_it(p["data"])}</span><b>{e(p["titolo"])}</b></a></li>' for p in latest)}</ul>
<a class="more" href="~/fonti/">Tutte le fonti {ic('arrow','ic-s')}</a>
</section>'''))

# ---------- privacy ----------
pages.append(page('/privacy/', 'Privacy', 'Come serenainmente.it tratta i dati: niente cookie, niente profilazione, statistiche anonime.', f'''
<section class="ph-hd wrap"><div class="ph-txt"><h1>Privacy</h1><p class="lead">In breve: niente cookie, niente profilazione, nessun dato personale raccolto.</p></div></section>
<section class="wrap-t prose">{''.join(f'<p>{e(p)}</p>' for p in CHI['Privacy'])}
<h2>Contatti</h2><p>Per qualsiasi domanda: <a href="mailto:{MAIL}">{MAIL}</a>, oppure un messaggio privato su Instagram a <a href="{IG}" rel="noopener">@serenainmente</a>.</p>
<p class="small">Ultimo aggiornamento: {data_it(datetime.date.today().isoformat())}.</p></section>'''))

# ---------- note legali ----------
pages.append(page('/note-legali/', 'Note legali', 'Chi cura serenainmente.it, come si possono usare i contenuti, informazioni sanitarie, link esterni e immagini.', f'''
<section class="ph-hd wrap"><div class="ph-txt"><h1>Note legali</h1><p class="lead">Le regole del sito, in parole semplici.</p></div></section>
<section class="wrap-t prose">
<h2>Chi cura il sito</h2><p>serenainmente.it e il profilo Instagram <a href="{IG}" rel="noopener">@serenainmente</a> sono un progetto editoriale indipendente, ideato e curato da una persona, con supporto AI per testi, immagini e verifica delle fonti. Non ci sono sponsor né pubblicità. Per qualsiasi comunicazione: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<h2>Uso dei contenuti</h2><p>Testi, grafiche, guide, checklist, fogli da stampare e il gestionale di famiglia sono di serenainmente.it. Puoi usarli gratuitamente per te e la tua famiglia, stamparli e condividerli con il link alla pagina originale. Non è consentito ripubblicarli, modificarli per distribuirli o usarli per scopi commerciali senza un consenso scritto: se ti servono per una scuola, un consultorio o un'associazione, scrivici e ne parliamo volentieri.</p>
<h2>Informazioni sanitarie</h2><p>I contenuti sono informazioni generali tratte da fonti indicate pagina per pagina. Non sono diagnosi né indicazioni per una persona specifica e non sostituiscono il parere del pediatra, del medico o di altri professionisti. In caso di urgenza chiama il 112.</p>
<h2>Link e fonti esterne</h2><p>Le fonti citate rimandano a siti di enti e istituzioni che non gestiamo. Controlliamo i collegamenti alla data indicata in ogni pagina, ma i loro contenuti possono cambiare: in quel caso aggiorniamo la pagina appena ce ne accorgiamo.</p>
<h2>Immagini</h2><p>Le fotografie del sito e le grafiche sono generate o composte con strumenti digitali e AI e scelte da una persona: non ritraggono persone, luoghi o oggetti reali.</p>
<h2>Marchi di terzi</h2><p>Microsoft Excel, Fogli Google, Numbers, Instagram e WhatsApp sono marchi dei rispettivi titolari: li citiamo solo per spiegare come usare gli strumenti.</p>
<h2>Errori e segnalazioni</h2><p>Se trovi un errore, un dato superato o un link che non funziona, scrivici: correggiamo e indichiamo la data dell'aggiornamento. Come trattiamo i dati è spiegato nella pagina <a href="~/privacy/">Privacy</a>.</p>
<p class="small">Ultimo aggiornamento: {data_it(datetime.date.today().isoformat())}.</p></section>'''))

# ---------- fonti ----------
post_cards = []
for p in sorted(D['post'], key=lambda x: x['data'], reverse=True):
    claims = ''.join(f'<li>{e(c)}</li>' for c in p['affermazioni'])
    fonti = ''.join(src_block(fid) for fid in p['fonti'])
    guida = next((g for g in D['guide'] if g['slug'] == p.get('guida')), None)
    gl = f'<a class="btn" href="~/guide/{guida["slug"]}/">Leggi la guida</a>' if guida else ''
    pages.append(page(f"/fonti/{p['slug']}/", f"Fonti: {p['titolo']}", f"Le fonti del post «{p['titolo']}» di @serenainmente.", f'''
<section class="wrap-t prose fpage"><nav class="crumbs"><a href="~/fonti/">Le fonti</a></nav><span class="eyebrow">Fonti del post · {data_it(p['data'])}</span><h1>{e(p['titolo'])}</h1>
<h2>Cosa dice il post</h2><ul class="plain">{claims}</ul>
<h2>Fonti</h2><ul class="sources">{fonti}</ul>
<p class="small">Collegamenti controllati il {data_it(p['controllo'])}. Informazioni generali, non sostituiscono il parere del pediatra o del medico.</p>
<div class="row">{gl}<a class="btn btn-line" href="{IG}" rel="noopener" data-umami-event="instagram">Vai al profilo Instagram</a></div></section>'''))
    post_cards.append(f'<li><a href="~/fonti/{p["slug"]}/"><span class="date">{data_it(p["data"])}</span><b>{e(p["titolo"])}</b><span class="small">{len(p["fonti"])} {"fonte" if len(p["fonti"]) == 1 else "fonti"}</span></a></li>')
pages.append(page('/fonti/', 'Le fonti di Serena', 'Le fonti dei dati citati nei post di @serenainmente, con i link alle pagine originali.', f'''
<section class="ph-hd wrap"><div class="ph-txt"><h1>Le fonti</h1><p class="lead">Ogni dato citato nei post viene da qui. Apri un post per vedere cosa afferma e da quale fonte viene.</p></div></section>
<section class="wrap-t"><ul class="postl">{''.join(post_cards)}</ul></section>'''))

# ---------- home ----------
MAXROT = 5  # quante domande vede chi visita la home (scelte a caso ogni volta)
DOMANDE = [(g['domanda'], f"/guide/{g['slug']}/") for g in GUIDE if g.get('domanda')] + [('Come organizzare la settimana', '/gestionale/')]
ROT = (f'<p class="rot" data-rot data-max="{MAXROT}"><span class="sr">Per esempio: </span>'
       + ''.join(f'<a href="~{h}"{"" if i == 0 else " hidden"}>{e(t)} {ic("arrow","ic-s")}</a>' for i, (t, h) in enumerate(DOMANDE))
       + '</p>')
ROT = (f'<div class="rotw">{ROT}<button class="rot-all" type="button" aria-expanded="false" aria-controls="tutte-domande" hidden>Vedi tutte</button></div>'
       f'<ul class="asks" id="tutte-domande" hidden>' + ''.join(f'<li><a href="~{h}">{e(t)}</a></li>' for t, h in DOMANDE) + '</ul>')
tiles = ''.join(f'<a class="tile {a[4]}" href="~/guide/#{a[0]}"><span class="tic">{ic(a[3])}</span><b>{e(a[1])}</b><small>{e(a[2])}</small><span class="cnt">{argc[a[0]]} {"guida" if argc[a[0]] == 1 else "guide"}</span></a>' for a in ARG if argc[a[0]])
pages.append(page('/', 'Serena', 'Parole e idee per chi si prende cura della famiglia: guide pratiche, dati con le loro fonti, strumenti gratuiti.', f'''
<section class="hero wrap">
<div class="hero-txt"><h1>Hai già abbastanza da tenere a mente.</h1>
{ROT}
<p class="lead">Guide chiare e strumenti gratuiti per chi si prende cura della famiglia.</p>
<div class="row"><a class="btn" href="~/guide/">Scopri le guide</a><a class="btn btn-line" href="{IG}" rel="noopener" data-umami-event="instagram">Seguici su Instagram</a></div></div>
{foto('hero', '', 'hero-img', tone='rosa', eager=True)}
</section>
<section class="wrap">{valori('v-band')}</section>
<section class="wrap rv"><div class="sec-hd"><h2>Ultimi approfondimenti</h2><a class="more" href="~/guide/">Vedi tutti {ic('arrow','ic-s')}</a></div>
<div class="grid3 carousel">{''.join(card(g) for g in GUIDE[:3])}</div></section>
<section class="wrap rv"><div class="sec-hd"><h2>Esplora per argomento</h2></div><div class="tiles">{tiles}</div></section>
<section class="wrap rv"><div class="gband">{devices('sm')}<div class="gb-txt"><span class="eyebrow">Risorsa gratuita</span><h2>Il gestionale di famiglia</h2><p>Uno strumento semplice per organizzare documenti, scadenze, visite e la settimana di tutti.</p><ul class="ticks">{''.join(f'<li>{ic("check","ic-s")}{p}</li>' for p in GEST_PUNTI[:3])}</ul><a class="btn" href="~/gestionale/">Scopri il gestionale {ic('arrow','ic-s')}</a></div></div></section>
<section class="wrap rv"><div class="chi-band">{foto('chi', '', 'cb-img', tone='sabbia')}<div class="cb-txt"><h2>Chi è Serena</h2><p>{e(D['chi']['sommario'])} Ogni dato ha la sua fonte, ogni pagina è letta da una persona.</p><a class="btn btn-line" href="~/chi-e-serena/">Scopri di più su Serena {ic('arrow','ic-s')}</a></div><blockquote class="quote"><p>{QUOTE}</p></blockquote></div></section>
<section class="wrap rv ig-sec"><div><h2>Ogni giorno, una cosa utile</h2><p>Su Instagram, ogni mattina alle 10: una cosa pratica da fare in dieci minuti, un dato che toglie un'ansia, una frase in cui ritrovarsi.</p></div>{IGCARD}</section>
''', cls='p-home'))

# ---------- sitemap, robots, file ----------
if not PREVIEW:
    today = datetime.date.today().isoformat()
    sm = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>' for p in pages)
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
else:
    for d in ['assets/fonts', 'assets/brand', 'assets/gestionale', 'assets/foto', 'scarica']:
        s = os.path.join(ROOT, d)
        if os.path.isdir(s): shutil.copytree(s, os.path.join(OUT, d), dirs_exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'assets', 'stile2.css'), os.path.join(OUT, 'assets', 'stile2.css'))
    for g in D['guide']:
        s = os.path.join(ROOT, 'guide', g['slug'], 'checklist.xlsx')
        if os.path.exists(s): shutil.copy(s, os.path.join(OUT, 'guide', g['slug'], 'checklist.xlsx'))
print('\n'.join(pages))
