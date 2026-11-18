// Grafiche di @serenainmente, generate in locale e gratis (nessun servizio a pagamento).
// Uso:  cd gen/grafiche && npm install && node render.js input.json ../../img
// input.json è un elenco di immagini. Campi comuni: file (nome jpg), tipo, sfondo (colore).
//   tipo "frase"      → frase, stile: "" (frase breve minuscola) | "pensiero" | "forte" | "riconoscimento" | "parola"
//                       per "parola": parola, numero (n. del vocabolario), frase = definizione
//                       freccia: true → aggiunge "→" (prima slide di una frase a sospeso)
//   tipo "tabella" → etichetta, titolo, colonne[], righe[][], stato (indice colonna con chip), numeri (indice colonna numerica), nota
//   tipo "zoom"    → etichetta, titolo, r1, r2, chip, testo
//   tipo "copertina"  → etichetta, titolo, sottotitolo [, rubrica, aggiornato]
//   "rub": true su qualunque scheda → accenti verde scuro (rubrica Notizie utili, sfondo #E8EEE6)   (prima slide di carosello o pratico)
//   tipo "passo"      → numero, titolo, testo            (slide centrali)
//   tipo "chiusura"   → titolo, testo, fonte, nota       (ultima slide: in pratica + fonte)
//   story: true       → formato storia 1080x1920 (solo tipo "frase")
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const FONTS = path.join(__dirname, '..', '..', 'assets', 'fonts');
const f64 = file => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, file)).toString('base64');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';

const css = `
@font-face{font-family:Fraunces;font-weight:400;src:url(${f64('fraunces-latin-400-normal.woff2')}) format('woff2');unicode-range:U+0000-00FF,U+2000-206F,U+20AC,U+2122,U+2190-2193}
@font-face{font-family:Fraunces;font-weight:400;src:url(${f64('fraunces-latin-ext-400-normal.woff2')}) format('woff2');unicode-range:U+0100-02AF}
@font-face{font-family:Fraunces;font-weight:600;src:url(${f64('fraunces-latin-600-normal.woff2')}) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:400;src:url(${f64('dm-sans-latin-400-normal.woff2')}) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')}) format('woff2')}
@font-face{font-family:'DM Sans';font-weight:800;src:url(${f64('dm-sans-latin-800-normal.woff2')}) format('woff2')}
*{margin:0;padding:0;box-sizing:border-box}
.c{position:relative;width:1080px;height:1350px;overflow:hidden;color:#3A2C30}
.f{position:absolute;left:150px;top:420px;width:780px;height:400px;display:flex;align-items:center;justify-content:center;text-align:center;font-family:Fraunces,Georgia,serif;font-size:60px;line-height:1.32;text-transform:lowercase;white-space:pre-line}
.pensiero .f{font-size:44px;line-height:1.4;text-transform:none;left:110px;width:860px;top:330px;height:520px}
.riconoscimento .f{font-size:54px;line-height:1.3;text-transform:none;text-align:center;justify-content:center;left:110px;width:860px;top:300px;height:540px}
.forte .f{font-family:'DM Sans',sans-serif;font-weight:800;font-size:64px;line-height:1.12;text-transform:uppercase;text-align:left;justify-content:flex-start;letter-spacing:.5px;left:150px;width:780px;top:280px;height:580px}
.parola .f{font-size:50px;line-height:1.36;text-transform:none;text-align:left;justify-content:flex-start;align-items:flex-start;left:150px;width:800px;top:610px;height:300px}
.parola .t{top:950px}
.parola.lunga .lab{top:360px}.parola.lunga .f{font-size:44px;line-height:1.32;top:540px;height:410px}.parola.lunga .t{top:980px}
.lab{position:absolute;left:150px;top:420px;padding:18px 34px;background:#EBD3D9;font-family:'DM Sans',sans-serif;font-weight:800;font-size:46px;letter-spacing:6px;text-transform:uppercase}
.lab small{display:block;font-weight:500;font-size:20px;letter-spacing:2px;color:#97606F;text-transform:none;margin-top:6px}
.t{position:absolute;left:0;top:860px;width:1080px;height:200px}
.s{position:absolute;left:240px;top:1210px;width:600px;height:50px;display:flex;align-items:center;justify-content:center;font-family:'DM Sans',sans-serif;font-weight:500;font-size:24px;letter-spacing:3px;color:#97606F}
.arrow{position:absolute;right:110px;top:1190px;font-family:Fraunces,serif;font-size:64px;color:#97606F}
.story.c{height:1920px}.story .f{top:560px;height:640px}.story .t{top:1290px}.story .s{top:1640px}
/* caroselli */
.cnt{position:absolute;right:110px;top:110px;font-family:'DM Sans',sans-serif;font-weight:500;font-size:28px;letter-spacing:3px;color:#97606F}
.tab{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 24px 50px -30px rgba(58,44,48,.45);font-family:'DM Sans',sans-serif}
.tab th{background:#4A383D;color:#FBF6F4;font-weight:800;font-size:19px;letter-spacing:1px;text-transform:uppercase;text-align:left;padding:16px 14px}
.tab td{font-size:24px;line-height:1.25;padding:16px 14px;border-top:1px solid #EFE6E8;color:#3A2C30;vertical-align:middle}
.tab td.n{font-weight:800;text-align:right;white-space:nowrap}
.chip{display:inline-block;border-radius:30px;padding:6px 14px;font-size:19px;font-weight:800;white-space:nowrap}
.chip.sa{background:#F6D8D2;color:#8A3B2E}.chip.sb{background:#F8EBC8;color:#7A5A12}.chip.sc{background:#E3EDE0;color:#3F5C3B}
.card{background:#fff;border-radius:26px;padding:44px 48px;box-shadow:0 24px 50px -30px rgba(58,44,48,.45);display:flex;flex-direction:column;gap:18px;font-family:'DM Sans',sans-serif}
.card .r1{font-size:30px;color:#6B575C}.card .r2{font-family:Fraunces,serif;font-size:64px;line-height:1.1}.card .r3{font-size:44px;font-weight:800}

.rub .eti,.rub .scorri,.rub .agg{color:#4F6B4C}.rub .num{background:#5B7558;color:#F4F7F2}.pill{align-self:flex-start;background:#5B7558;color:#F4F7F2;font-family:'DM Sans',sans-serif;font-weight:800;font-size:28px;letter-spacing:4px;padding:14px 28px;border-radius:44px;text-transform:uppercase;margin-bottom:6px}.agg{font-family:'DM Sans',sans-serif;font-weight:500;font-size:26px;margin-top:6px}
.densa .k{gap:26px}.densa .pt{font-size:60px}.densa .px{font-size:34px;line-height:1.45}
.k{position:absolute;left:110px;right:110px;top:150px;bottom:230px;display:flex;flex-direction:column;justify-content:center;gap:40px}
.eti{font-family:'DM Sans',sans-serif;font-weight:800;font-size:26px;letter-spacing:5px;text-transform:uppercase;color:#97606F}
.tit{font-family:Fraunces,serif;font-weight:600;font-size:84px;line-height:1.08;white-space:pre-line}
.sot{font-family:'DM Sans',sans-serif;font-size:38px;line-height:1.4;color:#5E4A4F;white-space:pre-line}
.num{width:110px;height:110px;border-radius:50%;background:#97606F;color:#FBF6F4;display:grid;place-items:center;font-family:Fraunces,serif;font-size:60px}
.pt{font-family:Fraunces,serif;font-size:66px;line-height:1.15;white-space:pre-line}
.px{font-family:'DM Sans',sans-serif;font-size:38px;line-height:1.45;color:#4A383D;white-space:pre-line}
.ct{font-family:Fraunces,serif;font-size:58px;line-height:1.2;white-space:pre-line}
.box{background:rgba(255,255,255,.6);border-radius:22px;padding:30px 36px;display:flex;flex-direction:column;gap:14px}
.fo{font-family:'DM Sans',sans-serif;font-weight:500;font-size:28px;line-height:1.4}
.no{font-family:'DM Sans',sans-serif;font-size:23px;line-height:1.4;color:#6B575C}
.mini{position:absolute;left:110px;bottom:110px;width:200px;height:auto}
.firma{position:absolute;right:110px;bottom:118px;font-family:'DM Sans',sans-serif;font-weight:500;font-size:24px;letter-spacing:3px;color:#97606F}
.scorri{position:absolute;right:110px;bottom:170px;font-family:'DM Sans',sans-serif;font-weight:500;font-size:26px;color:#97606F}
`;
const PATH = 'M 300 128 C 380 128 400 62 470 62 C 540 62 552 138 620 138 C 690 138 700 84 760 84';
const filo = `<svg class="t" viewBox="0 0 1080 200"><path d="${PATH}" fill="none" stroke="#97606F" stroke-width="7" stroke-linecap="round"/><circle cx="792" cy="84" r="9" fill="#C99AA6"/></svg>`;
const filoMini = `<svg class="mini" viewBox="280 40 540 110"><path d="${PATH}" fill="none" stroke="#97606F" stroke-width="9" stroke-linecap="round"/><circle cx="792" cy="84" r="11" fill="#C99AA6"/></svg>`;
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;');
const SFONDI = { copertina: '#F4E9EC', passo: '#FBF6F4', chiusura: '#F2EBE3' };

function corpo(it) {
  const tipo = it.tipo || 'frase';
  if (tipo === 'frase') {
    const lab = it.parola ? `<div class="lab">${esc(it.parola)}<small>il vocabolario di Serena · n. ${esc(it.numero)}</small></div>` : '';
    return `${it.conta ? `<div class="cnt">${esc(it.conta)}</div>` : ''}${lab}<div class="f">${esc(it.frase)}</div>${filo}<div class="s">serenainmente</div>${it.freccia ? '<div class="arrow">→</div>' : ''}`;
  }
  const piede = `${filoMini}<div class="firma">serenainmente</div>`;
  if (tipo === 'copertina')
    return `<div class="k">${it.rubrica ? `<div class="pill">${esc(it.rubrica)}</div>` : ''}<div class="eti">${esc(it.etichetta)}</div><div class="tit">${esc(it.titolo)}</div>${it.sottotitolo ? `<div class="sot">${esc(it.sottotitolo)}</div>` : ''}${it.aggiornato ? `<div class="agg">${esc(it.aggiornato)}</div>` : ''}</div><div class="scorri">scorri →</div>${piede}`;
  if (tipo === 'passo')
    return `<div class="k"><div class="num">${esc(it.numero)}</div><div class="pt">${esc(it.titolo)}</div><div class="px">${esc(it.testo)}</div></div>${piede}`;
  if (tipo === 'chiusura')
    return `<div class="k"><div class="eti">${esc(it.etichetta || 'in pratica')}</div><div class="ct">${esc(it.titolo)}</div>${it.testo ? `<div class="px">${esc(it.testo)}</div>` : ''}${it.fonte || it.nota ? `<div class="box">${it.fonte ? `<div class="fo">${esc(it.fonte)}</div>` : ''}${it.nota ? `<div class="no">${esc(it.nota)}</div>` : ''}</div>` : ''}</div>${piede}`;
  if (tipo === 'tabella') {
    const cls = v => /settimana|scadut/i.test(v) ? 'sa' : /30 giorni/i.test(v) ? 'sb' : 'sc';
    const th = it.colonne.map(c => `<th>${esc(c)}</th>`).join('');
    const tr = it.righe.map(r => `<tr>${r.map((v, i) => i === it.stato ? `<td><span class="chip ${cls(v)}">${esc(v)}</span></td>` : `<td class="${i === it.numeri ? 'n' : ''}">${esc(v)}</td>`).join('')}</tr>`).join('');
    return `<div class="k" style="gap:30px"><div class="eti">${esc(it.etichetta || '')}</div><div class="ct">${esc(it.titolo)}</div><table class="tab"><tr>${th}</tr>${tr}</table>${it.nota ? `<div class="no">${esc(it.nota)}</div>` : ''}</div>${piede}`;
  }
  if (tipo === 'zoom')
    return `<div class="k"><div class="eti">${esc(it.etichetta || '')}</div><div class="ct">${esc(it.titolo)}</div><div class="card"><div class="r1">${esc(it.r1)}</div><div class="r2">${esc(it.r2)}</div><div class="r3">${it.chip ? `<span class="chip sa" style="font-size:34px;padding:10px 22px">${esc(it.chip)}</span>` : ''}</div></div>${it.testo ? `<div class="px">${esc(it.testo)}</div>` : ''}</div>${piede}`;
  throw new Error('tipo sconosciuto: ' + tipo);
}

(async () => {
  const [input, outdir] = process.argv.slice(2);
  if (!input || !outdir) { console.error('uso: node render.js input.json cartella_uscita'); process.exit(1); }
  const items = JSON.parse(fs.readFileSync(input, 'utf8'));
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ executablePath: EXE });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 } });
  for (const it of items) {
    const tipo = it.tipo || 'frase';
    const bg = it.sfondo || SFONDI[tipo] || '#FBF6F4';
    const h = it.story ? 1920 : 1350;
    const cls = `c ${it.densa ? 'densa ' : ''}${(it.rub || it.rubrica) ? 'rub ' : ''}${tipo === 'frase' ? (it.stile || '') + (it.parola ? ' parola' + (String(it.frase || '').split('\n').length > 4 ? ' lunga' : '') : '') : ''} ${it.story ? 'story' : ''}`;
    await page.setViewportSize({ width: 1080, height: h });
    await page.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body><div class="${cls}" style="background:${bg}">${corpo(it)}</div></body></html>`, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    // controllo: il testo non deve uscire dal riquadro
    const over = await page.evaluate(() => [...document.querySelectorAll('.f,.k')].some(el => el.scrollHeight > el.clientHeight + 2));
    if (over) console.warn('ATTENZIONE testo troppo lungo:', it.file);
    await page.screenshot({ path: path.join(outdir, it.file), type: 'jpeg', quality: 90 });
    console.log('ok', it.file);
  }
  await browser.close();
})();
