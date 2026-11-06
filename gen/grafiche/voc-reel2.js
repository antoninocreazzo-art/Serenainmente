// Il vocabolario di Serena, versione 2 (dal 7/11/2026): voce da dizionario vero
// (parola, categoria scritta per intero, definizione, esempio d'uso) e il filo che, finita la lettura,
// entra da sinistra e continua a disegnare, a linea continua, il profilo di una donna dietro il testo.
// Uso: cd gen/grafiche && node voc-reel2.js post/vocabolario-2026-11.json [AAAA-MM-GG] [cartella-uscita]
// Esce in video/AAAA-MM-GG-reel-v3.mp4 e video/AAAA-MM-GG-reel-v3-cover.jpg (o nella cartella indicata).
// Zona sicura di Instagram: niente testo nei primi 250 px e negli ultimi 260 px.
const fs = require('fs'), path = require('path'), { execSync } = require('child_process'), { chromium } = require('playwright-core');
const ROOT = path.join(__dirname, '..', '..'), FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = n => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, n)).toString('base64');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const FPS = 30;
// Il filo (la «s» di sempre) entra da sinistra e, senza staccarsi, continua verso destra e disegna a una linea continua
// una donna di 35-40 anni di profilo, quasi a tutta pagina: capelli, ciuffo, fronte, naso, labbra, mento, collo, spalla.
// Lo stile resta sempre a una linea continua (decisione di Antonino, 6/11/2026).
const FILO = 'M -20 1560 C -2 1560 58 1570 90 1560 C 122 1550 143 1510 170 1500 C 197 1490 223 1488 250 1500 C 277 1512 303 1562 330 1575 C 357 1588 387 1584 410 1575 C 433 1566 460 1529 470 1520';
const DONNA = 'M 470 1520 C 471 1511 481 1483 478 1468 C 475 1453 462 1441 452 1430 C 442 1419 428 1417 418 1400 C 408 1383 401 1363 392 1330 C 383 1297 369 1248 362 1200 C 355 1152 347 1093 352 1040 C 357 987 371 929 392 880 C 413 831 445 780 480 745 C 515 710 558 684 600 668 C 642 652 693 648 730 652 C 767 656 798 674 820 690 C 842 706 857 728 862 745 C 867 762 860 781 850 790 C 840 799 813 802 800 800 C 787 798 772 787 770 780 C 768 773 779 761 790 760 C 801 759 823 763 835 775 C 847 787 856 808 862 830 C 868 852 868 882 870 905 C 872 928 877 950 876 968 C 875 986 865 998 866 1010 C 867 1022 872 1028 880 1042 C 888 1056 903 1080 914 1094 C 925 1108 942 1117 946 1126 C 950 1135 945 1143 938 1148 C 931 1153 908 1154 904 1158 C 900 1162 907 1169 912 1174 C 917 1179 931 1185 934 1190 C 937 1195 932 1200 928 1204 C 924 1208 910 1209 910 1212 C 910 1215 924 1218 928 1222 C 932 1226 934 1233 932 1238 C 930 1243 923 1249 918 1254 C 913 1259 904 1260 904 1268 C 904 1276 917 1290 917 1302 C 917 1314 912 1329 904 1338 C 896 1347 883 1352 872 1357 C 861 1362 847 1359 838 1366 C 829 1373 820 1381 816 1400 C 812 1419 809 1453 812 1480 C 815 1507 817 1538 832 1560 C 847 1582 855 1595 900 1610 C 945 1625 1067 1643 1100 1650';
const css = `@font-face{font-family:Fr;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:DM;font-weight:800;src:url(${f64('dm-sans-latin-800-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}body{margin:0}
.c{width:1080px;height:1920px;position:relative;overflow:hidden;color:#3A2C30}
svg.d{position:absolute;left:0;top:0;width:1080px;height:1920px}
.lab{position:absolute;left:130px;top:290px;padding:22px 40px;background:#EBD3D9;font:800 58px DM;letter-spacing:7px;text-transform:uppercase}
.lab small{display:block;font:500 24px DM;letter-spacing:2px;color:#97606F;text-transform:none;margin-top:8px}
.g{position:absolute;left:130px;top:505px;font:500 28px DM;letter-spacing:2px;color:#97606F}
.f{position:absolute;left:130px;width:860px;top:560px;font-family:Fr;font-size:54px;line-height:1.34}
.l{opacity:0;transform:translateY(16px);white-space:nowrap}
.e{margin-top:42px;opacity:0}
.e b{display:block;font:500 24px DM;letter-spacing:3px;text-transform:uppercase;color:#97606F;margin-bottom:6px}
.e div{font-family:Fr;font-size:42px;line-height:1.3;color:#6E4552;white-space:nowrap}
.s{position:absolute;left:0;right:0;text-align:center;top:1625px;font:500 28px DM;letter-spacing:4px;color:#97606F;opacity:0}`;
const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
(async () => {
  const [file, solo, outDir] = process.argv.slice(2);
  const voci = JSON.parse(fs.readFileSync(file, 'utf8')).voci.filter(v => !solo || v.data === solo);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const v of voci) {
    const lines = v.frase.split('\n'), ex = (v.esempio || '').split('\n').filter(Boolean);
    const html = `<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="background:${v.sfondo}">
<svg class="d" viewBox="0 0 1080 1920" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path id="dn" d="${DONNA}" stroke="#C99AA6" stroke-width="5" opacity=".85"/><path id="fi" d="${FILO}" stroke="#97606F" stroke-width="7"/></svg>
<div class="lab">${esc(v.parola)}<small>il vocabolario di Serena · n. ${esc(v.numero)}</small></div>
<div class="g">${esc(v.categoria || '')}</div>
<div class="f">${lines.map(l => `<div class="l">${esc(l)}</div>`).join('')}${ex.length ? `<div class="e"><b>esempio</b>${ex.map(l => `<div>${esc(l)}</div>`).join('')}</div>` : ''}</div>
<div class="s">serenainmente</div></div>`;
    await p.setContent(html); await p.evaluate(() => document.fonts.ready);
    // controllo: nessuna riga oltre 860 px, il testo finisce sopra il filo
    const chk = await p.evaluate(() => { const f = document.querySelector('.f'); const w = Math.max(...[...f.querySelectorAll('.l, .e div')].map(l => l.scrollWidth)); return { w, bottom: f.getBoundingClientRect().bottom }; });
    if (chk.w > 860 || chk.bottom > 1140) throw new Error(`${v.data}: testo troppo largo o lungo ${JSON.stringify(chk)}`);
    const tl = 0.5 + lines.length * 0.8, te = tl + 0.3, tx = te + (ex.length ? 1.6 : 0);
    const tf = tx + 0.2, DUR = Math.ceil(tf + 4.6 + 0.8 + 2.0), N = FPS * DUR;
    const dir = fs.mkdtempSync('/tmp/voc2-');
    for (let i = 0; i < N; i++) {
      const t = i / FPS;
      await p.evaluate(({ t, te, tf }) => {
        const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
        const inout = t => t < 0 ? 0 : t > 1 ? 1 : t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        document.querySelectorAll('.l').forEach((el, k) => { const q = ease((t - 0.5 - k * 0.8) / 0.8); el.style.opacity = q; el.style.transform = `translateY(${16 * (1 - q)}px)`; });
        const e = document.querySelector('.e'); if (e) e.style.opacity = ease((t - te) / 0.8);
        const fi = document.getElementById('fi'), dn = document.getElementById('dn'), Lf = fi.getTotalLength(), Ld = dn.getTotalLength();
        const q = (t - tf) / 4.6, k = q < 0 ? 0 : q > 1 ? 1 : (q < .8 ? q / .8 * .9 : .9 + .1 * ease((q - .8) / .2)); // una sola penna: velocità costante, rallenta alla fine
        const L = (Lf + Ld) * k; fi.style.strokeDasharray = Lf; fi.style.strokeDashoffset = Lf - Math.min(L, Lf);
        dn.style.strokeDasharray = Ld; dn.style.strokeDashoffset = Ld - Math.max(0, L - Lf);
        document.querySelector('.s').style.opacity = ease((t - tf - 4.6) / 0.6);
      }, { t, te, tf });
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
