# BOZZA — NON PUBBLICARE PRIMA DEL LANCIO PUBBLICO (7 gennaio 2027)

Pagina `serenainmente.it/n/app`: è l'arrivo del QR di pag. 139 del quaderno «Nascita» nella versione con l'app (`APP=si`).
Sta in `gen/` apposta: la cartella non si pubblica (`_config.yml`) e `build.py` non la legge. Fino al lancio la pagina non esiste,
non è collegata da nessuna parte e non è nella sitemap. Al lancio si trasforma in una pagina vera, con gli stessi modelli delle pagine `/n/…`.

Da riconfermare nell'app prima di pubblicare: le parole dei pulsanti («Aggiungi al calendario del telefono», «Salva una copia», «Riprendi da una copia»),
dove stanno (Profilo → «I tuoi dati») e quando suona l'avviso del calendario. Le immagini delle schermate vere si aggiungono al lancio, da un Android e da un iPhone.
Le frasi fra virgolette basse «…» qui sotto sono parole dell'app o del quaderno: si lasciano come sono.

---

## Serenainmente

Dal quaderno Nascita, pag. 139

Il quaderno è il primo modo: quello che è scritto lì non va più tenuto a mente. Il secondo sta nel telefono: è l'app Serenainmente, con visite, scadenze, promemoria e documenti in un posto solo. Una data segnata lì passa, con un tocco, al calendario del telefono, che vi avvisa.

Per visite, scadenze e promemoria è gratuita, e non chiede un account. Quello che scrivete resta sul vostro telefono: a noi non arriva niente.

**[Apri Serenainmente]** → https://app.serenainmente.it

Si apre dal browser, all'indirizzo app.serenainmente.it. Non è negli store.

## Tenerla sulla schermata Home

Così si apre con un tocco, come le altre app.

### Android, con Chrome
1. Aprite app.serenainmente.it con Chrome.
2. Toccate il menù, i tre puntini in alto a destra.
3. Toccate «Aggiungi a schermata Home» oppure «Installa app» (dipende dal telefono).
4. Confermate. L'icona di Serenainmente compare sulla schermata Home.

*(immagine: il menù di Chrome con la voce evidenziata — da fare al lancio, su un Android vero)*

### iPhone, con Safari
1. Aprite app.serenainmente.it con Safari.
2. Toccate «Condividi», il quadrato con la freccia verso l'alto.
3. Scorrete e toccate «Aggiungi alla schermata Home».
4. Toccate «Aggiungi». L'icona di Serenainmente compare sulla schermata Home.

*(immagine: il foglio «Condividi» di Safari con la voce evidenziata — da fare al lancio, su un iPhone vero)*

Su iPhone conviene farlo subito: «Su iPhone, finché Serena resta una pagina di Safari, il telefono può cancellare i suoi dati dopo sette giorni che non la apri. Se la aggiungi alla schermata Home, non succede più.» *(testo dell'app, `js/app.js`, IOS_SETTE_GIORNI)*

## Come arriva l'avviso

Ad app chiusa, Serenainmente non avvisa. Avvisa il calendario del telefono.

Accanto a una visita, a una scadenza o a un promemoria c'è il pulsante «Aggiungi al calendario del telefono». Toccatelo: la data passa nel calendario che usate già, e da lì arriva l'avviso, anche con l'app chiusa.

Il calendario avvisa un'ora prima, se avete segnato l'ora; alle 9 del mattino, se è una data senza ora.

*(immagine: il pulsante «Aggiungi al calendario del telefono» in una visita — da fare al lancio)*

## Se cambiate telefono

Quello che scrivete in Serenainmente sta solo su questo telefono. Se cambiate telefono, o se cancellate i dati del browser, si perde: a meno di aver salvato una copia.

1. Nel telefono di adesso: Profilo → «I tuoi dati» → «Salva una copia». È un file con tutto quello che avete scritto, e si può proteggere con una password.
2. Tenete il file in un posto sicuro, fuori dal telefono.
3. Nel telefono nuovo: aprite app.serenainmente.it, poi Profilo → «I tuoi dati» → «Riprendi da una copia», e scegliete il file.

---

### Note per chi la pubblica
- Indirizzo fisso, stampato nel libro: `/n/app` (con la barra finale la crea GitHub Pages da sé). Non si cambia e non si spegne.
- Stesso trattamento delle altre pagine `/n/…`: fuori da menù, ricerca e sitemap, `noindex`.
- Il video, se e quando esiste: corto, senza audio obbligato, che non parte da solo. Il libro non lo promette.
- Fonti dei fatti: verifica del coordinatore sul codice dell'app (rami `master` e `dinamica`, 20/11/2026) riportata in `PROGETTO-FABLE.md` §E «Verificato nel codice dell'app»; testi di «I tuoi dati» in `index.html` dell'app (Fase 1, M3) e della nota iPhone in `js/app.js`.
- Al lancio, sulle pagine `/n/…` entra anche il blocco «Sul telefono» (F.5, punto 3): pulsante «Apri Serenainmente» e collegamento a questa pagina. Oggi non c'è, apposta.
