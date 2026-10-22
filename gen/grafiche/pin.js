// Pin verticali per Pinterest (1000x1500): assets/pin/<chiave>.jpg
// Uso: cd gen/grafiche && node pin.js   (crea anche ig-<chiave>.jpg 1080x1350 per i post e story-<chiave>.jpg 1080x1920 per le storie)
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
.c{width:var(--w);height:var(--h);display:flex;flex-direction:column;padding:var(--pt) 70px var(--pb);color:#3A2C30;background:var(--bg)}
.chip{align-self:flex-start;font:500 24px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#7F4E5C;background:#fff8;padding:10px 22px;border-radius:999px}
h1{font:400 76px/1.08 Fraunces,serif;margin-top:34px}
p{font:400 32px/1.4 'DM Sans';margin-top:22px;color:#5B4A4F}
.im{flex:1;margin:44px 0 36px;display:flex;align-items:center;justify-content:center;min-height:0}
.im img{max-width:100%;max-height:100%;border-radius:12px;box-shadow:0 30px 60px -30px rgba(58,44,48,.55);background:#fff}
.b{display:flex;align-items:center;justify-content:space-between;font:500 28px 'DM Sans';color:#97606F;letter-spacing:.04em}
.b span{display:flex;align-items:center;gap:16px}.g{background:#97606F;color:#fff;padding:14px 26px;border-radius:999px;font-size:26px}`;

const PHONE = `<div class="ph"><div class="scr">
<div class="top"><span class="dot"></span><b>Preparo la visita</b></div>
<div class="hd">Sofia · Dott.ssa Rossi<br><small>martedì 4 novembre, 16:30</small></div>
<div class="sec">Cosa ho notato</div><div class="txt">Tosse da lunedì, soprattutto di notte. Niente febbre.</div>
<div class="sec">Le domande</div>
<div class="q ok"><i>✓</i><span>La tosse di notte è normale?</span></div><div class="ans">Sì, se non ha febbre e mangia bene.</div>
<div class="q"><i></i><span>Quando richiamare se non passa?</span></div>
<div class="q"><i></i><span>Può andare all'asilo?</span></div>
<div class="btns"><span class="b1">Sono in ambulatorio</span><span class="b2">Manda il riepilogo</span></div>
</div></div>`;
const PHONE_CSS = `.ph{width:430px;height:100%;max-height:820px;background:#3A2C30;border-radius:56px;padding:16px;box-shadow:0 40px 70px -30px rgba(58,44,48,.6)}
.scr{background:#FBF6F4;border-radius:42px;height:100%;overflow:hidden;padding:34px 30px;font-family:'DM Sans';text-align:left}
.top{display:flex;align-items:center;gap:12px;font-size:22px;color:#97606F;margin-bottom:22px}.dot{width:26px;height:26px;border-radius:50%;background:#EBD3D9;border:5px solid #F4E9EC}
.hd{background:#F4E9EC;border-radius:18px;padding:16px 18px;font:400 26px/1.3 Fraunces;color:#3A2C30;margin-bottom:8px}.hd small{font:400 19px 'DM Sans';color:#7F4E5C}
.sec{font:400 25px Fraunces;color:#3A2C30;margin:20px 0 8px}.txt{font-size:20px;line-height:1.4;color:#5B4A4F}
.q{display:flex;gap:12px;align-items:flex-start;font-size:21px;line-height:1.3;color:#3A2C30;margin:12px 0 6px}.q i{flex:none;width:26px;height:26px;border:2.5px solid #97606F;border-radius:7px;font-style:normal;color:#fff;display:grid;place-items:center;font-size:17px;margin-top:1px}.q.ok i{background:#97606F}
.ans{margin:0 0 6px 38px;background:#fff;border:1.5px solid #EBD3D9;border-radius:12px;padding:10px 12px;font-size:19px;color:#5B4A4F}
.compact .b2,.compact .top{display:none}.compact .scr{padding:24px 26px}.compact .sec{margin:12px 0 6px}.btns{display:flex;flex-direction:column;gap:10px;margin-top:22px}.btns span{border-radius:999px;padding:14px;text-align:center;font-size:20px}.b1{background:#97606F;color:#fff}.b2{border:2px solid #97606F;color:#97606F}`;

const PINS = [
  ['lista-delle-medicine', '#F4E9EC', 'Da stampare, gratis', 'La lista delle medicine da stampare', 'Per chi segue un genitore o un nonno: si scrive insieme, a quattro mani.', 'assets/stampabili/lista-delle-medicine.webp'],
  ['settimana-sul-frigo', '#F2EBE3', 'Da stampare, gratis', 'Il planner settimanale della famiglia', 'Da attaccare al frigo: chi va dove, visite, chi accompagna.', 'assets/stampabili/settimana-sul-frigo.webp'],
  ['domande-per-il-pediatra', '#E8EDE4', 'Da stampare, gratis', 'Le domande da fare al pediatra', 'Un foglio da compilare a casa: in ambulatorio non dimentichi niente.', 'assets/stampabili/domande-per-il-pediatra.webp'],
  ['gestionale', '#FBF6F4', 'File gratuito', 'Il gestionale di famiglia', 'Visite, scadenze e documenti in un file solo. Excel o Fogli Google, anche dal telefono.', 'assets/gestionale/inizia.webp'],
  ['preparo-la-visita', '#EBD3D9', 'Gratis, dal telefono', 'Prepara la visita dal pediatra, dal telefono', 'Scrivi a casa cosa hai notato e le domande in ordine. In ambulatorio hai tutto davanti.', 'PHONE'],
];
(async () => {
  const b = await chromium.launch({ executablePath: EXE });
  const FORMATI = [['', 1000, 1500, 70, 56], ['ig-', 1080, 1350, 70, 56], ['story-', 1080, 1920, 250, 260]];
  for (const [pre, W, H, PT, PB] of FORMATI) {
  const p = await b.newPage({ viewport: { width: W, height: H } });
  for (const [k, bg, chip, t, d, img] of PINS) {
    const isPhone = img === 'PHONE';
    if (!isPhone && (!img || !fs.existsSync(path.join(ROOT, img)))) { console.log('salto', k); continue; }
    const src = isPhone ? '' : i64(path.join(ROOT, img));
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}${PHONE_CSS}</style><div class="c" style="--bg:${bg};--w:${W}px;--h:${H}px;--pt:${PT}px;--pb:${PB}px"><span class="chip">${chip}</span><h1>${esc(t)}</h1><p>${esc(d)}</p><div class="im">${isPhone ? (H < 1400 ? PHONE.replace('class="ph"','class="ph compact"') : PHONE) : `<img src="${src}">`}</div><div class="b"><span>${LOGO}serenainmente.it</span><span class="g">${pre === 'story-' ? 'Link in bio' : (k === 'preparo-la-visita' ? 'Provalo gratis' : 'Scaricalo gratis')}</span></div></div>`);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(ROOT, 'assets', 'pin', `${pre}${k}.jpg`), type: 'jpeg', quality: 88 }); console.log('ok', pre + k);
  }
  await p.close(); }
  await b.close();
})();
