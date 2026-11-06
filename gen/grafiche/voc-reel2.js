// Il vocabolario di Serena, versione 2 (dal 7/11/2026): voce da dizionario vero
// (parola, categoria scritta per intero, definizione, esempio d'uso) e il filo che, finita la lettura,
// continua e disegna a linea continua il profilo di una donna, chiaro, dietro il testo.
// Uso: cd gen/grafiche && node voc-reel2.js post/vocabolario-2026-11.json [AAAA-MM-GG] [cartella-uscita]
// Esce in video/AAAA-MM-GG-reel-v3.mp4 e video/AAAA-MM-GG-reel-v3-cover.jpg (o nella cartella indicata).
// Zona sicura di Instagram: niente testo nei primi 250 px e negli ultimi 260 px.
const fs = require('fs'), path = require('path'), { execSync } = require('child_process'), { chromium } = require('playwright-core');
const ROOT = path.join(__dirname, '..', '..'), FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = n => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, n)).toString('base64');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const FPS = 30;
// il filo di sempre, poi la donna: nuca, crocchia, testa, occhio chiuso, profilo, collo
const FILO = 'M 300 1418 C 380 1418 400 1352 470 1352 C 540 1352 552 1428 620 1428 C 690 1428 700 1374 760 1374';
const DONNA = 'M 760 1374 C 840 1374 905 1350 920 1290 C 935 1230 900 1170 885 1110 C 878 1080 880 1055 895 1040 C 930 1060 985 1050 995 1005 C 1005 955 960 930 925 948 C 900 960 905 990 925 990 C 950 985 955 940 940 900 C 960 820 930 750 870 720 C 800 685 700 695 665 750 C 645 782 645 812 646 838 C 646 856 638 868 630 882 C 618 904 604 920 608 932 C 612 942 624 942 630 946 C 622 956 622 964 632 970 C 624 978 622 988 630 996 C 638 1006 632 1020 640 1034 C 652 1054 684 1058 708 1052 C 716 1100 712 1150 694 1190 C 674 1230 614 1250 560 1255';
const DETTAGLI = 'M 676 842 C 686 856 704 858 716 846 M 682 852 L 676 864 M 694 856 L 692 868 M 706 854 L 708 866 M 700 712 C 760 760 800 820 790 900';
const css = `@font-face{font-family:Fr;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:DM;font-weight:800;src:url(${f64('dm-sans-latin-800-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}body{margin:0}
.c{width:1080px;height:1920px;position:relative;overflow:hidden;color:#3A2C30}
svg.d{position:absolute;left:0;top:0;width:1080px;height:1920px}
.lab{position:absolute;left:130px;top:380px;padding:22px 40px;background:#EBD3D9;font:800 58px DM;letter-spacing:7px;text-transform:uppercase}
.lab small{display:block;font:500 24px DM;letter-spacing:2px;color:#97606F;text-transform:none;margin-top:8px}
.g{position:absolute;left:130px;top:600px;font:500 28px DM;letter-spacing:2px;color:#97606F}
.f{position:absolute;left:130px;width:860px;top:660px;font-family:Fr;font-size:56px;line-height:1.36}
.l{opacity:0;transform:translateY(16px);white-space:nowrap}
.e{margin-top:42px;opacity:0}
.e b{display:block;font:500 24px DM;letter-spacing:3px;text-transform:uppercase;color:#97606F;margin-bottom:6px}
.e div{font-family:Fr;font-size:44px;line-height:1.3;color:#6E4552;white-space:nowrap}
.s{position:absolute;left:0;right:0;top:1580px;text-align:center;font:500 28px DM;letter-spacing:4px;color:#97606F;opacity:0}`;
const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
(async () => {
  const [file, solo, outDir] = process.argv.slice(2);
  const voci = JSON.parse(fs.readFileSync(file, 'utf8')).voci.filter(v => !solo || v.data === solo);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const v of voci) {
    const lines = v.frase.split('\n'), ex = (v.esempio || '').split('\n').filter(Boolean);
    const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="background:${v.sfondo}">
<svg class="d" viewBox="0 0 1080 1920" fill="none" stroke-linecap="round" stroke-linejoin="round"><g transform="translate(40 0)">
<path id="dn" d="${DONNA}" stroke="#C99AA6" stroke-width="4.5" opacity=".55"/>
<path id="dt" d="${DETTAGLI}" stroke="#C99AA6" stroke-width="4" opacity="0"/>
<path id="fi" d="${FILO}" stroke="#97606F" stroke-width="7"/></g></svg>
<div class="lab">${esc(v.parola)}<small>il vocabolario di Serena · n. ${esc(v.numero)}</small></div>
<div class="g">${esc(v.categoria || '')}</div>
<div class="f">${lines.map(l => `<div class="l">${esc(l)}</div>`).join('')}${ex.length ? `<div class="e"><b>esempio</b>${ex.map(l => `<div>${esc(l)}</div>`).join('')}</div>` : ''}</div>
<div class="s">serenainmente</div></div>`;
    await p.setContent(html); await p.evaluate(() => document.fonts.ready);
    // controllo: nessuna riga oltre 860 px, il testo finisce sopra il filo
    const chk = await p.evaluate(() => { const f = document.querySelector('.f'); const w = Math.max(...[...f.querySelectorAll('.l, .e div')].map(l => l.scrollWidth)); return { w, bottom: f.getBoundingClientRect().bottom }; });
    if (chk.w > 860 || chk.bottom > 1330) throw new Error(`${v.data}: testo troppo largo o lungo ${JSON.stringify(chk)}`);
    const tl = 0.5 + lines.length * 0.8, te = tl + 0.3, tx = te + (ex.length ? 1.6 : 0);
    const tf = tx + 0.2, td = tf + 1.2, DUR = Math.ceil(td + 2.6 + 0.9 + 2.2), N = FPS * DUR;
    const dir = fs.mkdtempSync('/tmp/voc2-');
    for (let i = 0; i < N; i++) {
      const t = i / FPS;
      await p.evaluate(({ t, te, tf, td }) => {
        const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
        const inout = t => t < 0 ? 0 : t > 1 ? 1 : t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        document.querySelectorAll('.l').forEach((el, k) => { const q = ease((t - 0.5 - k * 0.8) / 0.8); el.style.opacity = q; el.style.transform = `translateY(${16 * (1 - q)}px)`; });
        const e = document.querySelector('.e'); if (e) e.style.opacity = ease((t - te) / 0.8);
        const fi = document.getElementById('fi'), Lf = fi.getTotalLength(); fi.style.strokeDasharray = Lf; fi.style.strokeDashoffset = Lf * (1 - inout((t - tf) / 1.2));
        const dn = document.getElementById('dn'), Ld = dn.getTotalLength(); dn.style.strokeDasharray = Ld; dn.style.strokeDashoffset = Ld * (1 - inout((t - td) / 2.6));
        document.getElementById('dt').style.opacity = 0.55 * ease((t - td - 2.4) / 0.6);
        document.querySelector('.s').style.opacity = ease((t - td - 2.7) / 0.6);
      }, { t, te, tf, td });
      await p.screenshot({ path: `${dir}/${String(i).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
    }
    const od = outDir || path.join(ROOT, 'video');
    const out = path.join(od, `${v.data}-reel-v3.mp4`), cov = path.join(od, `${v.data}-reel-v3-cover.jpg`);
    execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/%04d.jpg -c:v libx264 -preset veryfast -pix_fmt yuv420p -profile:v high -crf 20 -movflags +faststart "${out}"`);
    fs.copyFileSync(`${dir}/${String(N - 1).padStart(4, '0')}.jpg`, cov);
    fs.rmSync(dir, { recursive: true });
    console.log('ok', path.basename(out), DUR + 's');
  }
  await b.close();
})();
