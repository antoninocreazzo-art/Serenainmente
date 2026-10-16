# serenainmente.it

Sito di Serena: parole e idee per chi si prende cura della famiglia.

- Contenuti e fonti: `gen/dati.json`
- Generatore delle pagine: `python3 gen/build.py`
- Stile: `assets/stile.css`
- Immagini dei post: `img/`

Pubblicato con GitHub Pages su serenainmente.it.

## Grafiche Instagram (gratis, in locale)

Le immagini dei post si generano con `gen/grafiche/render.js` (vedi i commenti in cima al file per i tipi di slide).

```
cd gen/grafiche && npm install
node render.js post/AAAA-MM-GG.json ../../img
```

Le immagini finiscono in `img/` e, dopo il push, sono pubbliche su `https://serenainmente.it/img/<nome>.jpg`: è l'indirizzo da dare a Metricool.
