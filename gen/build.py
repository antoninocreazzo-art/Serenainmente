#!/usr/bin/env python3
"""Genera il sito statico di serenainmente.it a partire da gen/dati.json.
Uso: python3 gen/build.py  (dalla cartella del sito)"""
import json, os, html, datetime

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

# ---------- guide ----------
guide_cards = []
for g in D['guide']:
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
{f'<section class="note stack"><h2>Checklist</h2><ul class="check">{check}</ul></section>' if check else ''}
{f'<section class="stack"><h2>Fonti</h2><ul class="sources">{fonti}</ul></section>' if fonti else ''}
<p class="small">{e(g['avvertenza'])}</p>
</article>'''
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": g['titolo'], "description": g['sommario'],
          "datePublished": g['data'], "dateModified": g['data'], "inLanguage": "it",
          "author": {"@type": "Organization", "name": "Serena"}, "publisher": {"@type": "Organization", "name": "Serena"}}
    pages.append(page(f"/guide/{g['slug']}/", g['titolo'], g['sommario'], body, ld))
    guide_cards.append(f'<a class="card link" href="/guide/{g["slug"]}/"><span class="eyebrow">{e(g["categoria"])} · {e(g["tempo"])}</span><b>{e(g["titolo"])}</b><span>{e(g["sommario"])}</span></a>')

pages.append(page('/guide/', 'Guide pratiche', 'Piccoli metodi per giornate più leggere, con le fonti quando servono.',
    f'''<section class="stack"><h1>Guide pratiche</h1><p class="lead">Piccoli metodi per giornate più leggere. Si fanno con quello che hai già in casa: una cartellina, un foglio, il telefono.</p></section>
<div class="cards">{''.join(guide_cards)}</div>'''))

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
    f'''<article class="stack article"><h1>Chi è Serena</h1><p class="lead">{e(c['sommario'])}</p>
{''.join(f'<section class="stack"><h2>{e(s[0])}</h2>' + ''.join(f'<p>{e(x)}</p>' for x in s[1]) + '</section>' for s in c['sezioni'])}
</article>'''))

# ---------- home ----------
latest = sorted(D['post'], key=lambda x: x['data'], reverse=True)[:3]
home_posts = ''.join(f'<li class="post"><span class="date">{data_it(p["data"])}</span><h2><a href="/fonti/{p["slug"]}/">{e(p["titolo"])}</a></h2></li>' for p in latest)
pages.append(page('/', 'Serena', 'Parole e idee per chi si prende cura della famiglia: guide pratiche, dati con le loro fonti, frasi in cui ritrovarsi.',
    f'''<section class="stack hero"><h1>Parole e idee per chi si prende cura della famiglia.</h1>{FILO}
<p class="lead">Una cosa pratica da fare in dieci minuti, un dato che toglie un'ansia, una frase in cui ritrovarsi.</p>
<div class="row"><a class="btn" href="https://www.instagram.com/serenainmente/">Seguici su Instagram</a><a class="btn sec" href="/guide/">Leggi le guide</a></div></section>
<section class="stack"><h2>Guide che restano</h2><div class="cards">{''.join(guide_cards)}</div></section>
<section class="stack"><h2>Dai nostri post</h2><p>Le fonti dei dati citati su Instagram, post per post.</p><ol class="posts">{home_posts}</ol><a href="/fonti/">Tutte le fonti →</a></section>
<section class="note stack"><h2>Chi è Serena</h2><p>{e(c['sommario'])}</p><a href="/chi-e-serena/">Come lavoriamo →</a></section>'''))

# ---------- sitemap, robots ----------
today = datetime.date.today().isoformat()
sm = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>' for p in pages)
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
print('\n'.join(pages))
