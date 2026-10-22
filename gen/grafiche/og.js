// Immagini di anteprima (Open Graph, 1200x630) per ogni guida: assets/og/<slug>.jpg
// Uso: cd gen/grafiche && node og.js
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const ROOT = path.join(__dirname, '..', '..');
const D = JSON.parse(fs.readFileSync(path.join(ROOT, 'gen', 'dati.json'), 'utf8'));
const FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = f => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, f)).toString('base64');
const img64 = f => 'data:image/webp;base64,' + fs.readFileSync(f).toString('base64');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const LOGO = fs.readFileSync(path.join(ROOT, 'assets', 'brand', 'profilo-serena-senza-s.svg'), 'utf8').replace(/width="1080" height="1080"/, 'width="54" height="54"');
const ARG = { salute: 'Salute e visite', documenti: 'Documenti e burocrazia', organizzazione: 'Organizzazione e quotidianità', crescita: 'Bambini e crescita' };
const GUIDA_ARG = { 'domande-per-il-pediatra': 'salute', 'visita-specialistica-come-funziona': 'salute', 'spostare-disdire-pagare-visita': 'salute',
  'documenti-sanitari-dove-trovarli': 'documenti', 'pediatra-e-medico-di-base': 'documenti', 'cartellina-di-famiglia': 'organizzazione', 'routine-della-nanna': 'crescita' };
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

const css = `
@font-face{font-family:Fraunces;font-weight:400;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
.c{width:1200px;height:630px;display:flex;background:#F8F4EF;color:#3A2C30;overflow:hidden}
.t{width:640px;padding:56px 48px 48px 64px;display:flex;flex-direction:column}
.chip{align-self:flex-start;font:500 17px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#7F4E5C;background:#F4E9EC;padding:8px 16px;border-radius:999px}
h1{font-family:Fraunces,Georgia,serif;font-weight:400;line-height:1.12;margin-top:30px;font-size:var(--fs)}
.b{margin-top:auto;display:flex;align-items:center;gap:14px;font:500 22px 'DM Sans';letter-spacing:.06em;color:#97606F}
.p{flex:1;background-size:cover;background-position:center;border-radius:28px 0 0 28px}
`;

(async () => {
  const out = path.join(ROOT, 'assets', 'og'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ executablePath: EXE });
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  for (const g of D.guide) {
    const arg = g.argomento || GUIDA_ARG[g.slug] || 'organizzazione';
    const foto = path.join(ROOT, 'assets', 'foto', `${g.slug}.webp`);
    const bg = fs.existsSync(foto) ? `background-image:url(${img64(foto)})` : 'background:#F4E9EC';
    const fs_ = g.titolo.length > 80 ? 42 : g.titolo.length > 55 ? 50 : 58;
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c"><div class="t"><span class="chip">${ARG[arg]}</span><h1 style="--fs:${fs_}px">${esc(g.titolo)}</h1><div class="b">${LOGO}serenainmente.it</div></div><div class="p" style="${bg}"></div></div>`);
    await p.evaluate(() => document.fonts.ready);
    const h = await p.evaluate(() => document.querySelector('h1').getBoundingClientRect().bottom);
    if (h > 520) console.log('ATTENZIONE titolo lungo', g.slug, h);
    await p.screenshot({ path: path.join(out, `${g.slug}.jpg`), type: 'jpeg', quality: 86 });
    console.log('ok', g.slug);
  }
  // fogli da stampare: anteprima del PDF a destra
  const SP = [['settimana-sul-frigo', 'Il planner della settimana, da stampare'], ['domande-per-il-pediatra', 'Le domande per il pediatra, da stampare'], ['lista-delle-medicine', 'La lista delle medicine, da stampare']];
  for (const [f, t] of SP) {
    const img = path.join(ROOT, 'assets', 'stampabili', `${f}.webp`);
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}.p{background:#F4E9EC ${'url('}${img64(img)}) center/88% auto no-repeat;}</style><div class="c"><div class="t"><span class="chip">Da stampare, gratis</span><h1 style="--fs:54px">${esc(t)}</h1><div class="b">${LOGO}serenainmente.it</div></div><div class="p"></div></div>`);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(out, `stampabili-${f}.jpg`), type: 'jpeg', quality: 86 });
    console.log('ok', f);
  }
  await b.close();
})();
