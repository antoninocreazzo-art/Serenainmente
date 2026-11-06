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
// il filo di sempre; poi il filo si scioglie e al suo posto si disegna la donna (35-40 anni, capelli alle spalle, occhi chiusi),
// quasi a tutta pagina, di profilo verso destra: la linea parte dalla radice del naso e va in due direzioni (SU: fronte, capelli; GIU: naso, labbra, mento, collo, spalle)
const FILO = 'M 300 1418 C 380 1418 400 1352 470 1352 C 540 1352 552 1428 620 1428 C 690 1428 700 1374 760 1374';
const SU = 'M 881 1154 C 882 1148 884 1130 884 1116 C 885 1102 886 1092 886 1071 C 885 1050 885 1019 880 992 C 875 964 869 933 854 907 C 838 882 819 860 787 838 C 755 816 712 788 660 777 C 607 766 534 760 471 771 C 408 783 333 800 282 846 C 232 893 191 975 166 1050 C 142 1124 137 1221 135 1296 C 132 1371 150 1436 152 1499 C 154 1562 142 1618 145 1673 C 147 1728 151 1804 166 1827 C 182 1850 215 1812 239 1811 C 263 1810 287 1813 312 1821 C 336 1829 372 1851 384 1857';
const GIU = 'M 881 1154 C 885 1163 895 1189 903 1206 C 912 1223 923 1241 932 1255 C 941 1270 951 1283 955 1293 C 960 1303 962 1310 960 1316 C 957 1323 949 1327 941 1331 C 932 1335 916 1337 909 1340 C 902 1342 898 1344 897 1348 C 897 1353 900 1361 905 1367 C 909 1373 921 1381 923 1386 C 926 1391 925 1396 920 1399 C 916 1402 895 1402 894 1406 C 894 1410 913 1416 918 1422 C 922 1428 923 1436 920 1442 C 918 1448 911 1453 905 1458 C 898 1463 881 1463 880 1473 C 879 1483 896 1505 899 1521 C 901 1536 902 1552 896 1566 C 889 1579 878 1591 860 1600 C 841 1610 805 1610 787 1621 C 769 1632 759 1644 754 1667 C 748 1690 754 1732 755 1760 C 757 1788 775 1814 764 1835 C 753 1857 730 1877 688 1890 C 647 1904 580 1914 514 1917 C 449 1919 372 1902 297 1905 C 222 1908 138 1925 65 1937 C -8 1949 -104 1971 -138 1978';
const DETTAGLI = 'M 854 907 C 836 917 781 936 746 965 C 712 994 672 1041 645 1081 C 618 1122 594 1185 584 1206 M 584 1206 C 573 1238 534 1334 517 1398 C 501 1461 498 1518 486 1586 C 473 1654 449 1767 442 1804 M 572 1247 C 566 1250 541 1254 532 1267 C 523 1280 519 1307 520 1325 C 522 1343 533 1367 541 1377 C 548 1387 562 1384 567 1386 M 860 1600 C 838 1598 772 1598 732 1586 C 692 1574 646 1555 619 1528 C 591 1501 575 1443 567 1426 M 857 1108 C 849 1105 831 1092 813 1090 C 796 1088 762 1094 752 1094 M 845 1180 C 839 1183 823 1195 810 1196 C 797 1196 774 1185 767 1183 M 831 1189 C 832 1192 835 1203 836 1206 M 810 1196 C 811 1199 812 1210 812 1213 M 790 1193 C 790 1196 788 1208 787 1210 M 919 1400 C 917 1401 910 1404 906 1405 C 902 1406 895 1406 893 1406';
const css = `@font-face{font-family:Fr;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:DM;font-weight:800;src:url(${f64('dm-sans-latin-800-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}body{margin:0}
.c{width:1080px;height:1920px;position:relative;overflow:hidden;color:#3A2C30}
svg.d{position:absolute;left:0;top:0;width:1080px;height:1920px}
#fw{position:absolute;left:0;width:1080px}
.lab{position:absolute;left:130px;top:290px;padding:22px 40px;background:#EBD3D9;font:800 58px DM;letter-spacing:7px;text-transform:uppercase}
.lab small{display:block;font:500 24px DM;letter-spacing:2px;color:#97606F;text-transform:none;margin-top:8px}
.g{position:absolute;left:130px;top:505px;font:500 28px DM;letter-spacing:2px;color:#97606F}
.f{position:absolute;left:130px;width:860px;top:560px;font-family:Fr;font-size:54px;line-height:1.34}
.l{opacity:0;transform:translateY(16px);white-space:nowrap}
.e{margin-top:42px;opacity:0}
.e b{display:block;font:500 24px DM;letter-spacing:3px;text-transform:uppercase;color:#97606F;margin-bottom:6px}
.e div{font-family:Fr;font-size:42px;line-height:1.3;color:#6E4552;white-space:nowrap}
.s{position:absolute;left:130px;top:1560px;font:500 28px DM;letter-spacing:4px;color:#97606F;opacity:0}`;
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
<path id="su" d="${SU}" stroke="#C99AA6" stroke-width="4.5" opacity=".7"/><path id="gi" d="${GIU}" stroke="#C99AA6" stroke-width="4.5" opacity=".7"/>
<path id="dt" d="${DETTAGLI}" stroke="#C99AA6" stroke-width="3.5" opacity="0"/></svg>
<svg id="fw" viewBox="0 1300 1080 200" fill="none" stroke-linecap="round"><path id="fi" d="${FILO}" stroke="#97606F" stroke-width="7"/></svg>
<div class="lab">${esc(v.parola)}<small>il vocabolario di Serena · n. ${esc(v.numero)}</small></div>
<div class="g">${esc(v.categoria || '')}</div>
<div class="f">${lines.map(l => `<div class="l">${esc(l)}</div>`).join('')}${ex.length ? `<div class="e"><b>esempio</b>${ex.map(l => `<div>${esc(l)}</div>`).join('')}</div>` : ''}</div>
<div class="s">serenainmente</div></div>`;
    await p.setContent(html); await p.evaluate(() => document.fonts.ready);
    await p.evaluate(() => { document.getElementById('fw').style.top = (document.querySelector('.f').getBoundingClientRect().bottom + 10) + 'px'; });
    // controllo: nessuna riga oltre 860 px, il testo finisce sopra il filo
    const chk = await p.evaluate(() => { const f = document.querySelector('.f'); const w = Math.max(...[...f.querySelectorAll('.l, .e div')].map(l => l.scrollWidth)); return { w, bottom: f.getBoundingClientRect().bottom }; });
    if (chk.w > 860 || chk.bottom > 1140) throw new Error(`${v.data}: testo troppo largo o lungo ${JSON.stringify(chk)}`);
    const tl = 0.5 + lines.length * 0.8, te = tl + 0.3, tx = te + (ex.length ? 1.6 : 0);
    const tf = tx + 0.2, td = tf + 1.2, DUR = Math.ceil(td + 3.2 + 1.0 + 2.0), N = FPS * DUR;
    const dir = fs.mkdtempSync('/tmp/voc2-');
    for (let i = 0; i < N; i++) {
      const t = i / FPS;
      await p.evaluate(({ t, te, tf, td }) => {
        const ease = t => t < 0 ? 0 : t > 1 ? 1 : 1 - Math.pow(1 - t, 3);
        const inout = t => t < 0 ? 0 : t > 1 ? 1 : t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        document.querySelectorAll('.l').forEach((el, k) => { const q = ease((t - 0.5 - k * 0.8) / 0.8); el.style.opacity = q; el.style.transform = `translateY(${16 * (1 - q)}px)`; });
        const e = document.querySelector('.e'); if (e) e.style.opacity = ease((t - te) / 0.8);
        const fi = document.getElementById('fi'), Lf = fi.getTotalLength(); fi.style.strokeDasharray = Lf; fi.style.strokeDashoffset = Lf * (1 - inout((t - tf) / 1.2));
        document.getElementById('fw').style.opacity = 1 - ease((t - td - 0.2) / 1.0);
        for (const id of ['su', 'gi']) { const q = document.getElementById(id), L = q.getTotalLength(); q.style.strokeDasharray = L; q.style.strokeDashoffset = L * (1 - inout((t - td) / 3.2)); }
        document.getElementById('dt').style.opacity = 0.7 * ease((t - td - 3.0) / 0.7);
        document.querySelector('.s').style.opacity = ease((t - td - 3.4) / 0.6);
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
