# serenainmente.it — «Domande rapide» (/domande/) e «Il vocabolario di Serena» (/vocabolario/).
# Non è uno script a sé: build.py lo esegue dentro di sé (exec), dopo le schede «Da sapere», e usa le sue funzioni
# (page, riga, ic, e, fonte_ds, data_ds, share, salva…). Così build.py cambia solo in pochi punti, segnati «domande».
# I testi delle domande stanno in gen/domande.json (fatti controllati, con le fonti); qui non si scrivono testi nuovi.
# Il vocabolario si legge dai file dei post di Instagram (gen/grafiche/post) e compare solo dal giorno in cui la parola è uscita.
import glob, unicodedata

P['domanda'] = '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.2a2.5 2.5 0 1 1 3.6 2.3c-.8.4-1.2 1-1.2 1.8v.4"/><path d="M12 16.8h.01"/>'

_DQJ = json.load(open(os.path.join(ROOT, 'gen', 'domande.json'), encoding='utf-8'))
DQ = _DQJ['domande']
DQ_GRUPPI = _DQJ['gruppi']
DQ_CONTROLLO, DQ_REVISIONE = _DQJ['controllo'], _DQJ['revisione']
DQN = {q['slug']: q for q in DQ}
# voce del menu del telefono (al computer il menu resta com'è: sei voci bastano)
MENU_M = [('/domande/', 'Domande rapide')] if DQ else []
DQ_CSS = open(os.path.join(ROOT, 'assets', 'stile-domande.css'), encoding='utf-8').read()
DQ_CSS = '<style>' + re.sub(r'\s*([{};,])\s*', r'\1', re.sub(r'/\*.*?\*/', '', DQ_CSS, flags=re.S)).replace(';}', '}').strip() + '</style>'

def dq_arg(q):
    """l'argomento della domanda è quello della guida o della scheda a cui rimanda (serve alla ricerca per «Può servirti anche»)"""
    for x in q.get('guide', []):
        if x in GN: return GN[x]['arg']
    for x in q.get('schede', []):
        if x in DSN: return DSN[x]['argomento']
    return 'organizzazione'
def riga_dq(q, li=''):
    return riga(f"~/domande/{q['slug']}/", q['domanda'], q['risposta'], icona='domanda', li=li)
def dq_di(slug):
    return [q for q in DQ if slug in q.get('guide', []) or slug in q.get('schede', [])]
def dq_rim(slug):
    """«Domande rapide su questo», in fondo alle guide e alle schede collegate"""
    L = dq_di(slug)
    if not L: return ''
    return ('<section class="ds-rim dq-rim noprint" aria-labelledby="dq-rim-t"><h2 id="dq-rim-t">Domande rapide su questo</h2><ul class="rows">'
            + ''.join(riga_dq(q) for q in L) + '</ul></section>')
def dq_home(blocco):
    """sotto «Da sapere», in pagina iniziale: un accesso discreto"""
    if not DQ or not blocco.endswith('</section>'): return blocco
    return blocco[:-len('</section>')] + f'<p class="dq-home"><a class="more" style="white-space:normal" href="~/domande/">Domande rapide: {len(DQ)} risposte in una riga {ic("arrow","ic-s")}</a></p></section>'

def _rif(q, f):
    if not f: return ''
    return ' <span class="rif">' + ''.join(f'<a class="rif-n" href="#fonte-{i + 1}" aria-label="Fonte {i + 1}: {e(q["fonti"][i]["ente"])}">{i + 1}</a>' for i in f) + '</span>'
def _gruppo_t(k): return dict(DQ_GRUPPI).get(k, '')

def domande_pagine():
    if not DQ: return
    for q in DQ:
        dp = f"/domande/{q['slug']}/"
        righe = ''.join(f'<p>{e(r["t"])}{_rif(q, r["f"])}</p>' for r in q['righe'])
        nf = len(q['fonti'])
        fonti = ''.join(fonte_ds(i, f) for i, f in enumerate(q['fonti']))
        gc = [GN[x] for x in q.get('guide', []) if x in GN]
        sc = [DSN[x] for x in q.get('schede', []) if x in DSN]
        altre = [x for x in DQ if x is not q and x['gruppo'] == q['gruppo']][:4]
        medico = f'<p class="ds-medico">{e(DS_MEDICO)}</p>' if q.get('medico') and DS_MEDICO else ''
        segnala = 'mailto:' + MAIL + '?subject=' + urllib.parse.quote('Segnalazione: ' + q['domanda'])
        body = f'''<article class="art ds dq">
<header class="art-hd wrap-t">
<nav class="crumbs" aria-label="Percorso"><span class="corta"><a href="~/domande/">{ic('chev','ic-s ind')}Domande rapide</a></span><span class="lunga"><a href="~/">Inizio</a>{ic('chev','ic-s')}<a href="~/domande/">Domande rapide</a>{ic('chev','ic-s')}<a href="~/domande/#{q['gruppo']}">{e(_gruppo_t(q['gruppo']))}</a></span></nav>
<p class="ds-occh">Domanda rapida</p>
<h1>{e(q['domanda'])}</h1>
</header>
<div class="wrap-t ds-corpo">
<section class="ds-testo vetro" aria-label="La risposta"><p class="dq-risp">{e(q['risposta'])}</p>{righe}</section>
<section class="dq-piu" aria-labelledby="dq-piu-t"><h2 id="dq-piu-t">Per saperne di più</h2><ul class="rows">{''.join(riga_guida(x) for x in gc)}{''.join(riga_scheda(x) for x in sc)}</ul></section>
<section class="ds-fonti" id="fonti" aria-labelledby="fonti-t"><h2 id="fonti-t">{'La fonte' if nf == 1 else 'Le fonti'}</h2><ol class="sources">{fonti}</ol></section>
<p class="small ds-date">Controllata il {data_ds(DQ_CONTROLLO)} · prossima revisione {data_ds(DQ_REVISIONE)}</p>
{medico}
<p class="small fatta-r noprint"><a href="{segnala}" data-umami-event="segnala-errore">Segnala un errore</a></p>
<div class="azioni noprint">{salva(dp, q['domanda'])}</div>
{share(dp, q['domanda'], 'Ti è utile? Mandala a chi ne ha bisogno.')}
</div>
<section class="related wrap-t noprint"><div class="sec-hd"><h2>Altre domande rapide</h2><a class="more" href="~/domande/">Tutte le domande {ic('arrow','ic-s')}</a></div>
<ul class="rows">{''.join(riga_dq(x) for x in altre)}</ul></section>
</article>'''
        url = SITE + dp
        risposta = ' '.join([q['risposta']] + [r['t'] for r in q['righe']])
        faq = {"@type": "FAQPage", "mainEntityOfPage": url, "inLanguage": "it", "dateModified": DQ_CONTROLLO,
               "mainEntity": [{"@type": "Question", "name": q['domanda'], "acceptedAnswer": {"@type": "Answer", "text": risposta, "url": url}}],
               "citation": [{"@type": "CreativeWork", "name": f['pagina'], "url": f['url'], "publisher": f['ente']} for f in q['fonti']],
               "publisher": {"@type": "Organization", "name": "Serena", "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/assets/brand/avatar-320.png"}}}
        crumbs = {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Domande rapide", "item": SITE + "/domande/"},
                  {"@type": "ListItem", "position": 2, "name": q['domanda'], "item": url}]}
        pages.append(page(dp, q['domanda'], q['risposta'][:155], body, {"@context": "https://schema.org", "@graph": [faq, crumbs]}, cls='p-ds p-dq', pre=DQ_CSS))
    gruppi = ''.join(f'<section class="wrap-t dq-gruppo" id="{k}" aria-labelledby="dq-{k}"><h2 class="sec-t" id="dq-{k}">{e(t)}</h2><ul class="rows">'
                     + ''.join(riga_dq(q) for q in DQ if q['gruppo'] == k) + '</ul></section>' for k, t in DQ_GRUPPI if any(q['gruppo'] == k for q in DQ))
    salti = ''.join(f'<li><a class="fchip" href="#{k}">{e(t)}</a></li>' for k, t in DQ_GRUPPI if any(q['gruppo'] == k for q in DQ))
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Domande rapide", "url": SITE + "/domande/", "inLanguage": "it",
          "hasPart": [{"@type": "WebPage", "name": q['domanda'], "url": f"{SITE}/domande/{q['slug']}/"} for q in DQ]}
    pages.append(page('/domande/', 'Domande rapide', 'Le domande di tutti i giorni su documenti, medico, scuola e spese, con la risposta in una riga e le fonti ufficiali.', f'''
<section class="ph-hd wrap-t"><h1>Domande <em>rapide</em></h1><p class="lead">La risposta in una riga, poi due parole di contesto e le fonti ufficiali. Per le cose che si cercano di corsa.</p>
<ul class="dq-salti" aria-label="Vai a un argomento">{salti}</ul></section>
{gruppi}
<section class="wrap-t dq-fondo"><p class="small">Ogni risposta è controllata sulle fonti ufficiali, con la data. Quando una regola cambia da Regione a Regione, la risposta lo dice. Informazioni generali: per la tua situazione vale quello che dicono il medico, il Comune o l'ente indicato.</p>
<div class="row"><a class="btn btn-line" href="~/da-sapere/">Le schede «Da sapere»</a><a class="btn btn-line" href="~/guide/">Tutte le guide</a></div></section>''', ld, cls='p-list p-dq-i', pre=DQ_CSS))
    vocabolario_pagina()

def dq_indice():
    """le domande nella ricerca del sito: risultati di tipo «Domanda» (assets/sito.js le conta a parte, come le schede)"""
    out = []
    for q in DQ:
        v = voce(f"/domande/{q['slug']}/", q['domanda'], q['risposta'], 'Domanda', ' '.join([q['domanda'], q.get('chiavi', '')]), q['risposta'],
                 c2=' '.join(r['t'] for r in q['righe']), az='Leggi la risposta', ar=dq_arg(q), c=q.get('c', 'bambino'), fa=q.get('fa', TUTTE_ETA),
                 gd=[f'/guide/{x}/' for x in q.get('guide', [])] + [f'/da-sapere/{x}/' for x in q.get('schede', [])])
        out.append(v)
    return out

# ---------- il vocabolario di Serena ----------
def _slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')
def _riga_una(f): return ' '.join(x.strip() for x in f.split('\n') if x.strip())
def vocabolario():
    """Le parole già uscite su Instagram (data passata, o di oggi se la build gira dalle 18 ora di Roma), dalla più recente.
    1) gen/grafiche/post/vocabolario-*.json: le voci con la loro data (fanno fede);
    2) gen/grafiche/post/*vocabolario*.json (i caroselli): la data è quella del nome del file;
    3) gli altri post del giorno (AAAA-MM-GG*.json) con «parola» e «numero»: solo per numeri e parole che mancano (es. la n. 1)."""
    cart = os.path.join(ROOT, 'gen', 'grafiche', 'post')
    V, parole = {}, set()
    # La parola esce su Instagram alle 18 (ora di Roma): compare solo se la data è passata,
    # oppure se è oggi e la build gira dalle 18:00 in poi.
    from zoneinfo import ZoneInfo
    ora = datetime.datetime.now(ZoneInfo('Europe/Rome')); oggi_roma = ora.date().isoformat()
    def uscita(data): return data < oggi_roma or (data == oggi_roma and ora.hour >= 18)
    def metti(n, parola, frase, data, fonte):
        if not (parola and frase and n) or not uscita(data): return
        n = int(n)
        if n in V or parola.lower() in parole: return
        V[n] = dict(numero=n, parola=parola.strip(), frase=_riga_una(frase), data=data, fonte=fonte); parole.add(parola.lower())
    for f in sorted(glob.glob(os.path.join(cart, 'vocabolario-*.json'))):
        for v in json.load(open(f, encoding='utf-8')).get('voci', []):
            metti(v.get('numero'), v.get('parola'), v.get('frase'), v.get('data', '9999'), os.path.basename(f))
    altri = [f for f in sorted(glob.glob(os.path.join(cart, '*.json'))) if re.match(r'\d{4}-\d{2}-\d{2}', os.path.basename(f))]
    for f in sorted(altri, key=lambda f: ('vocabolario' not in os.path.basename(f), os.path.basename(f))):
        try: L = json.load(open(f, encoding='utf-8'))
        except Exception: continue
        if not isinstance(L, list): continue
        data = os.path.basename(f)[:10]
        for v in L:
            if isinstance(v, dict) and v.get('tipo') == 'frase' and v.get('parola') and v.get('numero'):
                metti(v['numero'], v['parola'], v.get('frase'), data, os.path.basename(f))
    return sorted(V.values(), key=lambda v: v['numero'], reverse=True)

def vocabolario_pagina():
    VOC = vocabolario()
    if not VOC: return
    voci = ''.join(f'''<li class="voc-v{' voc-ultima' if i == 0 else ''}" id="{_slug(v['parola'])}"><p class="voc-n">{'L’ultima parola · ' if i == 0 else ''}n. {v['numero']}</p>
<h2 class="voc-p">{e(v['parola'])}</h2><p class="voc-d">{e(v['frase'])}</p></li>''' for i, v in enumerate(VOC))
    indice = ''.join(f'<li><a href="#{_slug(v["parola"])}">{e(v["parola"])}</a></li>' for v in sorted(VOC, key=lambda v: _slug(v['parola'])))
    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Il vocabolario di Serena", "url": SITE + "/vocabolario/", "inLanguage": "it",
          "hasDefinedTerm": [{"@type": "DefinedTerm", "name": v['parola'], "description": v['frase'], "termCode": str(v['numero']), "url": f"{SITE}/vocabolario/#{_slug(v['parola'])}"} for v in VOC]}
    pages.append(page('/vocabolario/', 'Il vocabolario di Serena', 'Le parole della vita di casa, con la loro definizione: merenda, cinque minuti, zaino e le altre uscite su Instagram.', f'''
<section class="ph-hd wrap-t voc-hd"><p class="eyebrow">{len(VOC)} parole, finora</p><h1>Il vocabolario <em>di Serena</em></h1>
<p class="lead">Una parola della vita di casa, ogni giorno alle 18 su <a href="{IG}" rel="noopener" data-umami-event="instagram">Instagram</a>.</p></section>
<nav class="wrap-t voc-indice" aria-label="Le parole, in ordine alfabetico"><ul>{indice}</ul></nav>
<section class="wrap-t" aria-label="Le parole del vocabolario"><ol class="voc">{voci}</ol></section>
<section class="wrap-t voc-fondo">{IGCARD}{share('/vocabolario/', 'Il vocabolario di Serena', 'Ti ritrovi in una parola? Mandala a chi la conosce bene.')}</section>''', ld, cls='p-voc', pre=DQ_CSS))
