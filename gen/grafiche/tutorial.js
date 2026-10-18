// Video tutorial del gestionale di famiglia: 1080x1920, 25 fps, senza audio.
// Uso: node tutorial.js ../../video/gestionale-tutorial.mp4
// I dati mostrati sono le righe di esempio del file (scarica/gestionale-di-famiglia.xlsx).
const fs = require('fs'), path = require('path'), { execSync } = require('child_process'), { chromium } = require('playwright-core');
const A = path.join(__dirname, '..', '..', 'assets');
const f64 = n => 'data:font/woff2;base64,' + fs.readFileSync(path.join(A, 'fonts', n)).toString('base64');
const i64 = n => 'data:image/' + (n.endsWith('png') ? 'png' : 'webp') + ';base64,' + fs.readFileSync(path.join(A, n)).toString('base64');
const OUT = process.argv[2] || 'tutorial.mp4', FPS = 25;
const D = JSON.parse(process.argv[3] || '{}'); // date di esempio passate dal generatore (facoltative)
const v1 = D.v1 || '24/10/2026', d1 = D.d1 || '22/10/2026', r0 = D.r0 || '08/09/2026', r1 = D.r1 || '08/11/2026';

// scene: [inizio, fine] in secondi
const S = [[0, 4], [4, 11.5], [11.5, 19.5], [19.5, 27], [27, 35], [35, 41], [41, 45.5]];
const DUR = S[S.length - 1][1];

const sheet = (title, head, rows, widths) => `<div class="win"><div class="bar"><i class="fi"><b></b><b></b><b></b><b></b></i>gestionale-di-famiglia.xlsx</div>
<div class="tt">${title}</div><table><colgroup>${widths.map(w => `<col style="width:${w}%">`).join('')}</colgroup>
<tr>${head.map(h => `<th>${h}</th>`).join('')}</tr>${rows.join('')}</table></div>`;
const row = (at, cells, hl = []) => `<tr class="ap" data-at="${at}">${cells.map((c, i) => `<td${hl[i] ? ` class="hl" data-hl="${hl[i]}"` : ''}>${c}</td>`).join('')}</tr>`;
const cap = (n, t, s, extra = '') => `<div class="cap"><span class="n">${n}</span><h1>${t}</h1><p>${s}</p>${extra}</div>`;

const scenes = [
  `<div class="intro"><img src="${i64('brand/avatar-320.png')}" class="ap" data-at="0.2"><h1 class="ap" data-at="0.5">Il gestionale<br>di famiglia</h1><p class="ap" data-at="1.1">Come si usa, in un minuto</p></div>`,
  cap('1', 'Scrivi i nomi di casa', 'Scheda <b>Famiglia</b>: una volta sola. Poi li ritrovi nei menu di tutte le altre schede.') +
  sheet('La tua famiglia', ['Nome', 'Ruolo', 'Nato il', 'Età'], [
    row(1.0, ['Sofia', 'Figlio/a', '14/03/2024', '2 anni'], [0, 0, 0, 1.6]),
    row(1.9, ['Luca', 'Papà', '02/09/1990', '36 anni'], [0, 0, 0, 2.5]),
    row(2.8, ['Anna', 'Mamma', '21/05/1992', '34 anni'], [0, 0, 0, 3.4]),
  ], [26, 24, 28, 22]) +
  `<div class="menu ap" data-at="4.3"><div class="mt">Per chi</div><div>Sofia</div><div>Luca</div><div>Anna</div></div>`,
  cap('2', 'Aggiungi una visita', 'Data, per chi e dove. <b>«Disdire entro»</b> si calcola da solo: due giorni lavorativi prima.') +
  sheet('Visite', ['Data', 'Per chi', 'Dove', 'Disdire entro'], [
    row(1.0, [v1, 'Sofia', 'Dott.ssa Rossi', `<span class="ap" data-at="2.2">${d1}</span>`], [0, 0, 0, 2.4]),
  ], [24, 20, 30, 26]) +
  `<div class="note ap" data-at="4.2">Se la tua struttura dice diverso, scrivi la data nella colonna accanto.</div>` +
  `<div class="note ap" data-at="5.6">Fatta la visita, segna <b>«Completata»</b>: esce dagli impegni.</div>`,
  cap('3', 'Le cose che si ripetono', 'Retta, rinnovi, controlli: scegli <b>«Ogni mese»</b> o <b>«Ogni anno»</b> e la data si sposta da sola.') +
  sheet('Scadenze', ['Cosa', 'Si ripete', 'Prossima volta'], [
    row(1.0, ['Retta del nido', 'Ogni mese', `<span class="ap" data-at="2.3">${r1}</span>`], [0, 1.8, 2.5]),
    row(3.2, ['Richiamo vaccino', 'Mai', r1], [0, 0, 0]),
  ], [42, 26, 32]) +
  `<div class="note ap" data-at="4.4">Chiusa? Spunta <b>«Fatto»</b> e sparisce dai promemoria.</div>`,
  cap('4', 'Apri «Inizia da qui»', 'Ogni volta che apri il file vedi cosa arriva, entro quando e per chi.') +
  `<div class="win dash"><div class="bar"><i class="fi"><b></b><b></b><b></b><b></b></i>Inizia da qui</div>
  <div class="hi ap" data-at="0.6">Buongiorno!</div>
  <div class="k ap" data-at="1.0" style="background:#F4E9EC"><b style="color:#97606F">2</b>scadenze nei prossimi 30 giorni</div>
  <div class="k ap" data-at="1.4" style="background:#E8EDE4"><b style="color:#4D5A48">2</b>visite nelle prossime due settimane</div>
  <div class="k ap" data-at="1.8" style="background:#EFE6DC"><b style="color:#6B5644">1</b>documento da rinnovare</div>
  <div class="lt ap" data-at="2.6">Prossimi impegni</div>
  <div class="li ap" data-at="3.0"><span>${v1.slice(0, 5)}</span>Visita · Dott.ssa Rossi<em>Sofia · tra 6 giorni</em></div>
  <div class="li ap" data-at="3.4"><span>${r1.slice(0, 5)}</span>Retta del nido<em>Sofia · tra 21 giorni</em></div>
  <div class="li ap" data-at="3.8"><span>27/11</span>Rinnovo · Carta d'identità<em>Luca · tra 40 giorni</em></div></div>`,
  cap('5', 'Dal telefono', 'Sul sito tocca <b>«Apri in Fogli Google»</b>, poi <b>«Crea una copia»</b>. Il file è tuo, nel tuo Drive.') +
  `<div class="phone ap" data-at="0.8"><img src="${i64('gestionale/inizia-telefono.webp')}"></div>`,
  `<div class="intro end"><p class="ap" data-at="0.2">Gratuito, senza registrazione.<br>I tuoi dati restano tuoi.</p><h1 class="ap" data-at="0.8">serenainmente.it<br><span>/gestionale</span></h1><img src="${i64('brand/avatar-320.png')}" class="ap" data-at="1.4"></div>`,
];

const html = `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:Fr;src:url(${f64('fraunces-latin-400-normal.woff2')})}@font-face{font-family:Fr;font-weight:600;src:url(${f64('fraunces-latin-600-normal.woff2')})}
@font-face{font-family:DM;src:url(${f64('dm-sans-latin-400-normal.woff2')})}@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
*{box-sizing:border-box;margin:0;padding:0}body{width:1080px;height:1920px;overflow:hidden}
.st{position:absolute;inset:0;background:#F8F4EF;color:#3A2C30;font-family:DM;padding:150px 80px 0;display:flex;flex-direction:column;gap:56px;opacity:0}
.cap{display:flex;flex-direction:column;gap:22px}.cap .n{width:84px;height:84px;border-radius:50%;background:#97606F;color:#fff;display:grid;place-items:center;font:600 44px Fr}
.cap h1{font:600 76px/1.08 Fr}.cap p{font-size:40px;line-height:1.38;color:#5E4A4F}.cap b{color:#97606F;font-weight:500}
.win{background:#fff;border-radius:28px;box-shadow:0 30px 60px -30px rgba(58,44,48,.35);overflow:hidden;border:1px solid #EADCDF}
.bar{display:flex;align-items:center;gap:16px;height:72px;padding:0 28px;border-bottom:1px solid #EFE6E8;font-size:28px;color:#6E5C60}
.fi{width:36px;height:36px;border-radius:8px;background:#62705C;display:grid;grid-template-columns:1fr 1fr;gap:3px;padding:7px}.fi b{background:rgba(255,255,255,.85);border-radius:2px}
.tt{font:600 40px Fr;padding:26px 28px 14px}
table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:31px}th{background:#97606F;color:#fff;font-weight:500;text-align:left;padding:18px 20px;font-size:27px}
td{padding:22px 20px;border-bottom:1px solid #EADCDF;color:#2B2BD9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}td:last-child{color:#3A2C30}
td.hl{transition:none}
.menu{align-self:flex-start;margin:-30px 0 0 40px;background:#fff;border-radius:18px;box-shadow:0 20px 40px -18px rgba(58,44,48,.4);border:1px solid #EADCDF;font-size:32px;min-width:330px}
.menu div{padding:18px 26px;border-bottom:1px solid #F3EAEC}.menu .mt{font-size:24px;color:#97606F;font-weight:500;letter-spacing:1px;text-transform:uppercase}
.note{background:#E8EDE4;border-radius:22px;padding:28px 32px;font-size:34px;line-height:1.4;color:#3A2C30;margin-top:-20px}.note b{color:#4D5A48;font-weight:500}
.dash{padding-bottom:20px}.dash .hi{font:400 46px Fr;color:#97606F;padding:26px 30px 16px}
.k{display:flex;align-items:center;gap:26px;margin:0 24px 10px;border-radius:16px;padding:16px 22px;font-size:30px}.k b{font:600 54px Fr;width:60px;text-align:center}
.lt{font:600 36px Fr;padding:22px 30px 8px}.li{display:grid;grid-template-columns:110px 1fr;gap:2px 16px;padding:16px 30px;border-bottom:1px solid #F0E4E7;font-size:30px}
.li span{color:#97606F;font-weight:500;grid-row:span 2}.li em{font-style:normal;color:#7A6569;font-size:25px}
.phone{align-self:center;width:520px;background:#2F2A2C;border-radius:64px;padding:18px;box-shadow:0 40px 70px -30px rgba(0,0,0,.5)}.phone img{width:100%;border-radius:48px;display:block}
.intro{height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px;text-align:center;padding-bottom:200px}
.intro img{width:240px;height:240px;border-radius:50%}.intro h1{font:600 104px/1.05 Fr}.intro p{font-size:42px;color:#6E5C60;line-height:1.4}
.end h1{font-size:84px;color:#97606F}.end h1 span{color:#3A2C30}
.foot{position:absolute;left:0;right:0;bottom:90px;text-align:center;font:500 28px DM;letter-spacing:5px;color:#97606F}
.dots{position:absolute;left:0;right:0;bottom:150px;display:flex;justify-content:center;gap:14px}.dots i{width:14px;height:14px;border-radius:50%;background:#E3D6CF}.dots i.on{background:#97606F;width:40px;border-radius:8px}
</style>
${scenes.map((s, i) => `<div class="st" id="s${i}">${s}</div>`).join('')}
<div class="dots">${S.slice(1, -1).map(() => '<i></i>').join('')}</div><div class="foot">serenainmente</div>
<script>
const S=${JSON.stringify(S)};const ease=t=>t<0?0:t>1?1:1-Math.pow(1-t,3);
window.frame=t=>{S.forEach(([a,b],i)=>{const el=document.getElementById('s'+i);const lt=t-a;
  const o=Math.min(ease(lt/0.5), i===S.length-1?1:ease((b-t)/0.5));el.style.opacity=(t>=a&&t<=b)?o:0;
  el.querySelectorAll('.ap').forEach(x=>{const p=ease((lt-parseFloat(x.dataset.at))/0.6);x.style.opacity=p;x.style.transform='translateY('+(26*(1-p))+'px)'});
  el.querySelectorAll('[data-hl]').forEach(x=>{const q=lt-parseFloat(x.dataset.hl);const h=q<0?0:q<0.4?q/0.4:q<1.6?1:Math.max(0,1-(q-1.6)/0.8);
    x.style.background='rgba(255,236,170,'+(0.9*h)+')';x.style.color=h>0.2?'#7A5A00':''});});
  const cur=S.findIndex(([a,b])=>t>=a&&t<b);document.querySelectorAll('.dots i').forEach((d,j)=>d.className=(j===cur-1)?'on':'');
  document.querySelector('.dots').style.opacity=(cur>0&&cur<S.length-1)?1:0;};
</script>`;

(async () => {
  const dir = fs.mkdtempSync('/tmp/tut-');
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.setContent(html); await p.evaluate(() => document.fonts.ready);
  const N = Math.round(DUR * FPS), only = process.env.FRAMES ? process.env.FRAMES.split(',').map(Number) : null;
  for (let i = 0; i < N; i++) {
    if (only && !only.includes(i)) continue;
    await p.evaluate(t => window.frame(t), i / FPS);
    await p.screenshot({ path: `${dir}/${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 90 });
  }
  await b.close();
  if (only) { for (const f of fs.readdirSync(dir)) fs.copyFileSync(`${dir}/${f}`, `${path.dirname(OUT)}/${f}`); console.log('frames', dir); return; }
  execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/%05d.jpg -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 23 -movflags +faststart "${OUT}"`);
  execSync(`ffmpeg -y -loglevel error -ss 30 -i "${OUT}" -frames:v 1 -q:v 3 "${OUT.replace(/\.mp4$/, '.jpg')}"`);
  fs.rmSync(dir, { recursive: true }); console.log('ok', OUT);
})();
