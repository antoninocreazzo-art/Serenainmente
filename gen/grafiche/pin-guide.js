// Pin verticali per Pinterest delle guide (1000x1500): assets/pin/guida-<slug>.jpg
// Uso: cd gen/grafiche && node pin-guide.js
const fs = require('fs'); const path = require('path'); const { chromium } = require('playwright-core');
const ROOT = path.join(__dirname, '..', '..'); const FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = f => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, f)).toString('base64');
const EXE = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const LOGO = fs.readFileSync(path.join(ROOT, 'assets', 'brand', 'profilo-serena.svg'), 'utf8').replace(/width="1080" height="1080"/, 'width="64" height="64"');
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const css = `@font-face{font-family:Fraunces;font-weight:400;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:400;src:url(${f64('dm-sans-latin-400-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
.c{width:1000px;height:1500px;display:flex;flex-direction:column;padding:70px 70px 56px;color:#3A2C30;background:var(--bg)}
.chip{align-self:flex-start;font:500 24px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#7F4E5C;background:#fff8;padding:10px 22px;border-radius:999px}
h1{font:400 78px/1.08 Fraunces,serif;margin-top:34px}
p{font:400 32px/1.4 'DM Sans';margin-top:22px;color:#5B4A4F}
.card{flex:1;margin:44px 0 36px;background:#fff;border-radius:28px;padding:50px 54px;box-shadow:0 30px 60px -30px rgba(58,44,48,.45);display:flex;flex-direction:column;justify-content:center;gap:56px}
.st{display:flex;gap:26px;align-items:flex-start}.n{flex:none;width:76px;height:76px;border-radius:50%;background:#97606F;color:#fff;font:400 38px Fraunces;display:grid;place-items:center}
.st span{font:400 46px/1.2 Fraunces;color:#3A2C30;padding-top:8px}
.b{display:flex;align-items:center;justify-content:space-between;font:500 28px 'DM Sans';color:#97606F;letter-spacing:.04em}
.b span{display:flex;align-items:center;gap:16px}.g{background:#97606F;color:#fff;padding:14px 26px;border-radius:999px;font-size:26px}`;
const G = JSON.parse(fs.readFileSync(path.join(__dirname, 'pin-guide.json'), 'utf8'));
(async () => {
  const b = await chromium.launch({ executablePath: EXE });
  const p = await b.newPage({ viewport: { width: 1000, height: 1500 } });
  for (const g of G) {
    const steps = g.passi.map((s, i) => `<div class="st"><b class="n">${i + 1}</b><span>${esc(s)}</span></div>`).join('');
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="--bg:${g.sfondo}"><span class="chip">Guida gratuita, con le fonti</span><h1>${esc(g.titolo)}</h1><p>${esc(g.sotto)}</p><div class="card">${steps}</div><div class="b"><span>${LOGO}serenainmente.it</span><span class="g">Leggi la guida</span></div></div>`);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(ROOT, 'assets', 'pin', `guida-${g.slug}.jpg`), type: 'jpeg', quality: 88 }); console.log('ok', g.slug);
  }
  await b.close();
})();
