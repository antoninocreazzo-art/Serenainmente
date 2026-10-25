// Storie del giorno (1080x1920), una per data: img/AAAA-MM-GG-storia.jpg
// Uso: cd gen/grafiche && node storie-giorno.js post/piano-AAAA-MM-GG.json
// Due tipi, alternati (decisione di Antonino del 25/10/2026):
//  - "post": riprende il post delle 10 con un aggancio e l'anteprima della sua copertina (img/AAAA-MM-GG-1g.jpg, altrimenti -1.jpg).
//  - "strumento" / "guida": uno strumento o una guida del sito, con l'anteprima e «Link in bio».
// Zona sicura di Instagram: niente testo nei primi 250 px e negli ultimi 260 px.
const fs=require('fs'),path=require('path'),{chromium}=require('playwright-core');
const ROOT=path.join(__dirname,'..','..'),FONTS=path.join(ROOT,'assets','fonts');
const f64=f=>'data:font/woff2;base64,'+fs.readFileSync(path.join(FONTS,f)).toString('base64');
const img64=f=>{const ext=path.extname(f).slice(1).replace('jpg','jpeg');return `data:image/${ext};base64,`+fs.readFileSync(path.join(ROOT,f)).toString('base64')};
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const css=`@font-face{font-family:Fraunces;src:url(${f64('fraunces-latin-400-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
@font-face{font-family:'DM Sans';font-weight:400;src:url(${f64('dm-sans-latin-400-normal.woff2')})}
*{margin:0;padding:0;box-sizing:border-box}
.c{width:1080px;height:1920px;display:flex;flex-direction:column;padding:250px 80px 260px;color:#3A2C30;background:var(--bg)}
.chip{align-self:flex-start;font:500 26px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#7F4E5C;background:#fff9;padding:12px 26px;border-radius:999px}
h1{font:400 84px/1.06 Fraunces,serif;margin-top:36px}
p{font:400 36px/1.4 'DM Sans';margin-top:26px;color:#5B4A4F}
.mid{flex:1;display:flex;align-items:center;justify-content:center;min-height:0;padding:44px 0 40px}
.thumb{max-height:100%;max-width:78%;border-radius:26px;box-shadow:0 34px 70px -28px rgba(58,44,48,.5);transform:rotate(-2deg)}
.card{background:#fff;border-radius:32px;overflow:hidden;box-shadow:0 34px 70px -28px rgba(58,44,48,.5);width:86%;max-height:100%;display:flex;flex-direction:column}
.card img{width:100%;aspect-ratio:3/2;object-fit:cover;display:block}
.card .k{font:500 22px 'DM Sans';letter-spacing:.1em;text-transform:uppercase;color:#97606F;padding:30px 36px 0}
.card .t{font:400 46px/1.12 Fraunces;padding:12px 36px 34px}
.f{display:flex;align-items:center;justify-content:space-between;font:500 30px 'DM Sans';color:#97606F}
.f .g{background:#97606F;color:#fff;padding:16px 30px;border-radius:999px;font-size:28px}`;
const piano=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const copertina=d=>['-1g.jpg','-1.jpg'].map(s=>`img/${d}${s}`).find(f=>fs.existsSync(path.join(ROOT,f)));
const corpo=s=>{
  let mid='',pill='Link in bio';
  if(s.tipo==='post'){const c=copertina(s.data);if(!c)throw new Error('manca la copertina del post '+s.data);mid=`<img class="thumb" src="${img64(c)}">`;pill='Il post è sul profilo'}
  else if(s.tipo==='guida'){mid=`<div class="card"><img src="${img64(s.immagine)}"><div class="k">Guida gratuita, con le fonti</div><div class="t">${esc(s.card)}</div></div>`}
  else{mid=`<img class="thumb" src="${img64(s.immagine)}">`}
  return `<span class="chip">${esc(s.chip)}</span><h1>${esc(s.titolo)}</h1><p>${esc(s.testo)}</p><div class="mid">${mid}</div><div class="f"><span>serenainmente.it</span><span class="g">${pill}</span></div>`;
};
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});const p=await b.newPage({viewport:{width:1080,height:1920}});
for(const s of piano.storie){await p.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div class="c" style="--bg:${s.sfondo}">${corpo(s)}</div>`);
await p.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})))});
const over=await p.evaluate(()=>{const c=document.querySelector('.c');return c.scrollHeight>c.clientHeight+1});
const out=path.join(ROOT,'img',`${s.data}-storia.jpg`);await p.screenshot({path:out,type:'jpeg',quality:88});console.log(over?'ATTENZIONE troppo alto':'ok',path.basename(out))}
await b.close()})();
