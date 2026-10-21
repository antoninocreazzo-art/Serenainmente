// Stampabili gratuiti di serenainmente.it (PDF A4), generati in locale.
// Uso: cd gen/grafiche && node stampabili.js   → scrive i PDF in ../../scarica/
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright-core');

const ROOT = path.join(__dirname, '..', '..');
const FONTS = path.join(ROOT, 'assets', 'fonts');
const f64 = f => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, f)).toString('base64');
const EXE = process.env.CHROME_PATH || '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const LOGO = fs.readFileSync(path.join(ROOT, 'assets', 'brand', 'profilo-serena-senza-s.svg'), 'utf8')
  .replace(/width="1080" height="1080"/, 'width="40" height="40"');

const css = `
@font-face{font-family:Fraunces;font-weight:400;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:Fraunces;font-weight:600;src:url(${f64('fraunces-latin-600-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:400;src:url(${f64('dm-sans-latin-400-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
html,body{font-family:'DM Sans',Arial,sans-serif;color:#3A2C30;font-size:10.5pt}
.pg{display:flex;flex-direction:column;height:100%}
.hd{display:flex;align-items:center;gap:10px;border-bottom:1.5px solid #97606F;padding-bottom:8px;margin-bottom:12px}
.hd h1{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:21pt;line-height:1.1}
.hd p{color:#6E5C60;font-size:9.5pt;margin-top:2px}
.hd .t{flex:1}
h2{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:12.5pt;color:#7F4E5C;margin:12px 0 6px}
.lab{font-size:8.5pt;color:#6E5C60;text-transform:uppercase;letter-spacing:.06em}
.ln{border-bottom:1px solid #C99AA6;height:22px}
.fld{display:flex;gap:14px}.fld>div{flex:1}
table{width:100%;border-collapse:collapse;table-layout:fixed}
th{background:#F4E9EC;color:#7F4E5C;font-weight:500;font-size:9pt;text-align:left;padding:6px 6px;border:1px solid #E7DCD6}
td{border:1px solid #E7DCD6;height:30px;vertical-align:top;padding:4px 6px;font-size:9pt;color:#6E5C60}
.box{background:#FBF6F4;border:1px solid #E7DCD6;border-radius:8px;padding:9px 12px}
.ck{list-style:none}.ck li{display:flex;gap:8px;align-items:center;margin:4px 0}
.ck li:before{content:"";width:11px;height:11px;border:1.3px solid #97606F;border-radius:3px;flex:none}
.q{display:flex;gap:8px;align-items:flex-end;margin:6px 0}.q b{font-family:Fraunces,Georgia,serif;color:#97606F;width:14px}.q .ln{flex:1}
.ft{margin-top:auto;padding-top:10px;display:flex;justify-content:space-between;font-size:8pt;color:#6E5C60;border-top:1px solid #E7DCD6}
.ft b{color:#97606F;font-weight:500}
.note{font-size:8.5pt;color:#6E5C60;margin-top:8px;line-height:1.4}
.when{display:flex;gap:6px;font-size:8pt}.when span{display:flex;align-items:center;gap:3px}
.when span:before{content:"";width:9px;height:9px;border:1px solid #97606F;border-radius:2px}
`;

const head = (t, s) => `<div class="hd">${LOGO}<div class="t"><h1>${t}</h1><p>${s}</p></div></div>`;
const foot = extra => `<div class="ft"><span>${extra}</span><span><b>serenainmente.it</b> · stampabile gratuito, per uso personale e familiare</span></div>`;
const lines = n => Array.from({ length: n }, () => '<div class="ln"></div>').join('');

const GIORNI = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica'];
const settimana = `<div class="pg">
${head('La settimana di tutti', 'Da attaccare al frigo la domenica sera: un solo foglio, così nessuno deve ricordare tutto da solo.')}
<div class="fld" style="margin-bottom:8px"><div><span class="lab">Settimana dal</span><div class="ln"></div></div><div><span class="lab">al</span><div class="ln"></div></div><div style="flex:2"><span class="lab">Chi c'è in casa questa settimana</span><div class="ln"></div></div></div>
<table><thead><tr><th style="width:15%"></th>${GIORNI.map(g => `<th>${g}</th>`).join('')}</tr></thead><tbody>
${['Chi va dove<br>(scuola, lavoro, sport)', 'Visite e appuntamenti', 'Chi accompagna,<br>chi va a prendere', 'Da preparare<br>o da portare', 'A tavola'].map(r => `<tr><th style="height:62px;vertical-align:top">${r}</th>${GIORNI.map(() => '<td></td>').join('')}</tr>`).join('')}
</tbody></table>
<div class="fld" style="margin-top:12px"><div class="box"><span class="lab">Questa settimana non dimenticare</span>${lines(3)}</div><div class="box"><span class="lab">Una cosa bella da fare insieme</span>${lines(3)}</div></div>
${foot('Si scrive a matita: le settimane cambiano, e va bene così.')}</div>`;

const pediatra = `<div class="pg">
${head('Prima della visita dal pediatra', 'Da compilare a casa, con calma. In ambulatorio i minuti volano: qui le domande non si perdono.')}
<div class="fld"><div><span class="lab">Bambino o bambina</span><div class="ln"></div></div><div><span class="lab">Data e ora della visita</span><div class="ln"></div></div><div><span class="lab">Medico</span><div class="ln"></div></div></div>
<h2>Perché andiamo</h2>${lines(2)}
<h2>Cosa ho notato</h2><p class="note" style="margin-top:0">Da quando, quante volte, cosa migliora o peggiora. Poche righe bastano.</p>${lines(4)}
<h2>Le mie domande, la più importante per prima</h2>
${[1, 2, 3, 4, 5].map(n => `<div class="q"><b>${n}</b><div class="ln"></div></div>`).join('')}
<h2>Cosa ha detto il medico</h2>
<div class="fld"><div><span class="lab">Cosa fare</span>${lines(3)}</div><div><span class="lab">Quando richiamare o tornare</span>${lines(3)}</div></div>
<div class="fld" style="margin-top:12px"><div class="box"><span class="lab">Da portare</span><ul class="ck"><li>Tessera sanitaria</li><li>Libretto pediatrico o delle vaccinazioni</li><li>Referti e lettere precedenti</li><li>Questo foglio e una penna</li></ul></div>
<div class="box"><span class="lab">Prima di uscire, so</span><ul class="ck"><li>cosa fare a casa</li><li>quando richiamare</li><li>se serve un controllo</li><li>come si chiama ciò che ha detto</li></ul></div></div>
<p class="note">Informazioni generali, non sostituiscono il parere del pediatra o del medico. La guida completa è su serenainmente.it/guide/domande-per-il-pediatra</p>
${foot('Se una parola non è chiara, chiedere di ripeterla è normale.')}</div>`;

const medicine = `<div class="pg">
${head('La lista delle medicine, scritta insieme', 'Da compilare con chi le prende, a quattro mani. Serve a ricordare, non a decidere: le scelte sulle terapie restano sue e del suo medico.')}
<div class="fld"><div style="flex:1.4"><span class="lab">Nome</span><div class="ln"></div></div><div><span class="lab">Medico di famiglia</span><div class="ln"></div></div><div><span class="lab">Telefono del medico</span><div class="ln"></div></div></div>
<div class="fld" style="margin-top:6px"><div><span class="lab">Allergie o medicine da evitare, se ce ne sono</span><div class="ln"></div></div><div><span class="lab">Farmacia di fiducia</span><div class="ln"></div></div></div>
<h2>Le medicine di ogni giorno</h2>
<table><thead><tr><th style="width:22%">Medicina</th><th style="width:17%">A cosa serve, in parole sue</th><th style="width:11%">Quanto</th><th style="width:28%">Quando</th><th style="width:10%">Fino a</th><th>Note</th></tr></thead><tbody>
${Array.from({ length: 7 }, () => `<tr><td></td><td></td><td></td><td><div class="when"><span>mattina</span><span>pranzo</span><span>sera</span><span>notte</span></div></td><td></td><td></td></tr>`).join('')}
</tbody></table>
<h2>Solo quando serve</h2>
<table><tbody>${Array.from({ length: 2 }, () => '<tr><td style="width:22%"></td><td></td></tr>').join('')}</tbody></table>
<div class="fld" style="margin-top:12px"><div class="box"><span class="lab">Domande da fare al medico alla prossima visita</span>${lines(2)}</div>
<div class="box"><span class="lab">Aggiornata il</span><div class="ln"></div><span class="lab" style="display:block;margin-top:6px">Scritta insieme da</span><div class="ln"></div></div></div>
<p class="note" style="margin-top:6px">Una copia in borsa o nel portafoglio, una sul frigo. Si porta a ogni visita e si aggiorna insieme quando il medico cambia qualcosa.</p>
${foot('Con chi ci ha insegnato tanto, si decide insieme.')}</div>`;

const DOCS = [
  { file: 'settimana-sul-frigo.pdf', html: settimana, landscape: true },
  { file: 'domande-per-il-pediatra.pdf', html: pediatra },
  { file: 'lista-delle-medicine.pdf', html: medicine, landscape: true },
];

(async () => {
  const b = await chromium.launch({ executablePath: EXE });
  const p = await b.newPage();
  for (const d of DOCS) {
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css} .pg{height:${d.landscape ? 186 : 273}mm}</style>${d.html}`);
    await p.evaluate(() => document.fonts.ready);
    const out = path.join(ROOT, 'scarica', d.file);
    await p.pdf({ path: out, format: 'A4', landscape: !!d.landscape, printBackground: true, margin: { top: '12mm', bottom: '10mm', left: '12mm', right: '12mm' } });
    console.log('ok', out);
  }
  await b.close();
})();
