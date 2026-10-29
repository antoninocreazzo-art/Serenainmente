// Il vocabolario di Serena — reel 1080x1920, 30 fps, ~8 s: l'etichetta della parola, la definizione riga per riga, il filo.
// La copertina è l'ultimo fotogramma (la "pagina del vocabolario").
// Uso: cd gen/grafiche && node voc-reel.js post/vocabolario-2026-11.json [AAAA-MM-GG]
// Esce in video/AAAA-MM-GG-reel.mp4 e video/AAAA-MM-GG-reel-cover.jpg
// Zona sicura di Instagram: niente testo nei primi 250 px e negli ultimi 260 px.
const fs = require('fs'), path = require('path'), { execSync } = require('child_process'), { chromium } = require('playwright-core');
const ROOT = path.join(__dirname, '..', '..'), FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = n => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, n)).toString('base64');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const FPS = 30;
const css = `@font-face{font-family:Fr;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:DM;font-weight:800;src:url(${f64('dm-sans-latin-800-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}body{margin:0}
.c{width:1080px;height:1920px;position:relative;overflow:hidden;color:#3A2C30}
.lab{position:absolute;left:130px;top:560px;padding:22px 40px;background:#EBD3D9;font:800 58px DM;letter-spacing:7px;text-transform:uppercase;}
.lab small{display:block;font:500 24px DM;letter-spacing:2px;color:#97606F;text-transform:none;margin-top:8px}
.f{position:absolute;left:130px;width:860px;top:820px;font-family:Fr;font-size:58px;line-height:1.38}
.l{opacity:0;transform:translateY(16px);white-space:nowrap}
.t{position:absolute;left:0;top:1290px;width:1080px}
.t path{stroke-dasharray:600;stroke-dashoffset:600}.t circle{opacity:0}
.s{position:absolute;left:0;right:0;top:1580px;text-align:center;font:500 28px DM;letter-spacing:4px;color:#97606F;opacity:0}`;
const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
(async () => {
  const [file, solo] = process.argv.slice(2);
  const voci = JSON.parse(fs.readFileSync(file, 'utf8')).voci.filter(v => !solo || v.data === solo);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const v of voci) {
    const lines = v.frase.split('\n');
    const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="background:${v.sfondo}">
<div class="lab">${esc(v.parola)}<small>il vocabolario di Serena · n. ${esc(v.numero)}</small></div>
<div class="f">${lines.map(l => `<div class="l">${esc(l)}</div>`).join('')}</div>
<svg class="t" viewBox="0 0 1080 200"><path d="M 300 128 C 380 128 400 62 470 62 C 540 62 552 138 620 138 C 690 138 700 84 760 84" fill="none" stroke="#97606F" stroke-width="7" stroke-linecap="round"/><circle cx="792" cy="84" r="9" fill="#C99AA6"/></svg>
<div class="s">serenainmente</div></div>`;
    await p.setContent(html); await p.evaluate(() => document.fonts.ready);
    // controllo: nessuna riga esce dal riquadro, la definizione non tocca il filo
    const chk = await p.evaluate(() => { const f = document.querySelector('.f'); const w = Math.max(...[...f.children].map(l => l.scrollWidth)); return { w, bottom: f.getBoundingClientRect().bottom }; });
    if (chk.w > 860 || chk.bottom > 1290) throw new Error(`${v.data}: testo troppo largo o lungo ${JSON.stringify(chk)}`);
    const tl = 0.5 + lines.length * 0.8, DUR = Math.max(8, Math.ceil(tl + 3.6)), N = FPS * DUR;
    const dir = fs.mkdtempSync('/tmp/voc-');
    for (let i = 0; i < N; i++) {
      const t = i / FPS;
      await p.evaluate(({ t, lines, tl }) => {
        const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
        const lab = document.querySelector('.lab'); lab.style.opacity = 1;
        document.querySelectorAll('.l').forEach((el, k) => { const q = ease((t - 0.5 - k * 0.8) / 0.8); el.style.opacity = q; el.style.transform = `translateY(${16 * (1 - q)}px)`; });
        const pf = ease((t - tl - 0.2) / 1.2);
        document.querySelector('.t path').style.strokeDashoffset = 600 * (1 - pf);
        document.querySelector('.t circle').style.opacity = ease((t - tl - 1.3) / 0.4);
        document.querySelector('.s').style.opacity = ease((t - tl - 1.5) / 0.6);
      }, { t, lines, tl });
      await p.screenshot({ path: `${dir}/${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
    }
    const out = path.join(ROOT, 'video', `${v.data}-reel.mp4`), cov = path.join(ROOT, 'video', `${v.data}-reel-cover.jpg`);
    execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/%04d.jpg -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 20 -movflags +faststart "${out}"`);
    fs.copyFileSync(`${dir}/${String(N - 1).padStart(4, '0')}.jpg`, cov);
    fs.rmSync(dir, { recursive: true });
    console.log('ok', path.basename(out), DUR + 's');
  }
  await b.close();
})();
