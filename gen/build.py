#!/usr/bin/env python3
"""Genera il sito statico di serenainmente.it a partire da gen/dati.json.
Uso: python3 gen/build.py  (dalla cartella del sito)"""
import json, os, html, datetime
from openpyxl import Workbook  # pip install openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, 'gen', 'dati.json'), encoding='utf-8'))
SITE = 'https://serenainmente.it'
e = html.escape

MARK = '<svg viewBox="0 0 1080 1080" aria-hidden="true"><path d="M 660 395 C 620 320 440 315 440 425 C 440 530 650 520 650 645 C 650 770 455 780 410 690" fill="none" stroke="#FBF6F4" stroke-width="90" stroke-linecap="round"/></svg>'
FILO = '<svg class="filo" viewBox="280 40 540 110" aria-hidden="true"><path d="M 300 128 C 380 128 400 62 470 62 C 540 62 552 138 620 138 C 690 138 700 84 760 84" fill="none" stroke="#97606F" stroke-width="7" stroke-linecap="round"/><circle cx="792" cy="84" r="9" fill="#C99AA6"/></svg>'
ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1080 1080'%3E%3Ccircle cx='540' cy='540' r='540' fill='%2397606F'/%3E%3Cpath d='M 660 395 C 620 320 440 315 440 425 C 440 530 650 520 650 645 C 650 770 455 780 410 690' fill='none' stroke='%23FBF6F4' stroke-width='90' stroke-linecap='round'/%3E%3C/svg%3E"
MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']

def data_it(s):
    d = datetime.date.fromisoformat(s)
    return f"{d.day} {MESI[d.month-1]} {d.year}"

def page(path, title, desc, body, ld=None):
    canon = SITE + path
    t = f"{title} · Serena" if title != 'Serena' else 'Serena · Parole e idee per chi si prende cura della famiglia'
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''
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
<meta property="og:type" content="website">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="it_IT">
<link rel="icon" href="{ICON}">
<link rel="stylesheet" href="/assets/stile.css">
{ldj}
</head>
<body>
<div class="wrap">
<header class="top">
<a class="brand" href="/"><span class="mark">{MARK}</span>serenainmente</a>
<nav class="nav" aria-label="Menu"><a href="/guide/">Guide</a><a href="/fonti/">Le fonti</a><a href="/chi-e-serena/">Chi è Serena</a></nav>
</header>
<main class="stack" style="gap:36px">
{body}
</main>
<footer>
<p>I testi di Serena nascono con l'aiuto dell'intelligenza artificiale e sono scelti da una persona. <a href="/chi-e-serena/">Come lavoriamo</a></p>
<p>Informazioni generali, non sostituiscono il parere del pediatra o del medico.</p>
<p>Questo sito non usa cookie e non raccoglie dati personali. © {datetime.date.today().year} serenainmente.it</p>
</footer>
</div>
</body>
</html>
'''
    full = os.path.join(ROOT, path.strip('/'), 'index.html') if path != '/' else os.path.join(ROOT, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(out)
    return path

FONTI = {f['id']: f for f in D['fonti']}

def share(path, title):
    url = SITE + path
    wa = 'https://wa.me/?text=' + html.escape(__import__('urllib.parse').parse.quote(f"{title} {url}"))
    return f'''<div class="share"><span class="small">Ti è utile? Mandala a chi ne ha bisogno.</span>
<div class="row"><a class="btn sec" href="{wa}" rel="noopener">Manda su WhatsApp</a><button class="btn sec" type="button" onclick="navigator.clipboard&&navigator.clipboard.writeText('{url}').then(()=>{{this.textContent='Link copiato'}})">Copia il link</button></div></div>'''

TRUST = '''<ul class="trust" aria-label="Come lavoriamo">
<li><b>Fonti aperte</b><span>Ogni dato ha una fonte che puoi aprire</span></li>
<li><b>Nessuna pubblicità</b><span>Niente sponsor, niente cookie</span></li>
<li><b>Scelto da una persona</b><span>I testi nascono con l'IA, ogni pagina è letta e approvata</span></li>
<li><b>Il pediatra resta il riferimento</b><span>Informazioni generali, mai consigli sul singolo bambino</span></li>
</ul>'''


def src_block(fid):
    f = FONTI[fid]
    dom = f['url'].split('/')[2].replace('www.', '')
    return f'''<li class="src">
<span class="org">{e(f['ente'])}, {e(str(f['anno']))}</span>
<span class="ttl">{e(f['titolo'])}</span>
<span class="type">{e(f['tipo'])}</span>
<a href="{e(f['url'])}" rel="noopener">Apri la fonte su {e(dom)}</a>
</li>'''

pages = []

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

# ---------- guide ----------
guide_cards = []
for gi, g in enumerate(D['guide']):
    ng = D['guide'][(gi+1) % len(D['guide'])]
    nxt = f'<a class="card link next" href="/guide/{ng["slug"]}/"><span class="eyebrow">Prossima guida · {e(ng["tempo"])}</span><b>{e(ng["titolo"])}</b></a>' if len(D['guide'])>1 else ''
    if g.get('checklist'): checklist_xlsx(g)
    steps = ''.join(f'<li><b>{e(s[0])}</b><span>{e(s[1])}</span></li>' for s in g['passi'])
    errori = ''.join(f'<li>{e(x)}</li>' for x in g.get('errori', []))
    check = ''.join(f'<li><span class="box" aria-hidden="true"></span>{e(x)}</li>' for x in g.get('checklist', []))
    fonti = ''.join(src_block(fid) for fid in g.get('fonti', []))
    body = f'''<article class="stack article">
<p class="eyebrow">Guida pratica · {e(g['categoria'])}</p>
<h1>{e(g['titolo'])}</h1>
<p class="lead">{e(g['sommario'])}</p>
<dl class="facts"><div><dt>Tempo</dt><dd>{e(g['tempo'])}</dd></div><div><dt>Serve</dt><dd>{e(g['serve'])}</dd></div><div><dt>Aggiornata</dt><dd>{data_it(g['data'])}</dd></div></dl>
<section class="stack"><h2>Perché aiuta</h2>{''.join(f'<p>{e(p)}</p>' for p in g['perche'])}</section>
<section class="stack"><h2>Come si fa</h2><ol class="steps">{steps}</ol></section>
{f'<section class="stack"><h2>Errori comuni</h2><ul class="plain">{errori}</ul></section>' if errori else ''}
{f'<section class="note stack"><h2>Checklist</h2><ul class="check">{check}</ul><div class="row noprint"><a class="btn sec" href="/guide/{g["slug"]}/checklist.xlsx" download>Scarica in Excel</a><button class="btn sec" type="button" onclick="window.print()">Stampa</button></div></section>' if check else ''}
{f'<section class="stack"><h2>Fonti</h2><ul class="sources">{fonti}</ul></section>' if fonti else ''}
<p class="small">{e(g['avvertenza'])}</p>
{share(f"/guide/{g['slug']}/", g['titolo'])}
{nxt}
</article>'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": g['titolo'], "description": g['sommario'],
          "datePublished": g['data'], "dateModified": g['data'], "inLanguage": "it",
          "author": {"@type": "Organization", "name": "Serena"}, "publisher": {"@type": "Organization", "name": "Serena"}}
    pages.append(page(f"/guide/{g['slug']}/", g['titolo'], g['sommario'], body, ld))
    guide_cards.append(f'<a class="card link" href="/guide/{g["slug"]}/"><span class="eyebrow">{e(g["categoria"])} · {e(g["tempo"])}</span><b>{e(g["titolo"])}</b><span>{e(g["sommario"])}</span></a>')

cats = []
for g in D['guide']:
    if g['categoria'] not in cats: cats.append(g['categoria'])
guide_groups = ''.join(f'<section class="stack" id="{e(c.lower().replace(" ","-"))}"><h2>{e(c)}</h2><div class="cards">{"".join(gc for gc, g in zip(guide_cards, D["guide"]) if g["categoria"]==c)}</div></section>' for c in cats)
pages.append(page('/guide/', 'Guide pratiche', 'Piccoli metodi per giornate più leggere, con le fonti quando servono.',
    f'''<section class="stack"><h1>Guide pratiche</h1><p class="lead">Piccoli metodi per giornate più leggere. Si fanno con quello che hai già in casa: una cartellina, un foglio, il telefono.</p></section>
{guide_groups}'''))

# ---------- fonti per post ----------
post_cards = []
for p in sorted(D['post'], key=lambda x: x['data'], reverse=True):
    claims = ''.join(f'<li>{e(c)}</li>' for c in p['affermazioni'])
    fonti = ''.join(src_block(fid) for fid in p['fonti'])
    guida = next((g for g in D['guide'] if g['slug'] == p.get('guida')), None)
    gl = f'<a class="btn sec" href="/guide/{guida["slug"]}/">Leggi la guida: {e(guida["titolo"])}</a>' if guida else ''
    body = f'''<article class="stack article">
<p class="eyebrow">Fonti del post · {data_it(p['data'])}</p>
<h1>{e(p['titolo'])}</h1>
<section class="stack"><h2>Cosa dice il post</h2><ul class="plain">{claims}</ul></section>
<section class="stack"><h2>Fonti</h2><ul class="sources">{fonti}</ul></section>
<p class="small">Collegamenti controllati il {data_it(p['controllo'])}. Informazioni generali, non sostituiscono il parere del pediatra o del medico.</p>
<div class="row">{gl}<a class="btn sec" href="https://www.instagram.com/serenainmente/">Vai al profilo Instagram</a></div>
</article>'''
    pages.append(page(f"/fonti/{p['slug']}/", f"Fonti: {p['titolo']}", f"Le fonti del post «{p['titolo']}» di @serenainmente.", body))
    post_cards.append(f'<li class="post"><span class="date">{data_it(p["data"])}</span><h2><a href="/fonti/{p["slug"]}/">{e(p["titolo"])}</a></h2><span class="small">{len(p["fonti"])} {"fonte" if len(p["fonti"])==1 else "fonti"}</span></li>')

pages.append(page('/fonti/', 'Le fonti di Serena', 'Le fonti dei dati citati nei post di @serenainmente, con i link alle pagine originali.',
    f'''<section class="stack"><h1>Le fonti di Serena</h1><p class="lead">Ogni dato citato nei post viene da qui. Apri un post per vedere cosa afferma e da quale fonte viene. I più recenti sono in alto.</p></section>
<ol class="posts">{''.join(post_cards)}</ol>'''))

# ---------- chi è serena ----------
c = D['chi']
pages.append(page('/chi-e-serena/', 'Chi è Serena', c['sommario'],
    f'''<article class="stack article"><h1>Chi è Serena</h1><p class="lead">{e(c['sommario'])}</p>{TRUST}
{''.join(f'<section class="stack"><h2>{e(s[0])}</h2>' + ''.join(f'<p>{e(x)}</p>' for x in s[1]) + '</section>' for s in c['sezioni'])}
</article>'''))

# ---------- home ----------
latest = sorted(D['post'], key=lambda x: x['data'], reverse=True)[:3]
home_posts = ''.join(f'<li class="post"><span class="date">{data_it(p["data"])}</span><h2><a href="/fonti/{p["slug"]}/">{e(p["titolo"])}</a></h2></li>' for p in latest)
pages.append(page('/', 'Serena', 'Parole e idee per chi si prende cura della famiglia: guide pratiche, dati con le loro fonti, frasi in cui ritrovarsi.',
    f'''<section class="stack hero"><h1>Parole e idee per chi si prende cura della famiglia.</h1>{FILO}
<p class="lead">Una cosa pratica da fare in dieci minuti, un dato che toglie un'ansia, una frase in cui ritrovarsi.</p>
<div class="row"><a class="btn" href="https://www.instagram.com/serenainmente/">Seguici su Instagram</a><a class="btn sec" href="/guide/">Leggi le guide</a></div></section>
<section class="stack"><h2>Inizia da qui</h2><p>Scegli il momento che stai vivendo.</p><div class="moments">{''.join(f'<a class="moment" href="/guide/{m["guida"]}/"><b>{e(m["quando"])}</b><span>{e(m["cosa"])}</span></a>' for m in D.get('momenti', []))}</div></section>
{TRUST}
<section class="stack"><h2>Guide che restano</h2><div class="cards">{''.join(guide_cards)}</div><a href="/guide/">Tutte le guide →</a></section>
<section class="stack"><h2>Dai nostri post</h2><p>Le fonti dei dati citati su Instagram, post per post.</p><ol class="posts">{home_posts}</ol><a href="/fonti/">Tutte le fonti →</a></section>
<section class="note stack"><h2>Chi è Serena</h2><p>{e(c['sommario'])}</p><a href="/chi-e-serena/">Come lavoriamo →</a></section>
<section class="stack"><h2>Ogni giorno, una cosa utile</h2><p>Su Instagram pubblichiamo ogni mattina alle 10: un metodo pratico, un dato con la sua fonte, una frase da mandare a chi ne ha bisogno.</p><a class="btn" href="https://www.instagram.com/serenainmente/">Seguici su Instagram</a></section>'''))

# ---------- sitemap, robots ----------
today = datetime.date.today().isoformat()
sm = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>' for p in pages)
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
print('\n'.join(pages))
