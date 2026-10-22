// Pin verticali per Pinterest (1000x1500): assets/pin/<chiave>.jpg
// Uso: cd gen/grafiche && node pin.js
const fs = require('fs'); const path = require('path'); const { chromium } = require('playwright-core');
const ROOT = path.join(__dirname, '..', '..'); const FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = f => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, f)).toString('base64');
const i64 = f => `data:image/${f.endsWith('.png') ? 'png' : 'webp'};base64,` + fs.readFileSync(f).toString('base64');
const EXE = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const LOGO = fs.readFileSync(path.join(ROOT, 'assets', 'brand', 'profilo-serena-senza-s.svg'), 'utf8').replace(/width="1080" height="1080"/, 'width="64" height="64"');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const css = `@font-face{font-family:Fraunces;font-weight:400;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:400;src:url(${f64('dm-sans-latin-400-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
.c{width:1000px;height:1500px;display:flex;flex-direction:column;padding:70px 70px 56px;color:#3A2C30;background:var(--bg)}
.chip{align-self:flex-start;font:500 24px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#7F4E5C;background:#fff8;padding:10px 22px;border-radius:999px}
h1{font:400 76px/1.08 Fraunces,serif;margin-top:34px}
p{font:400 32px/1.4 'DM Sans';margin-top:22px;color:#5B4A4F}
.im{flex:1;margin:44px 0 36px;display:flex;align-items:center;justify-content:center;min-height:0}
.im img{max-width:100%;max-height:100%;border-radius:12px;box-shadow:0 30px 60px -30px rgba(58,44,48,.55);background:#fff}
.b{display:flex;align-items:center;justify-content:space-between;font:500 28px 'DM Sans';color:#97606F;letter-spacing:.04em}
.b span{display:flex;align-items:center;gap:16px}.g{background:#97606F;color:#fff;padding:14px 26px;border-radius:999px;font-size:26px}`;
const PINS = [
  ['lista-delle-medicine', '#F4E9EC', 'Da stampare, gratis', 'La lista delle medicine da stampare', 'Per chi segue un genitore o un nonno: si scrive insieme, a quattro mani.', 'assets/stampabili/lista-delle-medicine.webp'],
  ['settimana-sul-frigo', '#F2EBE3', 'Da stampare, gratis', 'Il planner settimanale della famiglia', 'Da attaccare al frigo: chi va dove, visite, chi accompagna.', 'assets/stampabili/settimana-sul-frigo.webp'],
  ['domande-per-il-pediatra', '#E8EDE4', 'Da stampare, gratis', 'Le domande da fare al pediatra', 'Un foglio da compilare a casa: in ambulatorio non dimentichi niente.', 'assets/stampabili/domande-per-il-pediatra.webp'],
  ['gestionale', '#FBF6F4', 'File gratuito', 'Il gestionale di famiglia', 'Visite, scadenze e documenti in un file solo. Excel o Fogli Google, anche dal telefono.', 'assets/gestionale/inizia.webp'],
  ['preparo-la-visita', '#EBD3D9', 'Gratis, dal telefono', 'Prepara la visita dal pediatra', 'Cosa hai notato e le domande in ordine. In ambulatorio hai tutto davanti.', process.env.PREPARO || ''],
];
(async () => {
  const b = await chromium.launch({ executablePath: EXE }); const p = await b.newPage({ viewport: { width: 1000, height: 1500 } });
  for (const [k, bg, chip, t, d, img] of PINS) {
    if (!img || !fs.existsSync(path.isAbsolute(img) ? img : path.join(ROOT, img))) { console.log('salto', k); continue; }
    const src = i64(path.isAbsolute(img) ? img : path.join(ROOT, img));
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="--bg:${bg}"><span class="chip">${chip}</span><h1>${esc(t)}</h1><p>${esc(d)}</p><div class="im"><img src="${src}"></div><div class="b"><span>${LOGO}serenainmente.it</span><span class="g">${k === 'preparo-la-visita' ? 'Provalo gratis' : 'Scaricalo gratis'}</span></div></div>`);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(ROOT, 'assets', 'pin', `${k}.jpg`), type: 'jpeg', quality: 88 }); console.log('ok', k);
  }
  await b.close();
})();
