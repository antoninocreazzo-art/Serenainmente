// Storie Instagram tipografiche (1080x1920): assets/pin/story-<chiave>.jpg
// Uso: cd gen/grafiche && node storie.js
const fs=require('fs'),path=require('path'),{chromium}=require('playwright-core');
const ROOT=path.join(__dirname,'..','..'),FONTS=path.join(ROOT,'assets','fonts');
const f64=f=>'data:font/woff2;base64,'+fs.readFileSync(path.join(FONTS,f)).toString('base64');
const LOGO=s=>fs.readFileSync(path.join(ROOT,'assets','brand','profilo-serena.svg'),'utf8').replace(/width="1080" height="1080"/,`width="${s}" height="${s}"`);
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const css=`@font-face{font-family:Fraunces;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:400;src:url(${f64('dm-sans-latin-400-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
.c{width:1080px;height:1920px;display:flex;flex-direction:column;padding:250px 80px 260px;color:#3A2C30;background:var(--bg)}
.chip{align-self:flex-start;font:500 26px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#7F4E5C;background:#fff9;padding:12px 26px;border-radius:999px}
h1{font:400 92px/1.06 Fraunces,serif;margin-top:40px}
p{font:400 38px/1.42 'DM Sans';margin-top:30px;color:#5B4A4F}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;gap:26px}
.logo{display:flex;justify-content:center}.logo svg{filter:drop-shadow(0 16px 36px rgba(126,74,90,.18))}
.li{background:#fffc;border-radius:28px;padding:30px 34px;font:400 36px/1.3 'DM Sans';color:#3A2C30;display:flex;gap:22px;align-items:flex-start}
.li b{font:400 40px Fraunces;color:#97606F;flex:none}
.card{background:#fff;border-radius:32px;padding:44px;box-shadow:0 30px 60px -30px rgba(58,44,48,.45)}
.card .k{font:500 24px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#97606F}
.card .t{font:400 54px/1.12 Fraunces;margin-top:16px}.card .d{font:400 32px/1.4 'DM Sans';color:#5B4A4F;margin-top:18px}
.f{display:flex;align-items:center;justify-content:space-between;font:500 30px 'DM Sans';color:#97606F}
.f .g{background:#97606F;color:#fff;padding:16px 30px;border-radius:999px;font-size:28px}
.tr{font:400 26px 'DM Sans';color:#7F4E5C;text-align:center;margin-bottom:26px}`;
const footer=(tr)=>`${tr?`<div class="tr">${tr}</div>`:''}<div class="f"><span>serenainmente.it</span><span class="g">Link in bio</span></div>`;
const S=[
 ['chi-sono-1','#F4E9EC',`<span class="chip">Piacere</span><h1>Ciao, sono Serena.</h1><p>Un posto per chi si prende cura della famiglia: figli, genitori, nonni. Cose pratiche, dette semplici.</p><div class="mid"><div class="logo">${LOGO(520)}</div></div>`+footer()],
 ['chi-sono-2','#FBF6F4',`<span class="chip">Cosa trovi qui</span><h1>Meno da ricordare, più tempo per voi.</h1><div class="mid">
<div class="li"><b>1</b><span>Guide pratiche: ogni dato con la sua fonte.</span></div>
<div class="li"><b>2</b><span>Strumenti e fogli da stampare, gratis e senza registrazione.</span></div>
<div class="li"><b>3</b><span>Parole per le giornate che pesano.</span></div></div>`+footer('Ideato e curato da una persona, con supporto AI')],
 ['guide','#F2EBE3',`<span class="chip">Le guide di Serena</span><h1>Le risposte che cerchi alle 23.</h1><div class="mid">
<div class="li"><b>·</b><span>Quanto dorme un bambino, età per età</span></div>
<div class="li"><b>·</b><span>Il certificato vaccinale: dove si scarica</span></div>
<div class="li"><b>·</b><span>Pediatra e medico di base: scegliere e cambiare</span></div>
<div class="li"><b>·</b><span>Spostare o disdire una visita, pagare il ticket</span></div></div>`+footer('Gratis, con le fonti, su serenainmente.it')],
 ['guida-sonno','#EBD3D9',`<span class="chip">Guida</span><div class="mid"><div class="card"><div class="k">Sonno</div><div class="t">Quanto dorme un bambino?</div><div class="d">Le ore di sonno età per età, con le fonti. E cosa conta davvero, più dei numeri.</div></div></div>`+footer()],
 ['guida-vaccinale','#F4E9EC',`<span class="chip">Guida</span><div class="mid"><div class="card"><div class="k">Documenti</div><div class="t">Il certificato vaccinale</div><div class="d">Dove si scarica, in pochi minuti, e quando serve davvero: nido, scuola, viaggi.</div></div></div>`+footer()],
];
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const [k,bg,body] of S){await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="--bg:${bg}">${body}</div>`);await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:path.join(ROOT,'assets','pin',`story-${k}.jpg`),type:'jpeg',quality:88});console.log('ok',k)}await b.close()})();
