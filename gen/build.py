#!/usr/bin/env python3
"""Genera il sito serenainmente.it da gen/dati.json — direzione «Luce» (2035).
Il gestionale NON si rigenera qui: python3 gen/gestionale.py e poi ricalcolo con LibreOffice.
Le miniature (assets/mini, assets/ig) si creano con python3 gen/miniature.py quando arriva una foto nuova.
Uso:
  ANTEPRIMA:  OUT=/percorso/anteprima LINKS=rel python3 gen/build.py
  SITO:       python3 gen/build.py            (scrive nella cartella del sito)
Stile: assets/stile3.css · Script: assets/sito.js · Indice della ricerca: assets/cerca-dati.js (generato qui)."""
import json, os, re, html, datetime, shutil, urllib.parse, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get('OUT', ROOT)
REL = os.environ.get('LINKS') == 'rel'
PREVIEW = OUT != ROOT
D = json.load(open(os.path.join(ROOT, 'gen', 'dati.json'), encoding='utf-8'))
SITE = 'https://serenainmente.it'
IG = 'https://www.instagram.com/serenainmente/'
MAIL = 'privacy@serenainmente.it'   # unico indirizzo di contatto (deciso dal presidente il 12/11/2026)
e = html.escape
MESI = ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre']
def data_it(s):
    d = datetime.date.fromisoformat(s); return f"{d.day}{'°' if d.day == 1 else ''} {MESI[d.month-1]} {d.year}"
def esiste(*p): return os.path.exists(os.path.join(ROOT, *p))
def ver(*p):
    """?v=… dall'impronta del file: cambia solo se cambia il contenuto (così la ricostruzione del mattino non tocca tutte le pagine)"""
    return hashlib.md5(open(os.path.join(ROOT, *p), 'rb').read()).hexdigest()[:8]
INDICE_V = '@@INDICE@@'  # si riempie in fondo con l'impronta dell'indice
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)

# ---------- argomenti ----------
ARG = [
    ('salute', 'Salute e visite', 'Pediatra, specialisti, ricette e prenotazioni', 'steth'),
    ('documenti', 'Documenti', 'Fascicolo sanitario, scelte, cambi e moduli', 'folder'),
    ('organizzazione', 'Organizzarsi', 'Cartellina, scadenze e settimana di famiglia', 'calendar'),
    ('crescita', 'Bambini e crescita', 'Sonno, routine e piccoli passi', 'sprout'),
]
ARGN = {a[0]: a for a in ARG}
GUIDA_ARG = {'indennita-di-accompagnamento': 'documenti', 'esenzione-ticket': 'documenti', 'risvegli-notturni': 'crescita', 'certificato-sport-bambini': 'salute', 'domande-per-il-pediatra': 'salute', 'visita-specialistica-come-funziona': 'salute',
             'spostare-disdire-pagare-visita': 'salute', 'documenti-sanitari-dove-trovarli': 'documenti',
             'pediatra-e-medico-di-base': 'documenti', 'cartellina-di-famiglia': 'organizzazione',
             'routine-della-nanna': 'crescita'}
# per chi è utile ogni pagina («Di chi ti prendi cura?» in home). Non è contenuto: è un'etichetta per ordinare.
TUTTE_ETA = ['0-1', '1-3', '3-6', '6-12', '13-18']
PER = {'routine-della-nanna': ('bambino', ['0-1', '1-3', '3-6']), 'risvegli-notturni': ('bambino', ['1-3']),
       'quanto-dorme-un-bambino': ('bambino', TUTTE_ETA), 'domande-per-il-pediatra': ('bambino', TUTTE_ETA),
       'iscrizioni-nido-e-scuola': ('bambino', ['0-1', '1-3', '3-6']), 'carta-identita-bambini': ('bambino', TUTTE_ETA),
       'certificato-vaccinale': ('bambino', ['0-1', '1-3', '3-6']), 'visita-specialistica-come-funziona': ('bambino', TUTTE_ETA),
       'certificato-sport-bambini': ('bambino', ['6-12', '13-18']), 'lista-medicine-genitore-anziano': ('anziano', []),
       'indennita-di-accompagnamento': ('anziano', []), 'esenzione-ticket': ('bambino anziano', ['0-1', '1-3', '3-6'])}
def per(slug): return PER.get(slug, ('bambino anziano', TUTTE_ETA))
# guide che danno numeri e regole (le altre dicono cosa fare): la ricerca mette prima il «cosa fare» quando chi scrive ha un problema
DATI = {'quanto-dorme-un-bambino'}
# quando una guida ha la precedenza sulle altre dello stesso argomento per un'età (es. sonno a 1-3 anni)
# parole in più per la ricerca (come le dice chi cerca), non compaiono nella pagina
CHIAVI = {
 'routine-della-nanna': 'non dorme non vuole dormire addormentare addormenta sera nanna sonno letto capricci',
 'indennita-di-accompagnamento': 'invalidità civile accompagnamento indennità inps assegno invalido non autosufficiente patronato verbale commissione 104 aiuto economico soldi',
 'esenzione-ticket': 'esenzione ticket esente non pagare reddito e01 e02 e03 e04 over 65 pensione minima disoccupato autocertificazione costo visite esami',
 'risvegli-notturni': 'si sveglia risvegli notturni notte piange non dorme sonno svegliarsi dormire 18 mesi due anni',
 'certificato-sport-bambini': 'sport certificato medico sportivo non agonistico palestra piscina calcio nuoto danza ginnastica attività fisica movimento elettrocardiogramma',
 'quanto-dorme-un-bambino': 'quante ore dorme poco troppo sonnellino pisolino sveglia notte neonato',
 'domande-per-il-pediatra': 'visita pediatra domande dottore bilancio di salute controllo domani appuntamento chiedo chiedere chiedergli',
 'visita-specialistica-come-funziona': 'specialista impegnativa ricetta cup prenotare lista d\'attesa',
 'spostare-disdire-pagare-visita': 'spostare disdire annullare rimandare cancellare visita cup ticket pagare',
 'documenti-sanitari-dove-trovarli': 'referto esami analisi fascicolo sanitario fse spid gruppo sanguigno',
 'pediatra-e-medico-di-base': 'cambiare scegliere pediatra medico di famiglia medico di base dottore trasferimento',
 'cartellina-di-famiglia': 'documenti tessera sanitaria libretto dove tenere ordine',
 'certificato-vaccinale': 'vaccino vaccini vaccinazioni libretto certificato scaricare fatti fatte obbligatori obbligatorie',
 'iscrizioni-nido-e-scuola': 'iscrivere iscrizione nido asilo materna scuola elementare primaria',
 'lista-medicine-genitore-anziano': 'medicine farmaci pastiglie pillole compresse terapia mamma papà nonna nonno anziano anziana badante',
 'carta-identita-bambini': 'carta d\'identità cie documento espatrio viaggio passaporto',
}
for g in D['guide']:
    g['arg'] = g.get('argomento') or GUIDA_ARG.get(g['slug'], 'organizzazione')
    testo = ' '.join([g['titolo'], g['sommario']] + g['perche'] + [a + ' ' + b for a, b in g['passi']] + g.get('errori', []) + g.get('checklist', []))
    g['min'] = max(2, round(len(testo.split()) / 200))
    g['fonti'] = list(dict.fromkeys(g.get('fonti', [])))  # una fonte si cita una volta sola
    g['agg'] = g.get('aggiornata', g['data'])
GUIDE = sorted(D['guide'], key=lambda g: g['data'], reverse=True)
GN = {g['slug']: g for g in GUIDE}
OGGI = datetime.date.today().isoformat()
# i post compaiono (fonti, home, sitemap) solo dal giorno in cui escono su Instagram
D['post'] = [x for x in D['post'] if x['data'] <= OGGI]
FRASI = sorted([f for f in D.get('frasi', []) if f['data'] <= OGGI], key=lambda f: f['data'], reverse=True)
FRASI_ON = len(FRASI) >= 5  # la pagina entra nei menu quando ha almeno 5 frasi
FRASI_LI = '<li><a href="~/frasi/">Le frasi da mandare</a></li>' if FRASI_ON else ''

# ---------- icone (linea, 24px) ----------
P = {
 'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
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
 'home': '<path d="M4 11.5 12 4l8 7.5"/><path d="M6 10v9.5h12V10"/>',
 'tools': '<rect x="3.5" y="3.5" width="7" height="7" rx="2"/><rect x="13.5" y="3.5" width="7" height="7" rx="2"/><rect x="3.5" y="13.5" width="7" height="7" rx="2"/><rect x="13.5" y="13.5" width="7" height="7" rx="2"/>',
 'sun': '<path d="M5 17h14M8 21h8"/><path d="M6 17a6 6 0 0 1 12 0"/><path d="M12 5v2M4.5 9.5 6 11M19.5 9.5 18 11"/>',
 'moon': '<path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z"/>',
 'bookmark': '<path d="M6 4h12v17l-6-4.5L6 21z"/>',
 'sound': '<path d="M4 10v4h3l5 4V6L7 10z"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/>',
 'zoom': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5M11 8v6M8 11h6"/>',
}
def ic(n, cls='ic'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[n]}</svg>'

def foto(key, alt, cls='', eager=False, sizes='(min-width:900px) 50vw, 100vw'):
    if not esiste('assets', 'foto', f'{key}.webp'): return ''
    return (f'<img class="ph {cls}" src="~/assets/foto/{key}-sm.webp" srcset="~/assets/foto/{key}-sm.webp 768w, ~/assets/foto/{key}.webp 1536w" '
            f'sizes="{sizes}" width="1536" height="1024" alt="{e(alt)}" {"" if eager else "loading=lazy"} decoding="async">')
def mini(nome):
    """miniatura quadrata da 160 px, se c'è"""
    return f'/assets/mini/{nome}.webp' if esiste('assets', 'mini', f'{nome}.webp') else None
def riga(href, titolo, sotto, img=None, icona='arrow', attr='', li=''):
    im = f'<img src="~{img}" alt="" width="64" height="64" loading="lazy" decoding="async">' if img else f'<span class="tic">{ic(icona)}</span>'
    return f'<li{li}><a class="rowl" href="{href}"{attr}>{im}<span class="t"><b>{e(titolo)}</b><small>{e(sotto)}</small></span></a></li>'
def riga_guida(g, li=''):
    return riga(f"~/guide/{g['slug']}/", g['titolo'], f"Guida · {g['min']} min · {ARGN[g['arg']][1]}", mini(g['slug']), 'book', li=li)

# ---------- pagina ----------
UMAMI = '<script defer src="https://cloud.umami.is/script.js" data-website-id="301edcb4-f5b2-444e-a1e5-8b8614d0100a" data-domains="serenainmente.it" data-do-not-track="true" data-exclude-search="true" data-exclude-hash="true"></script>'
LOGO = '<img class="logo-mark" src="~/assets/brand/mark-96.png" alt="" width="34" height="34"><span>serenainmente</span>'
NAV = [('/guide/', 'Guide'), ('/risorse/', 'Strumenti'), ('/chi-e-serena/', 'Chi è Serena'), ('/metodo/', 'Il metodo'), ('/fonti/', 'Le fonti')]
ZONE = {'/risorse/': ('/risorse/', '/gestionale/', '/stampabili/', '/strumenti/'), '/chi-e-serena/': ('/chi-e-serena/', '/metodo/', '/fonti/', '/privacy/', '/note-legali/', '/frasi/')}
def qui(path, h):
    return path == h if h == '/' else any(path.startswith(z) for z in ZONE.get(h, (h,)))
# la luce dell'ora, l'aspetto e la grandezza del testo si decidono prima che la pagina compaia (niente lampi)
PRIMA = ("<script>(function(){var d=document.documentElement,h=new Date().getHours(),s=location.search,m=/[?&]ora=(mattino|giorno|sera|notte)/.exec(s),f=/[?&]tema=(chiaro|scuro)/.exec(s),"
         "o=m?m[1]:h<5?'notte':h<12?'mattino':h<18?'giorno':h<22?'sera':'notte',t=null,z=0;try{t=localStorage.getItem('serena:aspetto');z=+localStorage.getItem('serena:testo')||0}catch(e){}"
         "if(f)t=f[1];d.className='js';d.dataset.ora=o;d.dataset.tema=(t==='scuro'||(t!=='chiaro'&&(o==='notte'||matchMedia('(prefers-color-scheme: dark)').matches)))?'scuro':'chiaro';"
         "if(z)d.style.fontSize=['','112.5%','128%'][z]})()</script>")
ESEMPI = ['non vuole dormire', 'domani ho il pediatra', 'spostare una visita', 'le medicine di mamma', 'iscrizione al nido', 'dove trovo un referto']

# Lo stile sta dentro ogni pagina (10 KB compressi): la pagina compare senza aspettare un secondo file. La fonte resta assets/stile3.css.
STILE = re.sub(r'\s*([{};,])\s*', r'\1', re.sub(r'/\*.*?\*/', '', open(os.path.join(ROOT, 'assets', 'stile3.css'), encoding='utf-8').read(), flags=re.S)).replace(';}', '}').strip()
SCRITTI = []
def page(path, title, desc, body, ld=None, cls='', seo=None, og=None):
    canon = SITE + path
    t = 'serenainmente · Serena, parole e idee per chi si prende cura della famiglia' if path == '/' else f'{seo or title} · serenainmente'
    if path == '/' and not ld:
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "WebSite", "name": "serenainmente", "alternateName": ["Serena", "Serena in mente"], "url": SITE + "/",
             "potentialAction": {"@type": "SearchAction", "target": SITE + "/guide/?q={q}", "query-input": "required name=q"}},
            {"@type": "Organization", "name": "Serena", "alternateName": "serenainmente", "url": SITE + "/",
             "logo": SITE + "/assets/brand/avatar-320.png", "sameAs": [IG, "https://www.pinterest.com/serenainmente/"]}]}
    ldj = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ''
    navl = ''.join(f'<a href="~{h}"{" aria-current=page" if qui(path, h) else ""}>{l}</a>' for h, l in NAV)
    def tab(h, l, i): return f'<a href="~{h}"{" aria-current=page" if qui(path, h) else ""}>{ic(i)}<span>{l}</span></a>'
    banner = '<div class="preview-bar">Anteprima del nuovo sito · non ancora pubblicata</div>' if PREVIEW else ''
    rel = '../' * len([x for x in path.strip('/').split('/') if x])
    out = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(t)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">{'<meta name="robots" content="noindex">' if path in ('/privacy/', '/404/', '/salvati/', '/senza-rete/') else ''}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="{'article' if path.startswith('/guide/') and path != '/guide/' else 'website'}">
<meta property="og:image" content="{SITE}/{og or "assets/og.png"}">
<meta name="p:domain_verify" content="82dca4ec0359bf826162f0392b29bb0c"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:locale" content="it_IT">
<meta name="theme-color" content="#FBF6F4">
<meta name="google-site-verification" content="urb5XcUNd0QsSnqqtO49dSjLHeByMvfosPu2Gs2IMlY">
<link rel="icon" type="image/png" href="~/assets/brand/favicon-48.png">
<link rel="apple-touch-icon" href="~/assets/brand/apple-touch-icon.png">
<style>{STILE.replace('url(fonts/', 'url(' + (rel if REL else '/') + 'assets/fonts/')}</style>
{PRIMA}
{'' if PREVIEW else UMAMI}
{ldj}
</head>
<body class="{cls}" data-base="{rel if REL else '/'}"{' data-rel="1"' if REL else ''}>
{banner}
<a class="skip" href="#contenuto">Vai al contenuto</a>
<header class="hd vivo">
<div class="hd-in">
<a class="brand" href="~/" aria-label="serenainmente, pagina iniziale">{LOGO}</a>
<nav class="nav-d" aria-label="Menu principale">{navl}</nav>
<div class="hd-act">
<a class="cerca-d" href="~/guide/#cerca" data-cerca role="button">{ic('search')}<span>Cerca</span><kbd aria-hidden="true">/</kbd></a>
<button class="icbtn" type="button" data-aa aria-label="Cambia la grandezza del testo"><b aria-hidden="true">A+</b></button>
<button class="icbtn tema" type="button" data-tema-btn aria-label="Cambia aspetto"><span class="luna">{ic('moon')}</span><span class="sole">{ic('sun')}</span></button>
</div>
</div>
</header>
<main id="contenuto">
{body}
</main>
<footer class="ft">
<div class="ft-in">
<div class="ft-brand"><a class="brand" href="~/">{LOGO}</a><p>Guide brevi con le loro fonti, strumenti gratuiti e parole in cui ritrovarsi, per chi si prende cura della famiglia.</p>
<a class="ft-ig" href="{IG}" rel="noopener" data-umami-event="instagram">{ic('insta')} Segui @serenainmente</a></div>
<nav aria-label="Esplora"><h2>Esplora</h2><ul><li><a href="~/guide/">Guide</a></li><li><a href="~/risorse/">Strumenti gratuiti</a></li><li><a href="~/gestionale/">Il gestionale di famiglia</a></li>{FRASI_LI}</ul></nav>
<nav aria-label="Serena"><h2>Serena</h2><ul><li><a href="~/chi-e-serena/">Chi è Serena</a></li><li><a href="~/metodo/">Il metodo</a></li><li><a href="~/fonti/">Le fonti</a></li><li><a href="~/correzioni/">Correzioni</a></li><li><a href="~/salvati/">I tuoi salvati</a></li><li><a href="~/privacy/">Privacy</a></li><li><a href="~/note-legali/">Note legali</a></li><li><a href="mailto:{MAIL}?subject=Segnalazione">Scrivi o segnala un errore</a></li></ul></nav>
</div>
<div class="ft-low"><p>Serena è ideata e curata da una persona, con il supporto dell'intelligenza artificiale per testi, immagini e verifica delle fonti. Informazioni generali: non sostituiscono il parere del pediatra o del medico.</p>
<p>Questo sito non usa cookie e non ti chiede dati. Come contiamo le visite: <a href="~/privacy/">Privacy</a>. © {datetime.date.today().year} serenainmente.it <button class="btn btn-line btn-sm" type="button" data-tema-auto hidden>Torna all'aspetto che segue l'ora</button></p></div>
</footer>
<nav class="tab vivo" aria-label="Menu">
{tab('/', 'Inizio', 'home')}{tab('/guide/', 'Guide', 'book')}
<a class="tab-c" href="~/guide/#cerca" data-cerca role="button"{' hidden data-con-casella' if 'class="chiedi' in body else ''}><span class="o">{ic('search')}</span><span>Cerca</span></a>
{tab('/risorse/', 'Strumenti', 'tools')}{tab('/chi-e-serena/', 'Serena', 'leaf')}
</nav>
<dialog class="foglio" id="cerca" data-src="~/assets/cerca-dati.js?v={INDICE_V}" aria-label="Cerca nel sito">
<div class="fg-in"><form class="fg-top" role="search">{ic('search')}<label class="sr" for="q">Cerca nelle guide di Serena</label><input id="q" type="search" placeholder="Che cosa cerchi?" autocomplete="off" enterkeyhint="search"><button type="button" class="icbtn" data-chiudi aria-label="Chiudi la ricerca">{ic('close')}</button></form>
<div class="fg-body"><div data-prima><h2>Per esempio</h2><ul class="esempi">{''.join(f'<li><button type="button" data-q="{e(x)}">{e(x)}</button></li>' for x in ESEMPI)}</ul><p class="small" style="margin-top:14px">La ricerca guarda nelle guide e negli strumenti di Serena. Quello che scrivi resta su questo telefono o computer.</p></div>
<div class="fg-esiti" data-esiti aria-live="polite"></div></div></div>
</dialog>
<script defer src="~/assets/sito.js?v={ver('assets', 'sito.js')}"></script>
</body>
</html>
'''
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
    out = out.replace(' ~/assets/', ' ' + (rel if REL else '/') + 'assets/')
    if path == '/404/': full = os.path.join(OUT, '404.html')
    else: full = os.path.join(OUT, path.strip('/'), 'index.html') if path != '/' else os.path.join(OUT, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(out); SCRITTI.append(full)
    return path

FONTI = {f['id']: f for f in D['fonti']}
def src_block(fid):
    f = FONTI[fid]; dom = f['url'].split('/')[2].replace('www.', '')
    it = dom.endswith('.it') or dom.endswith('.gov.it')
    nota = f'<span class="type">{e(f["nota"])}</span>' if f.get('nota') else ''
    return f'''<li class="src"><span class="org">{e(f['ente'])}, {e(str(f['anno']))}</span><span class="ttl">{e(f['titolo'])}</span><span class="type">{e(f['tipo'])}{'' if it else ' · pagina in inglese'}</span>{nota}<a href="{e(f['url'])}" rel="noopener">Apri la fonte su {e(dom)} {ic('arrow','ic-s')}</a></li>'''

def share(path, title, domanda='Ti è utile? Mandala a chi ne ha bisogno.'):
    url = SITE + path
    wa = 'https://wa.me/?text=' + e(urllib.parse.quote(f"{title} {url}"))
    return f'''<div class="share noprint"><p>{domanda}</p>
<div class="row"><button class="btn" type="button" hidden data-share data-umami-event="condividi" data-title="{e(title)}" data-url="{url}">Manda o salva in Note</button><a class="btn btn-line" href="{wa}" rel="noopener" data-umami-event="whatsapp">Manda su WhatsApp</a><button class="btn btn-line" type="button" data-copytext="{url}" data-done="Indirizzo copiato" data-umami-event="copia-link">Copia l'indirizzo</button></div></div>'''
def salva(path, title):
    return (f'<button class="btn btn-line btn-sm" type="button" hidden data-salva="{path}" data-title="{e(title)}" aria-pressed="false" data-umami-event="salva-per-dopo">{ic("bookmark","ic-s")}<span>Salva per dopo</span></button>'
            f'<button class="btn btn-line btn-sm" type="button" hidden data-ricorda="{path}" data-title="{e(title)}" data-umami-event="ricorda-domattina">{ic("calendar","ic-s")}<span>Ricordamelo domattina</span></button>')

VALORI = [('book', 'Fonti aperte', 'Ogni dato con la sua fonte, da aprire'),
          ('list', 'Cose pratiche', 'Da fare oggi, in pochi minuti'),
          ('lock', 'Niente dati', 'Nessun cookie, nessuna registrazione'),
          ('leaf', 'Nessuna pubblicità', 'Nessuno sponsor dietro i consigli')]
def valori():
    return '<ul class="values" aria-label="I valori di Serena">' + ''.join(f'<li><span class="tic">{ic(i)}</span><span><b>{t}</b><small>{s}</small></span></li>' for i, t, s in VALORI) + '</ul>'

IGCARD = f'''<a class="igcard vetro" href="{IG}" rel="noopener" data-umami-event="instagram"><img src="~/assets/brand/avatar-160.png" alt="" width="52" height="52" loading="lazy"><span><b>@serenainmente</b><small>Ogni mattina alle 10, una cosa utile</small></span><span class="go">Segui {ic('arrow','ic-s')}</span></a>'''

GEST = '~/scarica/gestionale-di-famiglia.xlsx'
SHEETS = D.get('gestionale_sheets_url')
GEST_PUNTI = ['Prima gli impegni: cosa, quando e per chi', 'Scrivi una volta, si aggiorna ovunque',
              'Funziona con Excel, Fogli Google e Numbers', 'Gratuito, e i tuoi dati restano tuoi']

pages = []

STAMPABILI = [('settimana-sul-frigo', 'La settimana di tutti', 'Un foglio da attaccare al frigo: chi va dove, visite, chi accompagna'),
              ('domande-per-il-pediatra', 'Prima della visita dal pediatra', 'Cosa hai notato, le domande in ordine, cosa ha detto il medico'),
              ('lista-delle-medicine', 'La lista delle medicine, scritta insieme', 'Per chi segue un genitore o un nonno: da compilare a quattro mani')]
STN = {f: (t, d) for f, t, d in STAMPABILI}
ST_PER = {'settimana-sul-frigo': 'bambino anziano', 'domande-per-il-pediatra': 'bambino', 'lista-delle-medicine': 'anziano'}
# pagine dedicate ai fogli da stampare: /stampabili/<slug>/
SP_INFO = {
 'settimana-sul-frigo': dict(
   seo='Planner settimanale per la famiglia da stampare (PDF gratis)', h1='La settimana di tutti: il foglio da stampare',
   intro='Un foglio A4 orizzontale da attaccare al frigo: chi va dove, le visite, chi accompagna e chi va a prendere, cosa preparare. Lo vede tutta la famiglia, così non lo deve ricordare una persona sola.',
   contiene=['I sette giorni, dal lunedì alla domenica', 'Chi va dove: scuola, lavoro, sport', 'Visite e appuntamenti', 'Chi accompagna, chi va a prendere', 'Cosa preparare o portare, e cosa c\'è a tavola'],
   come=['Stampalo la domenica sera, anche in bianco e nero.', 'Scrivetelo insieme, a matita: le settimane cambiano, e va bene così.', 'Attaccalo dove passano tutti: il frigo, la porta d\'ingresso.'],
   orient='orizzontale', guida='cartellina-di-famiglia', tool='gestionale'),
 'domande-per-il-pediatra': dict(
   seo='Domande da fare al pediatra: il foglio da stampare (PDF gratis)', h1='Prima della visita dal pediatra: il foglio da stampare',
   intro='Un foglio A4 da compilare a casa, con calma. In ambulatorio i minuti volano: qui le domande non si perdono, e c\'è lo spazio per scrivere cosa ha detto il medico.',
   contiene=['Per chi, quando, quale medico', 'Perché andate e cosa hai notato', 'Le domande, la più importante per prima', 'Cosa fare a casa e quando richiamare', 'Cosa portare e cosa sapere prima di uscire'],
   come=['Compilalo la sera prima, in cinque minuti.', 'Mettilo con la tessera sanitaria e il libretto.', 'In ambulatorio leggi le domande in ordine e scrivi le risposte.'],
   orient='verticale', guida='domande-per-il-pediatra', tool='preparo'),
 'lista-delle-medicine': dict(
   seo='Lista dei farmaci da stampare per anziani e familiari (PDF gratis)', h1='La lista delle medicine, scritta insieme',
   intro='Un foglio A4 verticale, a caratteri grandi, per chi segue un genitore o un nonno: le medicine di ogni giorno, quelle solo al bisogno, il medico e la farmacia. Si compila a quattro mani, con chi le prende: serve a ricordare, non a decidere.',
   contiene=['Nome, medico di famiglia e farmacia', 'Allergie o medicine da evitare', 'Dodici righe per le medicine di ogni giorno: quanto e quando', 'Dietro: le medicine solo quando servono', 'Le domande per la prossima visita'],
   come=['Scrivetela insieme, con le confezioni davanti.', 'Stampala fronte e retro: sono due pagine.', 'Una copia nel portafoglio, una sul frigo.', 'Portatela a ogni visita e aggiornatela quando il medico cambia qualcosa.'],
   orient='verticale', guida='lista-medicine-genitore-anziano', tool='medicine'),
}
def eta_mesi(s):
    """«0-3 mesi» → (0, 3); «1-2 anni» → (12, 35); «Meno di 3 anni» → (0, 35); «Da 3 a 18 anni» → (36, 227). Serve a trovare la riga giusta."""
    m = re.match(r'\s*(\d+)\s*-\s*(\d+)\s*(mesi|anni)\s*$', s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return (a, b) if m.group(3) == 'mesi' else (a * 12, b * 12 + 11)
    m = re.match(r'\s*Meno di (\d+) anni\s*$', s)
    if m: return (0, int(m.group(1)) * 12 - 1)
    m = re.match(r'\s*Da (\d+) a (\d+) anni\s*$', s)
    if m: return (int(m.group(1)) * 12, int(m.group(2)) * 12 - 1)
    if s.strip().startswith('Maggiorenni'): return (216, 1439)
    return None
def per_eta(t): return bool(t) and all(eta_mesi(r[0]) for r in t['righe'])
def tabella(t):
    if not t: return ''
    pe = per_eta(t)
    th = ''.join(f'<th scope="col">{e(c)}</th>' for c in t['colonne'])
    def tr(r):
        at = ' data-eta="%d-%d"' % eta_mesi(r[0]) if pe else ''
        return f'<tr{at}>' + ''.join((f'<th scope="row">{e(c)}</th>' if i == 0 else f'<td>{e(c)}</td>') for i, c in enumerate(r)) + '</tr>'
    nota = '<p class="tua-n" data-tua-n hidden>In evidenza le righe delle età che hai indicato nella pagina iniziale.</p>' if pe else ''
    return f'<section><h2>{e(t["titolo"])}</h2><div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{"".join(tr(r) for r in t["righe"])}</tbody></table></div>{nota}</section>'
def strumento_breve(key):
    if not key: return ''
    h, t = {'gestionale': ('/gestionale/', 'Il gestionale di famiglia'), 'preparo': ('/strumenti/preparo-la-visita/', 'Apri «Preparo la visita»'), 'medicine': ('/strumenti/medicine-di-casa/', 'Apri «Medicine di casa»')}.get(key, (None, None))
    if key == 'gestionale': return ''
    if not h: f = key.split(':', 1)[1]; h, t = f'/stampabili/{f}/', 'Guarda il foglio da stampare'
    return f'<a class="btn btn-full" href="~{h}" data-umami-event="guida-strumento-alto">{t} {ic("arrow","ic-s")}</a>'
def strumento_box(key):
    if not key: return ''
    if key == 'gestionale':
        return f'''<aside class="tool"><span class="chip">Strumento gratuito</span><h2>Il gestionale di famiglia</h2><p>Visite, scadenze e documenti in un file solo. I dati restano tuoi.</p><a class="btn" href="~/gestionale/" data-umami-event="guida-strumento" data-umami-event-tool="gestionale">Scopri il gestionale {ic('arrow','ic-s')}</a></aside>'''
    if key == 'preparo':
        return f'''<aside class="tool"><span class="chip">Strumento gratuito, dal telefono</span><h2>Preparo la visita</h2><p>Scrivi a casa cosa hai notato e le domande in ordine; in ambulatorio le hai davanti, con lo spazio per le risposte. Resta solo sul tuo telefono.</p><a class="btn" href="~/strumenti/preparo-la-visita/" data-umami-event="guida-strumento" data-umami-event-tool="preparo">Apri lo strumento {ic('arrow','ic-s')}</a></aside>'''
    if key == 'medicine':
        return f'''<aside class="tool"><span class="chip">Strumento gratuito, dal telefono</span><h2>Medicine di casa</h2><p>Scrivi la lista una volta: la stampi grande, la mandi a un familiare o al medico, e il telefono ti ricorda gli orari. Resta solo sul tuo telefono.</p><div class="row"><a class="btn" href="~/strumenti/medicine-di-casa/" data-umami-event="guida-strumento" data-umami-event-tool="medicine">Apri lo strumento {ic('arrow','ic-s')}</a><a class="btn btn-line" href="~/stampabili/lista-delle-medicine/">Oppure il foglio da stampare</a></div></aside>'''
    f = key.split(':', 1)[1]; t, d = STN[f]
    return f'''<aside class="tool"><span class="chip">Foglio da stampare, gratis</span><h2>{e(t)}</h2><p>{e(d)}. Un foglio da compilare a penna.</p><div class="row"><a class="btn" href="~/scarica/{f}.pdf" download data-umami-event="stampabile" data-umami-event-file="{f}">{ic('download','ic-s')} Scarica il foglio (PDF)</a><a class="btn btn-line" href="~/stampabili/{f}/">Guardalo prima</a></div></aside>'''
# (indirizzo, titolo, descrizione, icona, chiave, per chi, miniatura, etichetta)
TOOLS = [('/strumenti/preparo-la-visita/', 'Preparo la visita', 'Le domande in ordine e lo spazio per le risposte. Si usa dal telefono.', 'list', 'preparo', 'bambino anziano', None, 'Dal telefono'),
         ('/strumenti/medicine-di-casa/', 'Medicine di casa', 'La lista delle medicine, da stampare grande o mandare, con i promemoria degli orari.', 'clock', 'medicine', 'anziano', None, 'Dal telefono'),
         ('/gestionale/', 'Il gestionale di famiglia', 'Visite, scadenze, documenti e la settimana in un file solo.', 'calendar', 'gestionale', 'bambino anziano', mini('gestionale'), 'File gratuito')] + \
        [(f'/stampabili/{f}/', t, d + '.', 'download', f, ST_PER[f], mini('foglio-' + f), 'Da stampare') for f, t, d in STAMPABILI]
def tools_fila():
    def c(h, t, d, i, k, per, im, et):
        top = f'<img class="thumb" src="~/assets/stampabili/{k}-sm.webp" alt="" width="560" height="350" loading="lazy" decoding="async">' if esiste('assets', 'stampabili', f'{k}-sm.webp') else f'<span class="tic">{ic(i)}</span>'
        return f'<li><a class="tcard vetro" href="~{h}" data-umami-event="home-strumento" data-umami-event-tool="{k}">{top}<b>{e(t)}</b><small>{e(d)}</small><span class="chip">{et}</span></a></li>'
    return '<ul class="fila">' + ''.join(c(*x) for x in TOOLS) + '</ul>'

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
def checklist_xlsx(g):
    """Crea guide/<slug>/checklist.xlsx: nella colonna «Fatto» si sceglie Sì da un menu, e la riga si colora e si barra."""
    wb = Workbook(); ws = wb.active; ws.title = 'Lista'
    malva, ink = '97606F', '3A2C30'
    ws.column_dimensions['A'].width = 11; ws.column_dimensions['B'].width = 60; ws.column_dimensions['C'].width = 28
    ws['A1'] = g['titolo']; ws['A1'].font = Font(name='Georgia', size=16, bold=True, color=ink); ws.merge_cells('A1:C1')
    ws['A2'] = 'Tocca una casella della colonna «Fatto» e scegli Sì: la riga si colora.'; ws['A2'].font = Font(size=11, italic=True, color='5F4D52'); ws.merge_cells('A2:C2')
    ws.row_dimensions[1].height = 28; ws.row_dimensions[2].height = 20
    for col, t in zip('ABC', ['Fatto', 'Cosa', 'Note']):
        c = ws[f'{col}4']; c.value = t; c.font = Font(bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor=malva)
        c.alignment = Alignment(vertical='center'); ws.row_dimensions[4].height = 22
    thin = Side(style='thin', color='EADCDF'); box = Side(style='medium', color=malva)
    dv = DataValidation(type='list', formula1='"Sì,No"', allow_blank=True, showDropDown=False)
    dv.promptTitle = 'Fatto?'; dv.prompt = 'Scegli Sì quando è fatto'; dv.showInputMessage = True; ws.add_data_validation(dv)
    n = len(g.get('checklist', []))
    for i, item in enumerate(g.get('checklist', []), start=5):
        ws[f'A{i}'].alignment = Alignment(horizontal='center', vertical='center'); ws[f'A{i}'].font = Font(size=12, bold=True, color=malva)
        ws[f'A{i}'].border = Border(left=box, right=box, top=box, bottom=box)
        ws[f'B{i}'] = item; ws[f'B{i}'].alignment = Alignment(wrap_text=True, vertical='center'); ws.row_dimensions[i].height = 26
        dv.add(ws[f'A{i}'])
        for col in 'BC': ws[f'{col}{i}'].border = Border(bottom=thin)
    if n:
        ws.conditional_formatting.add(f'A5:C{4 + n}', FormulaRule(formula=['$A5="Sì"'], fill=PatternFill('solid', bgColor='E3ECDD', fgColor='E3ECDD'), font=Font(strike=True, color='5F4D52')))
        ws[f'B{6 + n}'] = '=COUNTIF(A5:A%d,"Sì")&" su %d fatte"' % (4 + n, n); ws[f'B{6 + n}'].font = Font(bold=True, color=malva)
    k = 8 + n
    ws[f'B{k}'] = f"Da serenainmente.it/guide/{g['slug']}/ · {g['avvertenza']}"; ws[f'B{k}'].font = Font(size=9, color='5F4D52'); ws[f'B{k}'].alignment = Alignment(wrap_text=True, vertical='top'); ws.merge_cells(f'B{k}:C{k}'); ws.row_dimensions[k].height = 54
    ws.freeze_panes = 'A5'; ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = 'portrait'; ws.page_setup.fitToWidth = 1; ws.print_options.horizontalCentered = True
    d = os.path.join(ROOT, 'guide', g['slug']); os.makedirs(d, exist_ok=True)
    wb.save(os.path.join(d, 'checklist.xlsx'))


# ---------- guide ----------
# «Calcola la scadenza»: il conto lo fa il telefono con la regola scritta nella guida (vedi assets/sito.js)
def storia(g):
    """Cosa è cambiato in una guida: voci scritte a mano in dati.json («storia»: [[data, testo], …]), più la prima versione."""
    return sorted([tuple(x) for x in g.get('storia', [])], reverse=True) + [(g['data'], 'prima versione.')]
CALC = {'carta-identita-bambini': ('cie', 'Rinnovare la carta d\'identità'), 'certificato-sport-bambini': ('anno', 'Rinnovare il certificato per lo sport')}
def calcolo(g):
    if g['slug'] not in CALC: return ''
    tipo, tit = CALC[g['slug']]
    nasc = '<label><span>Data di nascita</span><input type="date" data-nascita></label>' if tipo == 'cie' else ''
    return (f'<section class="box box-salvia calc noprint" data-calc="{tipo}" data-titolo="{e(tit)}" data-url="{SITE}/guide/{g["slug"]}/"><h2>Calcola la scadenza</h2>'
            f'<div class="pv-grid2">{nasc}<label><span>Data di rilascio</span><input type="date" data-rilascio></label></div>'
            f'<p class="calc-o" data-esito aria-live="polite"></p><button class="btn" type="button" data-cal hidden data-umami-event="scadenza-calendario">{ic("calendar","ic-s")} Mettila in calendario</button>'
            f'<p class="small">Il conto lo fa il tuo telefono, con la regola scritta in questa guida: le date non arrivano a nessuno. Fa fede la data scritta sul documento.</p></section>')
def azioni_lista(g, cktext):
    u = f"{SITE}/guide/{g['slug']}/"
    return (f'<div class="row noprint"><button class="btn" type="button" hidden data-sharetext="{cktext}" data-umami-event="checklist-note">Salva in Note o Promemoria</button>'
            f'<button class="btn btn-line" type="button" data-ics data-umami-event="checklist-calendario">{ic("calendar","ic-s")} Ricordamelo domattina</button>'
            f'<button class="btn btn-line" type="button" data-stampa-lista data-umami-event="checklist-stampa">Stampa solo la lista</button>'
            f'<button class="btn btn-line" type="button" data-copialista data-umami-event="checklist-copia">Copia la lista</button>'
            f'<button class="btn btn-line" type="button" data-ckreset hidden>Azzera le spunte</button></div>')
for g in GUIDE:
    a = ARGN[g['arg']]
    if g.get('checklist'): checklist_xlsx(g)
    steps = ''.join(f'<li><details id="passo-{i+1}"{" open" if i == 0 else ""}><summary data-leggi>{e(s[0])}</summary><p data-leggi>{e(s[1])}</p></details></li>' for i, s in enumerate(g['passi']))
    breve = ''.join(f'<li><a href="#passo-{i+1}">{e(s[0])}</a></li>' for i, s in enumerate(g['passi']))
    errori = ''.join(f'<li data-leggi>{e(x)}</li>' for x in g.get('errori', []))
    check = ''.join(f'<li><label><input type="checkbox" data-ck="{g["slug"]}-{i}"><span class="cbx" aria-hidden="true">{ic("check","ic-s")}</span><span>{e(x)}</span></label></li>' for i, x in enumerate(g.get('checklist', [])))
    cktext = e(g['titolo'] + '\n' + '\n'.join('☐ ' + x for x in g.get('checklist', [])) + '\nserenainmente.it/guide/' + g['slug'] + '/')
    d0 = datetime.date.fromisoformat(g['agg']); m6 = d0.month + 6; prossimo = f"{MESI[(m6 - 1) % 12]} {d0.year + (m6 - 1) // 12}"
    segnala = 'mailto:' + MAIL + '?subject=' + urllib.parse.quote('Segnalazione: ' + g['titolo'])
    fonti = ''.join(src_block(fid) for fid in g['fonti'])
    nf = len(g['fonti'])
    corr = [x for x in GUIDE if x is not g and x['arg'] == g['arg']] + [x for x in GUIDE if x is not g and x['arg'] != g['arg']]
    gp = f"/guide/{g['slug']}/"
    fonti_meta = f'<a href="#fonti">{nf} {"fonte" if nf == 1 else "fonti"}, da aprire</a>' if nf else ''
    lista = (f'<section class="box box-salvia ck" id="lista" data-titolo="{e(g["titolo"])}" data-url="{SITE}{gp}"><div class="ck-hd"><svg class="anello" viewBox="0 0 48 48" aria-hidden="true"><circle class="p" cx="24" cy="24" r="20"/><circle class="v" cx="24" cy="24" r="20"/></svg><div><h2>La lista da spuntare</h2><p class="ck-n" data-ckn aria-live="polite"></p></div></div>'
             f'<ul class="check">{check}</ul><p class="small noprint">Le spunte restano salvate su questo telefono o computer.</p>{azioni_lista(g, cktext)}</section>') if check else ''
    body = f'''<article class="art">
<header class="art-hd wrap-t">
<nav class="crumbs" aria-label="Percorso"><a href="~/guide/#{a[0]}">‹ Guide · {e(a[1])}</a></nav>
<h1 data-leggi>{e(g['titolo'])}</h1>
<div class="azioni noprint"><button class="btn btn-line btn-sm" type="button" hidden data-ascolta aria-pressed="false" data-umami-event="ascolta-guida">{ic('sound','ic-s')}<span>Ascolta la guida</span></button></div>
</header>
<div class="art-body wrap-t">
<section class="breve vetro" aria-label="In breve"><p data-leggi>{e(g['sommario'])}</p>
{tabella(g.get('tabella')) if per_eta(g.get('tabella')) else ''}
{strumento_breve(g.get('strumento'))}
<h2 class="passi-t">Come si fa, un passo alla volta</h2>
<ol class="passi">{steps}</ol>
<dl class="facts"><div><dt>Tempo</dt><dd>{e(g['tempo'])}</dd></div><div><dt>Cosa serve</dt><dd>{e(g['serve'])}</dd></div></dl></section>
<div class="sotto-breve"><p class="meta"><span>{ic('clock','ic-s')} {g['min']} min di lettura</span><span>Aggiornata il {data_it(g['agg'])}</span>{fonti_meta}</p>
<div class="azioni noprint">{salva(gp, g['titolo'])}</div></div>
{'' if per_eta(g.get('tabella')) else tabella(g.get('tabella'))}
{calcolo(g)}
<section><h2 data-leggi>Perché aiuta</h2>{''.join(f'<p data-leggi>{e(p)}</p>' for p in g['perche'])}</section>
{f'<section class="box box-rosa"><h2 data-leggi>Errori comuni</h2><ul class="plain">{errori}</ul></section>' if errori else ''}
{lista}
{strumento_box(g.get('strumento')) if g.get('strumento') == 'gestionale' else ''}
{foto(g['slug'], '', 'art-img', sizes='(min-width:760px) 700px, 100vw')}
{f'<section id="fonti"><h2>Le fonti</h2><p class="small">Ogni dato di questa pagina viene da qui.</p><ul class="sources">{fonti}</ul></section>' if fonti else ''}
<details class="piega fatta" id="come-e-fatta"><summary>Come è stata fatta questa guida</summary>
<ul class="plain"><li>{f'{nf} {"fonte" if nf == 1 else "fonti"}, aperte e lette prima di scrivere' if nf else 'Consigli organizzativi: non cita dati sanitari'}.</li><li>Fonti controllate il {data_it(g['agg'])}. Prossimo controllo entro {prossimo}.</li><li>Scritta con il supporto dell'intelligenza artificiale; letta e approvata da una persona prima di uscire.</li></ul>
<p class="small"><b>Cosa è cambiato.</b> {' '.join(f"{data_it(d)}: {e(t)}" for d, t in storia(g))}</p>
<div class="row noprint"><a class="btn btn-line btn-sm" href="~/metodo/">Il metodo</a><a class="btn btn-line btn-sm" href="~/correzioni/">Tutte le correzioni</a></div></details>
<p class="small fatta-r">Fonti controllate il {data_it(g['agg'])}; prossimo controllo entro {prossimo}. <a href="{segnala}" data-umami-event="segnala-errore">Segnala un errore</a></p>
<aside class="box box-line"><b>Da sapere</b><p data-leggi>{e(g['avvertenza'])}</p></aside>
{share(gp, g['titolo'])}
</div>
<section class="related wrap-t noprint"><div class="sec-hd"><h2>Continua a leggere</h2><a class="more" href="~/guide/">Tutte le guide {ic('arrow','ic-s')}</a></div>
<ul class="rows">{''.join(riga_guida(x) for x in corr[:3])}</ul></section>
</article>'''
    url = f"{SITE}{gp}"
    art = {"@type": "Article", "headline": g['titolo'], "description": g['sommario'], "mainEntityOfPage": url,
          "datePublished": g['data'], "dateModified": g['agg'], "inLanguage": "it", "articleSection": a[1],
          "isAccessibleForFree": True,
          "author": {"@type": "Organization", "name": "Serena", "url": SITE + "/chi-e-serena/"},
          "publisher": {"@type": "Organization", "name": "Serena", "logo": {"@type": "ImageObject", "url": SITE + "/assets/brand/avatar-320.png"}}}
    if esiste('assets', 'foto', f"{g['slug']}.webp"): art["image"] = f"{SITE}/assets/foto/{g['slug']}.webp"
    if g['fonti']: art["citation"] = [{"@type": "CreativeWork", "name": FONTI[f]['titolo'], "url": FONTI[f]['url'], "publisher": FONTI[f]['ente']} for f in g['fonti']]
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Guide", "item": SITE + "/guide/"},
        {"@type": "ListItem", "position": 2, "name": a[1], "item": SITE + "/guide/#" + a[0]},
        {"@type": "ListItem", "position": 3, "name": g['titolo'], "item": url}]}
    ld = {"@context": "https://schema.org", "@graph": [art, crumbs]}
    ogp = f"assets/og/{g['slug']}.jpg" if esiste('assets', 'og', f"{g['slug']}.jpg") else None
    pages.append(page(gp, g['titolo'], g['sommario'], body, ld, seo=g.get('titolo_seo'), og=ogp))

# ---------- elenco delle guide ----------
CHIEDI = f'<a class="chiedi cede" href="~/guide/#cerca" data-cerca role="button" data-umami-event="cerca-apri-casella">{ic("search")}<span>Cerca nelle guide di Serena</span><i>{ic("arrow")}</i></a>'
argc = {a[0]: sum(1 for g in GUIDE if g['arg'] == a[0]) for a in ARG}
chips = '<button type="button" class="fchip" data-arg="tutti" aria-pressed="true">Tutte</button>' + ''.join(
    f'<button type="button" class="fchip" data-arg="{a[0]}" aria-pressed="false">{e(a[1])}</button>' for a in ARG if argc[a[0]])
def riga_elenco(g):
    return riga(f"~/guide/{g['slug']}/", g['titolo'], f"{g['min']} min · {ARGN[g['arg']][1]} · {data_it(g['agg'])}", mini(g['slug']), 'book', li=f' data-a="{g["arg"]}"')
pages.append(page('/guide/', 'Guide', 'Guide pratiche e brevi per la vita di famiglia, con le fonti quando servono.', f'''
<section class="ph-hd wrap-t">
<h1>Guide</h1><p class="lead">Piccoli metodi per giornate più leggere e le regole che nessuno ti spiega. Si leggono in due minuti, con le fonti.</p>
{CHIEDI}
</section>
<section class="wrap-t list">
<div class="fchips" role="group" aria-label="Scegli un argomento">{chips}</div>
<h2 class="sr">Elenco delle guide</h2>
<ul class="rows" data-grid>{''.join(riga_elenco(g) for g in GUIDE)}</ul>
</section>''', cls='p-list'))

# ---------- gestionale ----------
SCHEDE = [('Inizia da qui', 'Appena lo apri: le scadenze dei prossimi 30 giorni, le visite delle prossime due settimane, i documenti da rinnovare e la lista dei prossimi impegni, dal più vicino. Più sotto, quello che è rimasto indietro.'),
          ('Famiglia', 'I nomi di casa, scritti una volta sola: diventano il menu di tutte le altre schede. L\'età si calcola dalla data di nascita.'),
          ('Scadenze', 'Richiami, rinnovi, iscrizioni, pagamenti. Se si ripete ogni mese o ogni anno, la data si sposta da sola. Spunta «Fatto» e sparisce.'),
          ('Visite', 'Data, ora, per chi e dove; lo stato (programmata, completata, annullata); la data entro cui disdire, che puoi correggere se la tua struttura dice diverso; il ticket. Poi le domande da fare.'),
          ('Documenti', 'La cartellina: dove sta ogni documento, su carta e online, e quando scade. Due mesi prima compare tra gli impegni.'),
          ('Settimana, Contatti, Prime volte', 'La settimana fissa di tutti, i numeri utili da stampare, i ricordi scritti il giorno stesso.')]
b_excel = f'<a class="btn {{c}}" href="{GEST}" download data-umami-event="gestionale-excel">{ic("download","ic-s")} Scarica il file Excel</a>'
b_fogli = f'<a class="btn {{c}}" href="{e(SHEETS)}" rel="noopener" data-umami-event="gestionale-fogli">Apri in Fogli Google</a>' if SHEETS else ''
passi_pc = '<ol><li>Scarica il file Excel e aprilo.</li><li>Nella scheda <b>Famiglia</b> scrivi i nomi di casa.</li><li>Aggiungi una visita o una scadenza, poi apri <b>Inizia da qui</b>: trovi il riepilogo.</li></ol>'
passi_tel = '<ol><li>Tocca «Apri in Fogli Google».</li><li>Google ti propone di fare una copia: tocca <b>Crea una copia</b>. È tua, nel tuo Drive.</li><li>Nella scheda <b>Famiglia</b> scrivi i nomi di casa.</li><li>Aggiungi il primo impegno e usa il file dall\'app Fogli Google.</li></ol>'
pages.append(page('/gestionale/', 'Il gestionale di famiglia', 'Un file gratuito per organizzare documenti, scadenze, visite, la settimana e i ricordi della famiglia.', f'''
<section class="gs-hero wrap">
<div class="gs-txt"><span class="chip">File gratuito · senza registrazione</span><h1>Il gestionale di famiglia</h1>
<p class="lead">Il quaderno di casa, in un file solo. Lo apri e vedi subito cosa c'è da fare, entro quando e per chi: visite, scadenze e documenti.</p>
<div class="row solo-tocco">{b_fogli.format(c='')}{b_excel.format(c='btn-line')}</div>
<div class="row solo-mouse">{b_excel.format(c='')}{b_fogli.format(c='btn-line')}</div>
<p class="small solo-tocco">Dal telefono conviene Fogli Google: tocca «Apri in Fogli Google», poi «Crea una copia», e il file è tuo. Nessun dato che scrivi arriva a Serena.</p>
<p class="small solo-mouse">Sul computer si apre con Excel o Numbers. Nessun dato che scrivi arriva a Serena.</p>
<div class="azioni">{salva('/gestionale/', 'Il gestionale di famiglia')}</div></div>
<img class="gs-shot" src="~/assets/gestionale/inizia-sm.webp" srcset="~/assets/gestionale/inizia-sm.webp 800w, ~/assets/gestionale/inizia.webp 1600w" sizes="(min-width:960px) 520px, 92vw" alt="La prima scheda del file, «Inizia da qui»: le scadenze dei prossimi giorni e i prossimi impegni" width="1600" height="1000" decoding="async" fetchpriority="high">
</section>
<section class="wrap-t gs-body">
<section><h2>Come si comincia</h2>
<details class="piega solo-tocco" open><summary>Dal telefono, in 4 passaggi</summary>{passi_tel}</details>
<details class="piega solo-tocco"><summary>Dal computer, in 3 passaggi</summary>{passi_pc}</details>
<details class="piega solo-mouse" open><summary>Dal computer, in 3 passaggi</summary>{passi_pc}</details>
<details class="piega solo-mouse"><summary>Dal telefono, in 4 passaggi</summary>{passi_tel}</details>
</section>
<section><ul class="ticks">{''.join(f'<li>{ic("check","ic-s")}<span>{p}</span></li>' for p in GEST_PUNTI)}</ul></section>
<figure class="vid"><video controls playsinline muted preload="none" poster="~/video/gestionale-tutorial.jpg" width="1080" height="1920" data-umami-event="gestionale-video"><source src="~/video/gestionale-tutorial.mp4" type="video/mp4"></video>
<figcaption><b>Come si usa, in un minuto.</b> Il video è senza audio.</figcaption></figure>
<section><h2>Cosa c'è dentro</h2>
{''.join(f'<details class="piega"><summary>{e(a)}</summary><p>{e(b)}</p></details>' for a, b in SCHEDE)}</section>
<figure class="shot"><img src="~/assets/gestionale/visite.webp" alt="La scheda Visite: data, ora, per chi, medico o struttura, stato, data entro cui disdire e ticket" loading="lazy" decoding="async" width="1800" height="478"><figcaption>La scheda Visite, con le righe di esempio che trovi nel file.</figcaption></figure>
<section class="box box-salvia"><h2>Come si usa</h2><ul class="plain"><li>Comincia dalla scheda Famiglia: scrivi i nomi di casa.</li><li>Le celle da compilare hanno il testo blu; quelle nere si calcolano da sole. Le righe di esempio vanno cancellate.</li><li>Sul computer aprilo con Excel; sul telefono usa la copia in Fogli Google.</li><li>Il file non manda notifiche: ti mostra cosa arriva ogni volta che lo apri.</li><li>Non è un archivio medico: scrivi solo quello che serve. Il file resta dove lo salvi tu, e nessun dato arriva a Serena.</li></ul></section>
<section><h2>Preferisci qualcosa di più semplice?</h2><ul class="rows">{riga('~/strumenti/preparo-la-visita/', 'Preparo la visita', 'Si usa dal telefono, senza scaricare niente', icona='list')}{riga('~/strumenti/medicine-di-casa/', 'Medicine di casa', 'Per chi segue una persona anziana: lista, stampa grande e promemoria', icona='clock')}{riga('~/stampabili/settimana-sul-frigo/', 'La settimana di tutti', 'Un foglio da stampare e attaccare al frigo', mini('foglio-settimana-sul-frigo'))}</ul></section>
<p class="small">Informazioni organizzative generali. Per vaccini, terapie e documenti sanitari il riferimento resta il pediatra, il medico o la ASL.</p>
{share('/gestionale/', 'Il gestionale di famiglia')}
</section>'''))

# ---------- strumenti gratuiti ----------
ck_rows = ''.join(f'''<li class="due"><a class="rowl" href="~/guide/{g['slug']}/#lista"><span class="t"><b>{e(g['titolo'])}</b><small>{len(g['checklist'])} cose da spuntare · si usa sul sito</small></span></a><a class="dl" href="~/guide/{g['slug']}/checklist.xlsx" download data-umami-event="checklist-excel" data-umami-event-guida="{g['slug']}" aria-label="Scarica la lista «{e(g.get('titolo_seo') or g['titolo'])}» in Excel">{ic('download','ic-s')} Excel</a></li>''' for g in GUIDE if g.get('checklist'))
st_rows = ''.join(f'''<li class="due"><a class="rowl" href="~/stampabili/{f}/"><img src="~{mini('foglio-' + f)}" alt="" width="64" height="64" loading="lazy"><span class="t"><b>{e(t)}</b><small>{e(d)}</small></span></a><a class="dl" href="~/scarica/{f}.pdf" download data-umami-event="stampabile" data-umami-event-file="{f}" aria-label="Scarica «{e(t)}» in PDF">{ic('download','ic-s')} PDF</a></li>''' for f, t, d in STAMPABILI)
pages.append(page('/risorse/', 'Strumenti gratuiti', 'Strumenti gratuiti per la famiglia: Preparo la visita, il gestionale di famiglia, fogli da stampare e le liste delle guide.', f'''
<section class="ph-hd wrap-t"><h1>Strumenti gratuiti</h1><p class="lead">Da usare subito, senza registrazione. Quello che scrivi resta sul tuo telefono o computer.</p></section>
<section class="wrap-t"><h2 class="sec-t">Dal telefono, senza scaricare niente</h2><ul class="rows">{riga('~/strumenti/preparo-la-visita/', 'Preparo la visita', 'Le domande in ordine e lo spazio per le risposte del medico', icona='list')}{riga('~/strumenti/medicine-di-casa/', 'Medicine di casa', 'La lista delle medicine: si stampa grande, si manda, ricorda gli orari', icona='clock')}</ul></section>
<section class="wrap-t"><h2 class="sec-t">Fogli da stampare</h2><ul class="rows">{st_rows}</ul></section>
<section class="wrap-t"><h2 class="sec-t">Per chi usa il computer</h2><ul class="rows">{riga('~/gestionale/', 'Il gestionale di famiglia', 'Visite, scadenze, documenti e la settimana in un file Excel', mini('gestionale'))}</ul></section>
<section class="wrap-t"><h2>Le liste da spuntare delle guide</h2><p class="lead-s">Ogni guida ha la sua lista: la spunti sul sito, la salvi in Note o la metti in calendario.</p><ul class="rows">{ck_rows}</ul></section>'''))

# ---------- pagine dei fogli da stampare ----------
for f, t, d in STAMPABILI:
    I = SP_INFO[f]
    g = GN.get(I['guida'])
    rel = ''
    if I['tool'] == 'preparo':
        rel += riga('~/strumenti/preparo-la-visita/', 'Preparo la visita', 'La stessa cosa sul telefono, senza stampare', icona='list')
    if I['tool'] == 'medicine':
        rel += riga('~/strumenti/medicine-di-casa/', 'Medicine di casa', 'La stessa lista sul telefono, con i promemoria degli orari', icona='clock')
    if g: rel += riga_guida(g)
    if I['tool'] == 'gestionale':
        rel += riga('~/gestionale/', 'Il gestionale di famiglia', 'Visite, scadenze, documenti e la settimana in un file', mini('gestionale'))
    for f2, t2, d2 in STAMPABILI:
        if f2 != f: rel += riga(f'~/stampabili/{f2}/', t2, 'Foglio da stampare', mini('foglio-' + f2))
    ld = {"@context": "https://schema.org", "@type": "DigitalDocument", "name": I['h1'], "description": I['intro'], "encodingFormat": "application/pdf",
          "url": f"{SITE}/stampabili/{f}/", "contentUrl": f"{SITE}/scarica/{f}.pdf", "image": f"{SITE}/assets/stampabili/{f}.webp", "isAccessibleForFree": True, "inLanguage": "it",
          "publisher": {"@type": "Organization", "name": "Serena", "url": SITE}}
    sp = f'/stampabili/{f}/'
    pages.append(page(sp, I['h1'], I['intro'][:155], f'''
<section class="wrap sp-page">
<nav class="crumbs" aria-label="Percorso"><a href="~/risorse/">‹ Strumenti gratuiti</a></nav>
<div class="sp-grid">
<div class="sp-txt"><span class="chip">Foglio da stampare · gratis</span><h1>{e(I['h1'])}</h1><p class="lead">{e(I['intro'])}</p>
<div class="row"><a class="btn" href="~/scarica/{f}.pdf" download data-umami-event="stampabile" data-umami-event-file="{f}" data-umami-event-da="pagina">{ic('download','ic-s')} Scarica il foglio (PDF)</a><a class="btn btn-line solo-mouse" href="~/scarica/{f}.pdf" target="_blank" rel="noopener" data-umami-event="stampabile-apri" data-umami-event-file="{f}">Apri e stampa</a></div>
<p class="small">Un foglio A4 {I['orient']}. Si stampa anche in bianco e nero.</p>
</div>
<figure class="sp-prev"><button type="button" data-zoom aria-label="Guarda il foglio da vicino"><img src="~/assets/stampabili/{f}-sm.webp" srcset="~/assets/stampabili/{f}-sm.webp 560w, ~/assets/stampabili/{f}.webp 1100w" sizes="(min-width:960px) 46vw, 92vw" alt="Anteprima del foglio «{e(t)}»" fetchpriority="high" decoding="async" width="{1100 if I['orient'] == 'orizzontale' else 778}" height="{778 if I['orient'] == 'orizzontale' else 1100}"></button><span class="lente">{ic('zoom','ic-s')} Guardalo da vicino</span></figure>
<div class="sp-altro">
<section class="box box-rosa noprint"><h2>Non hai una stampante adesso?</h2><div class="row">{salva(sp, t)}<button class="btn btn-line btn-sm" type="button" hidden data-share data-title="{e(I['h1'])}" data-url="{SITE}{sp}" data-umami-event="stampabile-manda">Mandalo a chi può stamparlo</button>{'<a class="btn btn-line btn-sm" href="~/strumenti/preparo-la-visita/">Fallo dal telefono</a>' if I['tool'] == 'preparo' else ''}{'<a class="btn btn-line btn-sm" href="~/strumenti/medicine-di-casa/">Scrivila dal telefono</a>' if I['tool'] == 'medicine' else ''}</div></section>
<section><h2>Cosa contiene</h2><ul class="ticks">{''.join(f'<li>{ic("check","ic-s")}<span>{e(x)}</span></li>' for x in I['contiene'])}</ul></section>
<section><h2>Come usarlo</h2><ol class="sp-come">{''.join(f'<li>{e(x)}</li>' for x in I['come'])}</ol></section>
</div>
</div>
</section>
<dialog class="zoom" aria-label="Il foglio da vicino"><div class="zin"><img src="~/assets/stampabili/{f}.webp" alt="Il foglio «{e(t)}» ingrandito" loading="lazy"></div><button class="icbtn x" type="button" aria-label="Chiudi">{ic('close')}</button></dialog>
<section class="wrap-t"><h2 class="sec-t">Ti può servire anche</h2><ul class="rows">{rel}</ul>
<p class="small" style="margin-top:14px">Foglio gratuito, per uso personale e familiare. Strumento organizzativo: non sostituisce il parere del medico o del farmacista.</p>
{share(sp, I['h1'])}</section>''', ld=ld, seo=I['seo'], og=f'assets/og/stampabili-{f}.jpg'))

# ---------- chi è serena ----------
CHI = {s[0]: s[1] for s in D['chi']['sezioni']}
QUOTE = 'Crediamo in una quotidianità più semplice, in famiglie più consapevoli, e in un po\' più di tempo per chi si prende cura degli altri.'
SEGNALA = f'mailto:{MAIL}?subject=Segnalazione'
NON_FA = ['Non dà diagnosi e non dice cosa ha un bambino o un adulto.', 'Non suggerisce medicine né quantità: quelle le decide il medico.', 'Non ti chiede dati e non ha un\'area riservata.', 'Non ha sponsor né pubblicità dietro ai consigli.', 'Non sostituisce il pediatra, il medico o il farmacista.']
PROCESSO = [('Una domanda vera', 'Si parte da quello che le famiglie chiedono davvero: dove trovo un referto, cosa succede se salto una visita, quante ore deve dormire un bambino.'),
            ('Le fonti, prima del testo', 'Si cercano enti e istituzioni: Organizzazione Mondiale della Sanità, Istituto Superiore di Sanità, Ministeri, Regioni, società scientifiche. Una fonte entra solo dopo essere stata aperta e letta, e se ne riportano i limiti: età, anno del dato.'),
            ('La scrittura', 'Il testo si scrive con il supporto dell\'intelligenza artificiale, in parole semplici. Niente dosaggi, niente diagnosi.'),
            ('Il controllo di una persona', 'Una persona legge ogni pagina, la confronta con le fonti e decide se pubblicarla. Niente esce da solo.'),
            ('La data, in vista', 'Ogni guida dice quando è stata aggiornata, quando sono state controllate le fonti e entro quando verranno ricontrollate: almeno ogni sei mesi, e subito se cambia una regola.'),
            ('La correzione', 'Se trovi un errore o un collegamento che non funziona, scrivi a ' + MAIL + ': correggiamo e indichiamo la data dell\'aggiornamento.')]
pages.append(page('/chi-e-serena/', 'Chi è Serena', D['chi']['sommario'], f'''
<section class="chi-hero wrap"><div class="ph-hd" style="padding:0"><h1>Chi è Serena</h1><p class="lead">{e(D['chi']['sommario'])}</p></div>{foto('chi', '', 'chi-img', eager=True)}</section>
<section class="wrap-t prose">
<h2 style="margin-top:0">Chi c'è dietro</h2>
<p>Serena è il nome del progetto. Lo cura una persona: sceglie gli argomenti, controlla le fonti e approva ogni pagina prima che esca. L'intelligenza artificiale aiuta a scrivere i testi, a comporre le immagini e a cercare le fonti.</p>
<p>I dati non vengono da noi: vengono da enti e istituzioni che puoi aprire da ogni pagina.</p>
<div class="row"><a class="btn btn-line" href="~/metodo/">Come nasce una guida</a><a class="btn btn-line" href="~/fonti/">Tutte le fonti</a></div>
<h2>Cosa Serena non fa</h2><ul class="ticks no">{''.join(f'<li>{ic("close","ic-s")}<span>{x}</span></li>' for x in NON_FA)}</ul>
<blockquote class="quote"><p>{QUOTE}</p></blockquote>
<h2>Perché nasce</h2><p>Chi si prende cura di una famiglia tiene a mente tutto: la visita da prenotare, il documento che scade, la domanda da fare al pediatra, la routine della sera. Serena nasce per alleggerire questo carico: informazioni affidabili, guide pratiche e strumenti utili, in parole semplici.</p>
<h2>Cosa facciamo</h2>{''.join(f'<p>{e(p)}</p>' for p in CHI['Cosa facciamo'])}
</section>
<section class="wrap-t"><h2 class="sec-t">I nostri valori</h2>{valori()}</section>
<section class="wrap-t prose">
<h2 style="margin-top:0">Per scriverci o segnalare un errore</h2><p>C'è un solo indirizzo: <a href="{SEGNALA}">{MAIL}</a>. Correggiamo e indichiamo la data.</p>
<div class="row"><a class="btn" href="~/guide/">Leggi le guide</a><a class="btn btn-line" href="~/risorse/">Strumenti gratuiti</a></div>
{IGCARD}
</section>'''))

# ---------- il metodo ----------
latest = sorted(D['post'], key=lambda x: x['data'], reverse=True)[:3]
ultima = max(g['agg'] for g in GUIDE)
pages.append(page('/metodo/', 'Il metodo', 'Come nascono e si controllano le guide di Serena: fonti, intelligenza artificiale, controllo di una persona, date.', f'''
<section class="ph-hd wrap-t"><h1>Il metodo</h1><p class="lead">Come nasce una guida di Serena, chi controlla le fonti e ogni quanto.</p></section>
<section class="wrap-t prose">
<ol class="steps">{''.join(f'<li><b>{e(a)}</b><span>{e(b)}</span></li>' for a, b in PROCESSO)}</ol>
<section class="box box-salvia"><h2>A oggi</h2><ul class="plain"><li>{len(GUIDE)} guide, con {len({f for g in GUIDE for f in g['fonti']})} fonti da aprire.</li><li>Ultimo controllo delle fonti: {data_it(ultima)}.</li><li>Le fotografie sono generate con strumenti di intelligenza artificiale e scelte da una persona: non ritraggono luoghi, oggetti o persone reali.</li></ul></section>
<h2>Cosa Serena non fa</h2><ul class="ticks no">{''.join(f'<li>{ic("close","ic-s")}<span>{x}</span></li>' for x in NON_FA)}</ul>
<section class="box box-rosa"><h2>Hai trovato un errore?</h2><p>Scrivi a {MAIL}, anche solo due righe. Correggiamo e indichiamo la data.</p><a class="btn" href="{SEGNALA}" data-umami-event="segnala-errore">Segnala un errore</a></section>
<h2>Le fonti</h2><p>Ogni guida ha in fondo le sue fonti, da aprire. Anche ogni dato citato su Instagram ha la sua pagina. Le più recenti:</p>
<ul class="postl">{''.join(f'<li><a href="~/fonti/{p["slug"]}/"><span class="date">{data_it(p["data"])}</span><b>{e(p["titolo"])}</b></a></li>' for p in latest)}</ul>
<a class="more" href="~/fonti/">Tutte le fonti {ic('arrow','ic-s')}</a>
</section>'''))

# ---------- correzioni ----------
corr = sorted([(d, t, g) for g in GUIDE for d, t in g.get('storia', [])], key=lambda x: x[0], reverse=True)
pages.append(page('/correzioni/', 'Correzioni e aggiornamenti', 'Cosa è stato corretto o aggiornato nelle guide di Serena, con la data.', f'''
<section class="ph-hd wrap-t"><h1>Correzioni e aggiornamenti</h1><p class="lead">Quando una guida cambia, lo scriviamo qui: cosa, quando e perché. Le guide nuove non compaiono: hanno la loro data.</p></section>
<section class="wrap-t"><ul class="postl">{''.join(f'<li><a href="~/guide/{g["slug"]}/#come-e-fatta"><span class="date">{data_it(d)}</span><b>{e(g["titolo"])}</b><span>{e(t)}</span></a></li>' for d, t, g in corr)}</ul></section>
<section class="wrap-t prose"><section class="box box-rosa"><h2>Hai trovato un errore?</h2><p>Scrivi a {MAIL}, anche solo due righe. Correggiamo e lo scriviamo in questa pagina.</p><a class="btn" href="{SEGNALA}" data-umami-event="segnala-errore">Segnala un errore</a></section>
<div class="row"><a class="btn btn-line" href="~/metodo/">Come nasce una guida</a></div></section>'''))

# ---------- i tuoi salvati (tutto nel browser) ----------
pages.append(page('/salvati/', 'I tuoi salvati', 'Le pagine salvate, i promemoria creati e le liste cominciate: restano su questo telefono o computer.', f'''
<section class="ph-hd wrap-t"><h1>I tuoi salvati</h1><p class="lead">Serena tiene qui quello che hai messo da parte. Resta su questo telefono o computer: a noi non arriva.</p></section>
<section class="wrap-t tuoi" data-tuoi data-guide="{e(json.dumps({g['slug']: g['titolo'] for g in GUIDE}, ensure_ascii=False))}">
<section data-t-salvati hidden><h2 class="sec-t">Pagine salvate</h2><ul class="rows"></ul></section>
<section data-t-liste hidden><h2 class="sec-t">Liste cominciate</h2><ul class="rows"></ul></section>
<section data-t-strumenti hidden><h2 class="sec-t">Quello che hai scritto negli strumenti</h2><ul class="rows"></ul></section>
<section data-t-promemoria hidden><h2 class="sec-t">Promemoria creati</h2><ul class="rows"></ul><p class="small">Sono nel calendario del tuo telefono: qui Serena ricorda solo di averli preparati.</p></section>
<section data-t-inizio><h2 class="sec-t">Da dove cominciare</h2><ul class="rows">{riga('~/guide/', 'Le guide', 'In ogni guida c\'è «Salva per dopo»', icona='book')}{riga('~/risorse/', 'Gli strumenti gratuiti', 'Quello che scrivi resta qui', icona='tools')}</ul></section>
<p class="small"><button class="btn btn-line btn-sm" type="button" data-t-svuota hidden>Dimentica tutto quello che è in questa pagina</button></p>
</section>''', cls='p-tuoi'))
pages.append(page('/senza-rete/', 'Questa pagina non è salvata sul telefono', 'Pagina mostrata quando manca la rete.', f'''
<section class="ph-hd wrap-t"><h1>Questa pagina non è salvata sul telefono.</h1><p class="lead">Adesso manca la rete: la pagina si apre appena torna. Le pagine che avevi già aperto o salvato, invece, si leggono anche così.</p>
<div class="row"><a class="btn" href="~/salvati/">I tuoi salvati</a><a class="btn btn-line" href="~/">Pagina iniziale</a></div>
<p class="small">Se è urgente, chiama il 112.</p></section>'''))

# ---------- privacy ----------
# Data vera dell'ultima modifica dei testi (non la data di oggi: il sito si
# rigenera ogni mattina). Si cambia a mano quando cambia il testo.
# Testo della pagina approvato dal presidente il 7/11/2026 (verifica privacy del sito); righe sul sito 2035 approvate il 12/11/2026.
AGG_PRIVACY = '2026-11-12'
AGG_NOTE_LEGALI = '2026-10-21'
PRIVACY_BODY = '<h2>Chi è responsabile dei dati</h2><p>Questo sito lo cura Antonino Creazzo, persona fisica. È il titolare del trattamento dei pochi dati descritti in questa pagina.</p><p>Per qualsiasi domanda sulla privacy scrivi a <a href="mailto:privacy@serenainmente.it">privacy@serenainmente.it</a>.</p><h2>In breve</h2><p>Non ti chiediamo dati. Non ci sono iscrizioni, moduli o account.</p><p>Quello che scrivi negli strumenti del sito resta sul tuo telefono o computer. A noi non arriva.</p><p>Ci sono solo due cose che, come per quasi tutti i siti, partono dal tuo browser:</p><ul><li>la richiesta delle pagine, che passa dal servizio che ospita il sito;</li><li>un conteggio delle visite, senza cookie.</li></ul><h2>Quando apri una pagina</h2><p>Il sito è ospitato da GitHub (GitHub, Inc., Stati Uniti). Come ogni servizio di questo tipo, GitHub riceve l\'indirizzo di rete (IP) da cui arriva la richiesta, il tipo di browser e la pagina richiesta. Li conserva per motivi di sicurezza, secondo le sue regole.</p><p>Senza questi dati la pagina non può arrivare al tuo schermo. Il motivo è il nostro interesse legittimo a far funzionare il sito e a proteggerlo.</p><p>Noi non vediamo questi dati.</p><h2>Come contiamo le visite</h2><p>Per capire quali pagine sono utili usiamo Umami (Umami Software, Inc., Stati Uniti). Umami non usa cookie e non salva niente sul tuo dispositivo.</p><p>A ogni pagina Umami riceve:</p><ul><li>l\'indirizzo di rete, che usa solo al momento e non conserva nelle statistiche;</li><li>il tipo di browser e di dispositivo, la lingua e la dimensione dello schermo;</li><li>la pagina visitata e il sito da cui arrivi;</li><li>i tocchi su alcuni pulsanti, come «Scarica il PDF». Mai quello che scrivi.</li></ul><p>Dall\'indirizzo di rete Umami ricava il Paese e la città approssimativi, e un codice di visita che non dice chi sei.</p><p>Noi vediamo solo totali: quante persone leggono una pagina, da quale canale arrivano, quanti scaricano un file. Non sappiamo chi sei e non creiamo profili.</p><p>Il motivo è il nostro interesse legittimo a capire quali contenuti servono. Per questo non c\'è un banner e non ti chiediamo il consenso.</p><p>Se nel browser hai attivato «Non tracciare», Umami non conta la tua visita. Puoi anche bloccare il conteggio con un blocco contenuti del browser: il sito funziona lo stesso.</p><p>Umami conserva le statistiche per 6 mesi. Le archivia su server nell\'Unione europea. Alcuni servizi tecnici di Umami, come la rete che distribuisce i file e i registri di sicurezza, si trovano comunque negli Stati Uniti. Umami tratta questi dati per conto nostro, con un contratto che lo obbliga a proteggerli.</p><h2>Cosa resta sul tuo telefono o computer</h2><p>Alcune parti del sito ricordano quello che fai usando la memoria del tuo browser. Non sono cookie e non arrivano a noi:</p><ul><li>le <b>spunte delle checklist</b> nelle guide;</li><li>quello che scrivi in <b>Preparo la visita</b>.</li></ul><p>Servono solo a ritrovare le cose quando torni. Puoi cancellarle quando vuoi:</p><ul><li>con «Azzera le spunte» o «Ricomincia da capo»;</li><li>cancellando i dati del sito dalle impostazioni del browser.</li></ul><p>Se il telefono o il computer lo usano anche altre persone, alla fine tocca «Ricomincia da capo».</p><h2>I file che scarichi</h2><p>Il gestionale di famiglia, i fogli da stampare e le checklist in Excel sono file. Restano dove li salvi tu.</p><p>Se usi «Apri in Fogli Google», la copia è tua, nel tuo Drive, con le regole di Google. Quello che ci scrivi non arriva a noi.</p><h2>Quando ci scrivi</h2><p>Se ci scrivi a <a href="mailto:privacy@serenainmente.it">privacy@serenainmente.it</a> o con un messaggio su Instagram, riceviamo il tuo indirizzo o il tuo nome utente e quello che scrivi.</p><p>Li usiamo solo per risponderti. Li teniamo per 12 mesi dall\'ultimo messaggio, poi li cancelliamo.</p><p>L\'email passa da Google (Gmail). I messaggi su Instagram passano da Meta, ciascuno con le sue regole.</p><p>Per favore, non mandarci dati sulla salute tua o dei tuoi figli: non possiamo darti indicazioni mediche.</p><h2>Quando esci dal sito</h2><p>I link alle fonti, a Instagram, a WhatsApp e a Fogli Google ti portano su altri siti, con le loro regole. Noi non riceviamo niente di quello che fai lì.</p><p>Se mandi qualcosa con WhatsApp o con «Condividi», il testo lo mandi tu, con l\'app che scegli.</p><h2>Fuori dall\'Unione europea</h2><p>GitHub e Umami sono aziende degli Stati Uniti. I dati tecnici descritti sopra possono quindi essere trattati negli Stati Uniti.</p><p>Questo avviene con le garanzie previste dal GDPR: la decisione della Commissione europea sul Data Privacy Framework UE‑USA, per i fornitori che vi aderiscono, e le clausole contrattuali tipo approvate dalla Commissione.</p><h2>I tuoi diritti</h2><p>Puoi chiederci in ogni momento di sapere quali dati tuoi abbiamo, di correggerli o di cancellarli, e di limitarne l\'uso.</p><p>Puoi anche <b>opporti</b> all\'uso dei tuoi dati basato sul nostro interesse legittimo, per esempio al conteggio delle visite.</p><p>Scrivi a <a href="mailto:privacy@serenainmente.it">privacy@serenainmente.it</a>: ti rispondiamo entro un mese. Tieni conto che da un indirizzo di rete spesso non è possibile risalire a una persona, e che i dati delle statistiche non ci dicono chi sei.</p><p>Puoi anche presentare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" rel="noopener">garanteprivacy.it</a>).</p><h2>Bambini</h2><p>Il sito è pensato per adulti. Non chiediamo dati a nessuno, nemmeno sui bambini.</p><h2>Se questa pagina cambia</h2><p>Se cambiamo il modo in cui trattiamo i dati, aggiorniamo questa pagina e la data qui sotto.</p>'
# Righe aggiunte con il sito 2035 e approvate dal presidente il 12/11/2026: il sito ricorda in locale alcune cose in più.
PRIVACY_BODY = PRIVACY_BODY.replace('<li>quello che scrivi in <b>Preparo la visita</b>.</li>',
    '<li>quello che scrivi in <b>Preparo la visita</b> e in <b>Medicine di casa</b>;</li><li>le pagine che <b>salvi per dopo</b>;</li><li>di chi ti prendi cura, se lo indichi nella pagina iniziale;</li><li>l\'aspetto chiaro o scuro e la grandezza del testo che scegli;</li><li>una copia delle pagine che hai aperto o salvato, per rileggerle anche senza rete;</li><li>il titolo dei promemoria che hai creato, per ritrovarli in «I tuoi salvati».</li></ul><p>«Salva una copia» in Medicine di casa crea un file sul tuo telefono: lo tieni tu, a noi non arriva.</p><p>Anche le parole che scrivi nella ricerca restano sul tuo telefono o computer: la ricerca lavora lì, senza mandarle a nessuno.</p><ul hidden>')
PRIVACY_BODY = PRIVACY_BODY.replace('<ul hidden></ul>', '').replace('con «Azzera le spunte» o «Ricomincia da capo»;', 'con «Azzera le spunte», «Ricomincia da capo» o «Dimentica»;')
pages.append(page('/privacy/', 'Privacy', 'Come serenainmente.it tratta i dati: niente cookie, niente profilazione, statistiche solo aggregate.', f'''
<section class="ph-hd wrap-t"><h1>Privacy</h1><p class="lead">In breve: niente cookie, niente profilazione. Contiamo le visite solo in forma aggregata, e quello che scrivi negli strumenti resta sul tuo telefono.</p></section>
<section class="wrap-t prose">{PRIVACY_BODY}
<p class="small">Ultimo aggiornamento: {data_it(AGG_PRIVACY)}.</p></section>'''))

# ---------- strumenti interattivi ----------
# Domande pronte: una sola fonte, usata da «Preparo la visita» e dalla ricerca. Sono domande da fare al medico o cose da raccontare, mai risposte.
TEMI = [('Sonno', ['Quante ore di sonno sono normali alla sua età?', 'Si sveglia spesso di notte: cosa possiamo provare?', 'C\'è qualcosa nel suo sonno che conviene controllare?']),
        ('Mangiare', ['Mangia abbastanza per la sua età?', 'Come capisco se cresce bene con quello che mangia?', 'Ci sono cibi da aggiungere o da aspettare?']),
        ('Crescita', ['Peso e altezza vanno bene per la sua età?', 'Cosa è normale che sappia fare, a questa età?', 'Quando è il prossimo controllo?']),
        ('Febbre o malessere', ['Da raccontare: da quando è cominciato e come è cambiato', 'Da raccontare: come mangia, beve e dorme in questi giorni', 'Da raccontare: cosa abbiamo già fatto a casa', 'Quali segnali devo tenere d\'occhio, e quando richiamo?']),
        ('Specialista', ['Servono altri esami? Dove si prenotano?', 'Chi mi comunica il risultato, e quando?', 'Cosa devo riferire al pediatra o al medico di famiglia?']),
        ('Sport e scuola', ['Serve un certificato per lo sport che fa?', 'Ha già fatto un elettrocardiogramma?', 'C\'è qualcosa da sapere prima di cominciare?']),
        ('Persona anziana', ['Le medicine che prende vanno ancora tutte bene?', 'C\'è qualcosa da controllare a casa?', 'Chi chiamo se ho un dubbio?'])]
# quali argomenti vengono prima, per età (i numeri sono le posizioni in TEMI)
TEMI_ETA = {'0-1': [2, 1, 0], '1-3': [0, 1, 2], '3-6': [2, 0, 1], '6-12': [5, 2, 0], '13-18': [5, 2], 'anziano': [6, 4], '': [2, 0, 1]}
PRONTE = ('<details class="pv-pronte"><summary>Domande pronte</summary><p class="small" style="margin-top:10px">Scegli un argomento e tocca le domande che ti servono: finiscono nella tua lista.</p><div class="pv-temi" role="group" aria-label="Argomento delle domande">'
          + ''.join(f'<button type="button" class="fchip" data-tema-q="{k}" aria-pressed="{"true" if k == 0 else "false"}">{e(t)}</button>' for k, (t, _) in enumerate(TEMI)) + '</div>'
          + ''.join(f'<ul class="esempi" data-gruppo="{k}"{"" if k == 0 else " hidden"}>' + ''.join(f'<li><button type="button" data-pronta>{e(q)}</button></li>' for q in v) + '</ul>' for k, (t, v) in enumerate(TEMI)) + '</details>')
PV = open(os.path.join(ROOT, 'gen', 'preparo.html'), encoding='utf-8').read().replace('{lock}', ic('lock','ic-s')).replace('{arrow}', ic('arrow','ic-s')).replace('{back}', '←').replace('{salva}', salva('/strumenti/preparo-la-visita/', 'Preparo la visita')).replace('{pronte}', PRONTE)
pages.append(page('/strumenti/preparo-la-visita/', 'Preparo la visita', 'Strumento gratuito: scrivi cosa hai notato e le domande per il pediatra o il medico, e in ambulatorio le hai davanti. Resta solo sul tuo telefono.', PV, seo='Preparo la visita: le domande per il medico', cls='p-tool'))

MD = open(os.path.join(ROOT, 'gen', 'medicine.html'), encoding='utf-8').read().replace('{lock}', ic('lock','ic-s')).replace('{check}', ic('check','ic-s')).replace('{salva}', salva('/strumenti/medicine-di-casa/', 'Medicine di casa'))
pages.append(page('/strumenti/medicine-di-casa/', 'Medicine di casa', 'Strumento gratuito: la lista delle medicine di una persona, da stampare grande o mandare, con i promemoria degli orari. Resta solo sul tuo telefono.', MD, seo='Medicine di casa: la lista dei farmaci sul telefono', cls='p-tool'))

# ---------- da instagram (link in bio) ----------
IGL = sorted([x for x in D.get('instagram', []) if x['data'] <= OGGI], key=lambda x: (x['data'], x.get('tipo') != 'fonti'), reverse=True)
visti = set(); IGU = []
for x in IGL:  # ogni pagina una volta sola: vale il post più recente
    if x['link'] not in visti: visti.add(x['link']); IGU.append(x)
TIPO = {'strumento': 'Strumento gratuito', 'stampabile': 'Foglio da stampare', 'guida': 'Guida', 'fonti': 'Il dato del post, con la fonte'}
def ig_img(x, grande=False):
    n = x['data'] + ('' if grande else '-m')
    return f'/assets/ig/{n}.webp' if esiste('assets', 'ig', f'{n}.webp') else None
def ig_li(x):
    return riga(f"~{x['link']}", x['titolo'], f"{TIPO.get(x.get('tipo'), 'Dal post')} · post del {data_it(x['data'])}", ig_img(x), attr=f' data-umami-event="ig-link" data-umami-event-link="{e(x["link"])}"')
ig_primo = ''
if IGU:
    x = IGU[0]; im = ig_img(x, True)
    az = {'strumento': 'Apri lo strumento', 'stampabile': 'Guarda il foglio', 'guida': 'Leggi la guida', 'fonti': 'Leggi cosa dice, in breve'}.get(x.get('tipo'), 'Apri')
    post0 = next((q for q in D['post'] if x.get('tipo') == 'fonti' and x['link'].strip('/').endswith(q['slug'])), None)
    detto = f'<p>{e(post0["affermazioni"][0])}</p>' if post0 else ''
    if post0: az = 'Da dove viene questo dato'
    ig_primo = f'''<a class="ig-primo vetro cede" href="~{x['link']}" data-umami-event="ig-link" data-umami-event-link="{e(x['link'])}">{f'<img src="~{im}" alt="" width="720" height="450" decoding="async" fetchpriority="high">' if im else ''}<span class="b"><span class="chip">Dall'ultimo post · {data_it(x['data'])}</span><h2>{e(post0['titolo'] if post0 else x['titolo'])}</h2>{detto}<span class="btn">{az} {ic('arrow','ic-s')}</span></span></a>'''
ig_altri = [t for t in TOOLS if t[0] not in visti]
pages.append(page('/ig/', 'Da Instagram', 'Gli strumenti, i fogli e le guide dei post di @serenainmente, a portata di tocco.', f'''
<section class="wrap-t ig-page"><div class="ig-hd"><img src="~/assets/brand/avatar-160.png" alt="" width="56" height="56"><div><h1>Dai post di Serena</h1><p class="small">Tutto quello che hai visto su Instagram. Gratis, senza registrazione.</p></div></div>
{ig_primo}
{CHIEDI}
<section data-salvati hidden><h2 class="sec-t"></h2><ul class="rows"></ul></section>
{f'<section><h2 class="sec-t">Dai post precedenti</h2><ul class="rows">' + ''.join(ig_li(x) for x in IGU[1:8]) + '</ul></section>' if len(IGU) > 1 else ''}
{'<section><h2 class="sec-t">Sempre a portata di mano</h2><ul class="rows">' + ''.join(riga('~' + t[0], t[1], t[2], t[6], t[3]) for t in ig_altri) + '</ul></section>' if ig_altri else ''}
<div class="row"><a class="btn btn-line" href="~/guide/">Tutte le guide</a><a class="btn btn-line" href="~/chi-e-serena/">Chi è Serena</a></div></section>''', cls='p-ig'))

# ---------- note legali ----------
pages.append(page('/note-legali/', 'Note legali', 'Chi cura serenainmente.it, come si possono usare i contenuti, informazioni sanitarie, link esterni e immagini.', f'''
<section class="ph-hd wrap-t"><h1>Note legali</h1><p class="lead">Le regole del sito, in parole semplici.</p></section>
<section class="wrap-t prose">
<h2 style="margin-top:0">Chi cura il sito</h2><p>serenainmente.it e il profilo Instagram <a href="{IG}" rel="noopener">@serenainmente</a> sono un progetto editoriale indipendente, ideato e curato da una persona, con supporto AI per testi, immagini e verifica delle fonti. Non ci sono sponsor né pubblicità. Per qualsiasi comunicazione: <a href="mailto:{MAIL}">{MAIL}</a>.</p>
<h2>Uso dei contenuti</h2><p>Testi, grafiche, guide, checklist, fogli da stampare e il gestionale di famiglia sono di serenainmente.it. Puoi usarli gratuitamente per te e la tua famiglia, stamparli e condividerli con il link alla pagina originale. Non è consentito ripubblicarli, modificarli per distribuirli o usarli per scopi commerciali senza un consenso scritto: se ti servono per una scuola, un consultorio o un'associazione, scrivici e ne parliamo volentieri.</p>
<h2>Informazioni sanitarie</h2><p>I contenuti sono informazioni generali tratte da fonti indicate pagina per pagina. Non sono diagnosi né indicazioni per una persona specifica e non sostituiscono il parere del pediatra, del medico o di altri professionisti. In caso di urgenza chiama il 112.</p>
<h2>Link e fonti esterne</h2><p>Le fonti citate rimandano a siti di enti e istituzioni che non gestiamo. Controlliamo i collegamenti alla data indicata in ogni pagina, ma i loro contenuti possono cambiare: in quel caso aggiorniamo la pagina appena ce ne accorgiamo.</p>
<h2>Immagini</h2><p>Le fotografie del sito e le grafiche sono generate o composte con strumenti digitali e AI e scelte da una persona: non ritraggono persone, luoghi o oggetti reali.</p>
<h2>Marchi di terzi</h2><p>Microsoft Excel, Fogli Google, Numbers, Instagram e WhatsApp sono marchi dei rispettivi titolari: li citiamo solo per spiegare come usare gli strumenti.</p>
<h2>Errori e segnalazioni</h2><p>Se trovi un errore, un dato superato o un link che non funziona, scrivici: correggiamo e indichiamo la data dell'aggiornamento. Come trattiamo i dati è spiegato nella pagina <a href="~/privacy/">Privacy</a>.</p>
<p class="small">Ultimo aggiornamento: {data_it(AGG_NOTE_LEGALI)}.</p></section>'''))

# ---------- fonti ----------
post_cards = []
for p in sorted(D['post'], key=lambda x: x['data'], reverse=True):
    claims = ''.join(f'<li>{e(c)}</li>' for c in p['affermazioni'])
    if 'OR-02' in p['fonti'] and 'OR-28' not in p['fonti']: p['fonti'].insert(p['fonti'].index('OR-02') + 1, 'OR-28')
    fonti = ''.join(src_block(fid) for fid in p['fonti'])
    guida = GN.get(p.get('guida'))
    gl = f'<a class="btn" href="~/guide/{guida["slug"]}/">Leggi la guida</a>' if guida else ''
    pages.append(page(f"/fonti/{p['slug']}/", f"Fonti: {p['titolo']}", f"Le fonti del post «{p['titolo']}» di @serenainmente.", f'''
<section class="wrap-t prose fpage"><nav class="crumbs" aria-label="Percorso"><a href="~/fonti/">‹ Le fonti</a></nav><span class="chip" style="align-self:flex-start">Fonti del post · {data_it(p['data'])}</span><h1>{e(p['titolo'])}</h1>
<h2>Cosa dice il post, in breve</h2><ul class="plain">{claims}</ul>
<h2>Da dove viene</h2><p class="small">Qui sopra c'è il dato in italiano. Sotto trovi il documento originale: alcuni sono in inglese.</p><ul class="sources">{fonti}</ul>
<p class="small">Collegamenti controllati il {data_it(p['controllo'])}. Informazioni generali, non sostituiscono il parere del pediatra o del medico.</p>
<div class="row">{gl}<a class="btn btn-line" href="{IG}" rel="noopener" data-umami-event="instagram">Vai al profilo Instagram</a></div></section>'''))
    post_cards.append(f'<li><a href="~/fonti/{p["slug"]}/"><span class="date">{data_it(p["data"])} · {len(p["fonti"])} {"fonte" if len(p["fonti"]) == 1 else "fonti"}</span><b>{e(p["titolo"])}</b></a></li>')
guide_fonti = ''.join(f'<li><a href="~/guide/{g["slug"]}/#fonti"><span class="date">Controllate il {data_it(g["agg"])} · {len(g["fonti"])} {"fonte" if len(g["fonti"]) == 1 else "fonti"}</span><b>{e(g["titolo"])}</b></a></li>' for g in GUIDE if g['fonti'])
enti = sorted({FONTI[f]['ente'] for g in GUIDE for f in g['fonti']} | {FONTI[f]['ente'] for p in D['post'] for f in p['fonti']})
pages.append(page('/fonti/', 'Le fonti di Serena', 'Le fonti dei dati citati nelle guide e nei post di @serenainmente, con i link alle pagine originali.', f'''
<section class="ph-hd wrap-t"><h1>Le fonti</h1><p class="lead">Ogni dato di Serena viene da un ente o da un'istituzione che puoi aprire e leggere. Qui le trovi tutte, guida per guida e post per post.</p></section>
<section class="wrap-t"><h2 class="sec-t">Le fonti delle guide</h2><ul class="postl">{guide_fonti}</ul></section>
<section class="wrap-t"><h2 class="sec-t">Le fonti dei post di Instagram</h2><ul class="postl">{''.join(post_cards)}</ul></section>
<section class="wrap-t"><details class="piega"><summary>Gli enti citati ({len(enti)})</summary><p>{e(' · '.join(enti))}</p></details></section>'''))

# ---------- le frasi di Serena ----------
def frase_li(f):
    txt = (f"{f['parola']}: " if f.get('parola') else '') + f['testo']
    msg = txt + ' — da @serenainmente'
    wa = 'https://wa.me/?text=' + e(urllib.parse.quote(msg))
    head = f'<span class="chip">Il vocabolario di Serena · n. {f["numero"]}</span><b class="parola">{e(f["parola"])}</b>' if f.get('parola') else ''
    return f'''<li class="fr">{head}<p>{e(f['testo'])}</p><div class="row"><button class="btn btn-sm" type="button" hidden data-sharetext="{e(msg)}" data-umami-event="frase-condividi">Manda</button><a class="btn btn-sm btn-line" href="{wa}" rel="noopener" data-umami-event="frase-whatsapp">WhatsApp</a><button class="btn btn-sm btn-line" type="button" data-copytext="{e(msg)}" data-done="Copiata" data-umami-event="frase-copia">Copia</button></div><span class="small">{data_it(f['data'])}</span></li>'''
if FRASI_ON:
    pages.append(page('/frasi/', 'Le frasi di Serena', 'Frasi brevi da mandare a chi si prende cura della famiglia, e le parole del vocabolario di Serena.', f'''
<section class="ph-hd wrap-t"><h1>Le frasi di Serena</h1><p class="lead">Parole brevi da mandare a chi ne ha bisogno oggi. Ogni settimana se ne aggiunge una.</p></section>
<section class="wrap-t"><ul class="frasi">{''.join(frase_li(f) for f in FRASI)}</ul>{IGCARD}</section>'''))
if FRASI_ON:
    f0 = next(f for f in FRASI if not f.get('parola')); m0 = f0['testo'] + ' — da @serenainmente'
    frase_home = (f'<section class="wrap-t"><div class="frase vetro"><span class="eyebrow">La frase della settimana</span><p>{e(f0["testo"])}</p>'
                  f'<div class="row" style="justify-content:center"><button class="btn btn-sm" type="button" hidden data-sharetext="{e(m0)}" data-umami-event="frase-condividi">Mandala a qualcuno</button><a class="more" href="~/frasi/">Tutte le frasi {ic("arrow","ic-s")}</a></div></div></section>')
else: frase_home = ''

# ---------- pagina iniziale ----------
SALUTO = {'mattino': 'Buongiorno', 'giorno': 'Buon pomeriggio', 'sera': 'Buonasera', 'notte': 'È tardi, lo sappiamo'}
INVITO = {'mattino': 'Una cosa alla volta. Cerca quella di oggi: la risposta è nelle guide di Serena.',
          'giorno': 'Una visita, un documento, una scadenza? Cerca qui: la risposta è nelle guide di Serena.',
          'sera': 'Stasera basta una cosa. Cercala qui: la risposta è nelle guide di Serena.',
          'notte': 'Basta una cosa. Cercala qui, tra le guide di Serena. Il resto può aspettare domani.'}
ORA = {'mattino': ('/strumenti/preparo-la-visita/', 'list', 'Una visita tra pochi giorni?', 'Prepara le domande in cinque minuti, dal telefono.'),
       'giorno': ('/guide/spostare-disdire-pagare-visita/', 'calendar', 'Una visita da spostare o da disdire?', 'Come si fa, e entro quando. Si legge in 2 minuti.'),
       'sera': ('/guide/routine-della-nanna/', 'moon', 'La sera che non finisce mai', 'Una routine della nanna in quattro mosse. Si legge in 2 minuti.'),
       'notte': ('/guide/quanto-dorme-un-bambino/', 'moon', 'Quanto deve dormire, alla sua età?', 'Le ore età per età, con le fonti. Sono intervalli larghi.')}
ora_cards = ''.join(f'<a class="ora-card vetro cede" data-per="{k}" href="~{h}" data-umami-event="home-ora" data-umami-event-ora="{k}"><span class="tic">{ic(i)}</span><span><b>{e(t)}</b><small>{e(s)}</small></span>{ic("arrow","ic-s")}</a>' for k, (h, i, t, s) in ORA.items())
# «da dove partire»: tutte le guide e gli strumenti, il sito mostra i primi 4 adatti a chi legge
def tag_li(chi, eta, base): return f' data-tag="{chi}" data-fasce="{" ".join(eta)}" data-base="{base}"'
partenze = [riga_guida(g, li=tag_li(*per(g['slug']), 1 if i < 4 else 0) + (' data-pri="1"' if g['arg'] == 'crescita' or per(g['slug'])[0] == 'anziano' else '')) for i, g in enumerate(GUIDE)]
partenze += [riga('~' + t[0], t[1], t[7] + ' · gratis', t[6], t[3], li=tag_li(t[5], [] if t[5] == 'anziano' else TUTTE_ETA, 0) + (' data-pri="1"' if t[5] == 'anziano' else '')) for t in TOOLS]
ordine = partenze
pages.append(page('/', 'Serena', 'Parole e idee per chi si prende cura della famiglia: guide pratiche, dati con le loro fonti, strumenti gratuiti.', f'''
<section class="hero wrap">
<div class="hero-txt"><p class="eyebrow">{''.join(f'<span data-per="{k}">{v}</span>' for k, v in SALUTO.items())}</p>
<h1>Hai già abbastanza da tenere a mente.</h1>
<p class="lead">{''.join(f'<span data-per="{k}">{e(v)}</span>' for k, v in INVITO.items())}</p>
{CHIEDI}
<div class="per-voi" data-per-voi hidden></div>
<ul class="esempi" aria-label="Esempi" data-esempi>{''.join(f'<li><a href="~/guide/?q={urllib.parse.quote(x)}" data-cerca="{e(x)}" role="button">{e(x)}</a></li>' for x in ESEMPI[:3])}</ul>
{ora_cards}
<p class="small">Guide brevi con le loro fonti, fogli da stampare e strumenti gratuiti. Senza registrazione e senza pubblicità.</p></div>
{foto('hero', '', 'hero-img')}
</section>
<section class="wrap blocco-s" data-salvati hidden><h2 class="sec-t"></h2><ul class="rows"></ul><a class="more" href="~/salvati/">I tuoi salvati {ic('arrow','ic-s')}</a></section>
<section class="wrap blocco-s">
<div class="per-te" hidden><h2>Di chi ti prendi cura?</h2><p class="lead-s">Scegli anche più di una persona: Serena mette in cima quello che vi serve, qui e nella ricerca.</p>
<ul class="esempi"><li><button type="button" data-cura="bambino" aria-pressed="false">Di un bambino</button></li><li><button type="button" data-cura="anziano" aria-pressed="false">Di una persona anziana</button></li></ul>
<div data-eta-box hidden><p class="lead-s" style="margin-top:14px">Quanti anni hanno i bambini? Puoi sceglierne più di una.</p><ul class="esempi">{''.join(f'<li><button type="button" data-eta="{k}" aria-pressed="false">{v}</button></li>' for k, v in [('0-1', 'Meno di 1 anno'), ('1-3', '1-3 anni'), ('3-6', '3-6 anni'), ('6-12', '6-12 anni'), ('13-18', '13-18 anni')])}</ul></div>
<p class="small" style="margin:12px 0 4px">Lo ricorda solo questo telefono o computer. <button class="btn btn-line btn-sm" type="button" data-dimentica hidden>Dimentica</button></p></div>
<div data-partenze-casa><h3 class="sec-t" data-partenze-t style="margin-top:18px">Le ultime guide</h3>
<ul class="rows" data-partenze>{''.join(ordine)}</ul>
</div><a class="more" href="~/guide/">Tutte le guide {ic('arrow','ic-s')}</a>
</section>
<section class="wrap"><div class="sec-hd"><h2>Strumenti gratuiti</h2><a class="more" href="~/risorse/">Tutti {ic('arrow','ic-s')}</a></div>{tools_fila()}</section>
{frase_home}
<section class="wrap"><div class="chi-band"><div style="display:flex;flex-direction:column;gap:14px;align-items:flex-start"><h2>Chi è Serena</h2><p>Serena è il nome di un progetto per chi si prende cura della famiglia. Lo cura una persona, con il supporto dell'intelligenza artificiale: ogni dato ha la sua fonte, ogni pagina è letta prima di uscire.</p><a class="btn btn-line" href="~/chi-e-serena/">Chi c'è dietro e come lavora {ic('arrow','ic-s')}</a></div>
<div style="display:flex;flex-direction:column;gap:20px">{valori()}{IGCARD}</div></div></section>
''', cls='p-home'))

# ---------- pagina non trovata ----------
pages_404 = page('/404/', 'Questa pagina non c\'è', 'Pagina non trovata.', f'''
<section class="ph-hd wrap-t"><h1>Questa pagina non c'è.</h1><p class="lead">Forse l'indirizzo è cambiato. Cerca qui quello che ti serviva.</p>{CHIEDI}
<div class="row"><a class="btn btn-line" href="~/">Vai alla pagina iniziale</a><a class="btn btn-line" href="~/guide/">Tutte le guide</a></div></section>''')

# ---------- indice della ricerca (resta nel browser: assets/cerca-dati.js) ----------
def voce(u, t, d, k, a, b='', **altro):
    return dict(u=u, t=t, d=d, k=k, a=a, b=b, **altro)
IDX = []
PIU_CERCATE = ['routine-della-nanna', 'risvegli-notturni', 'domande-per-il-pediatra', 'spostare-disdire-pagare-visita', 'lista-medicine-genitore-anziano']
for g in GUIDE:
    v = voce(f"/guide/{g['slug']}/", g['titolo'], g['sommario'], 'Guida',
             ' '.join([g['titolo'], g.get('titolo_seo', ''), g.get('domanda', ''), CHIAVI.get(g['slug'], '')]),
             ' '.join([g['sommario'], ARGN[g['arg']][1]] + [x for x, y in g['passi']] + g.get('checklist', [])),
             m=g['min'], ps=g['passi'], ag=data_it(g['agg']), c2=' '.join(g['perche'] + g.get('errori', []) + [y for x, y in g['passi']]), az='Tutti i passi', c=per(g['slug'])[0], fa=per(g['slug'])[1])
    if g['slug'] in DATI: v['g'] = 'dati'
    if mini(g['slug']): v['i'] = mini(g['slug'])
    if g['slug'] in PIU_CERCATE: v['top'] = 1
    if g['slug'] == 'domande-per-il-pediatra': v['dq'] = 1
    t = g.get('tabella')
    if per_eta(t):
        v['eta'] = dict(c=t['colonne'], r=[list(eta_mesi(r[0])) + r for r in t['righe']])
    IDX.append(v)
IDX.append(voce('/strumenti/preparo-la-visita/', 'Preparo la visita', 'Scrivi a casa cosa hai notato e le domande in ordine; in ambulatorio le hai davanti, con lo spazio per le risposte.', 'Strumento gratuito',
                'preparo la visita domande pediatra medico dottore ambulatorio domani appuntamento', 'strumento telefono appuntare risposte specialista chiedo chiedere', az='Apri lo strumento', c='bambino anziano', fa=TUTTE_ETA, dq=1))
IDX.append(voce('/strumenti/medicine-di-casa/', 'Medicine di casa', 'La lista delle medicine di una persona: la stampi grande, la mandi a un familiare o al medico, e il telefono ti ricorda gli orari.', 'Strumento gratuito',
                'medicine di casa lista medicine farmaci pastiglie pillole compresse terapia promemoria orari ricordare', 'anziano anziana nonna nonno mamma papà badante stampare grande', az='Apri lo strumento', c='anziano', fa=[]))
IDX.append(voce('/gestionale/', 'Il gestionale di famiglia', 'Visite, scadenze e documenti in un file solo, gratuito.', 'File gratuito',
                'gestionale di famiglia organizzare settimana scadenze calendario agenda promemoria excel fogli google', 'visite documenti impegni file scaricare', az='Scopri il gestionale', i=mini('gestionale')))
for f, t, d in STAMPABILI:
    IDX.append(voce(f'/stampabili/{f}/', t, d + '.', 'Foglio da stampare', t + ' stampare foglio pdf planner ' + {'settimana-sul-frigo': 'settimana organizzare frigo', 'domande-per-il-pediatra': 'pediatra visita domande', 'lista-delle-medicine': 'medicine farmaci pastiglie anziano nonna nonno mamma papà terapia'}[f],
                    d + ' ' + ' '.join(SP_INFO[f]['contiene']), az='Guarda il foglio', i=mini('foglio-' + f), c=ST_PER[f], fa=[] if ST_PER[f] == 'anziano' else TUTTE_ETA))
IDX.append(voce('/chi-e-serena/', 'Chi è Serena', D['chi']['sommario'], 'Pagina', 'chi è serena siamo siete dietro autore progetto persona', 'trasparenza indipendenza valori'))
IDX.append(voce('/metodo/', 'Il metodo', 'Come nasce un contenuto di Serena, da dove vengono i dati e chi decide cosa pubblicare.', 'Pagina', 'metodo come lavoriamo intelligenza artificiale ai affidabile fidarsi', 'fonti controllo revisione'))
IDX.append(voce('/fonti/', 'Le fonti', 'Le fonti dei dati citati nelle guide e nei post, con i link alle pagine originali.', 'Pagina', 'fonti fonte studi dati oms istituto superiore di sanità', ''))
IDX.append(voce('/privacy/', 'Privacy', 'Niente cookie, niente profilazione: cosa succede ai dati quando usi il sito.', 'Pagina', 'privacy cookie dati personali tracciamento', ''))
if FRASI_ON: IDX.append(voce('/frasi/', 'Le frasi di Serena', 'Parole brevi da mandare a chi ne ha bisogno oggi.', 'Pagina', 'frasi frase parole mandare vocabolario', ''))
for p in D['post']:
    IDX.append(voce(f"/fonti/{p['slug']}/", p['titolo'], p['affermazioni'][0][:180], 'Le fonti di un post', p['titolo'] + ' post instagram', '', az='Apri le fonti'))
idx_js = 'window.SERENA_INDICE=' + json.dumps(IDX, ensure_ascii=False, separators=(',', ':')) + ';window.SERENA_DOMANDE=' + json.dumps({'t': TEMI, 'e': TEMI_ETA}, ensure_ascii=False, separators=(',', ':')) + ';'
open(os.path.join(OUT, 'assets', 'cerca-dati.js'), 'w', encoding='utf-8').write(idx_js)
idx_v = hashlib.md5(idx_js.encode('utf-8')).hexdigest()[:8]
for f in SCRITTI:
    t = open(f, encoding='utf-8').read()
    open(f, 'w', encoding='utf-8').write(t.replace('@@INDICE@@', idx_v))

# ---------- sitemap, robots, file ----------
fd = os.path.join(OUT, 'fonti')  # toglie le pagine fonti di post non ancora usciti
if os.path.isdir(fd):
    vivi = {x['slug'] for x in D['post']}
    for n in os.listdir(fd):
        if os.path.isdir(os.path.join(fd, n)) and n not in vivi: shutil.rmtree(os.path.join(fd, n))
if not PREVIEW:
    today = datetime.date.today().isoformat()
    sm = ''.join(f'<url><loc>{SITE}{p}</loc><lastmod>{today}</lastmod></url>' for p in pages if p not in ('/privacy/', '/salvati/', '/senza-rete/'))  # la pagina Privacy (col nome del titolare) resta fuori dai motori di ricerca
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
else:
    for d in ['assets/fonts', 'assets/brand', 'assets/gestionale', 'assets/foto', 'assets/mini', 'assets/ig', 'assets/stampabili', 'scarica']:
        s = os.path.join(ROOT, d)
        if os.path.isdir(s): shutil.copytree(s, os.path.join(OUT, d), dirs_exist_ok=True)
    for f in ['stile3.css', 'sito.js']: shutil.copy(os.path.join(ROOT, 'assets', f), os.path.join(OUT, 'assets', f))
    for g in D['guide']:
        s = os.path.join(ROOT, 'guide', g['slug'], 'checklist.xlsx')
        if os.path.exists(s): shutil.copy(s, os.path.join(OUT, 'guide', g['slug'], 'checklist.xlsx'))
print('\n'.join(pages))
