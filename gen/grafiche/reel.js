// Reel di Serena: frase che appare riga per riga, filo che si disegna. 1080x1920, 30 fps.
// Uso: node reel.js '{"frase":"...","sfondo":"#F4E9EC","file":"out.mp4"}'
// Con più di 4 righe (mini-racconto) il testo diventa più piccolo, resta con le maiuscole e sta sopra il filo; usare "durata":12-15.
const fs=require('fs');const path=require('path');const {execSync}=require('child_process');const { chromium } = require('playwright-core');
const FONTS=path.join(__dirname,'..','..','assets','fonts');const f64=n=>'data:font/woff2;base64,'+fs.readFileSync(path.join(FONTS,n)).toString('base64');
const it=JSON.parse(process.argv[2]);const FPS=30,DUR=it.durata||8,N=FPS*DUR;
const lines=it.frase.split('\n');const lungo=lines.length>4;
const html=`<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:Fr;src:url(${f64('fraunces-latin-400-normal.woff2')})}@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
body{margin:0}.c{width:1080px;height:1920px;background:${it.sfondo||'#F4E9EC'};position:relative;overflow:hidden;font-family:Fr;color:#3A2C30}
.f{position:absolute;left:120px;right:120px;top:0;height:1920px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:10px;text-align:center;font-size:72px;line-height:1.3;text-transform:lowercase;padding-bottom:120px}
.l{opacity:0;transform:translateY(18px)}
.t{position:absolute;left:0;top:1230px;width:1080px}
.t path{stroke-dasharray:600;stroke-dashoffset:600}.t circle{opacity:0}
.s{position:absolute;left:0;right:0;top:1560px;text-align:center;font:500 28px DM;letter-spacing:4px;color:#97606F;opacity:0}
${lungo?'.f{top:260px;height:940px;font-size:58px;line-height:1.25;gap:14px;text-transform:none;padding-bottom:0;left:90px;right:90px}':''}
</style><div class="c"><div class="f">${lines.map(l=>`<div class="l">${l.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</div>`).join('')}</div>
<svg class="t" viewBox="0 0 1080 200"><path d="M 300 128 C 380 128 400 62 470 62 C 540 62 552 138 620 138 C 690 138 700 84 760 84" fill="none" stroke="#97606F" stroke-width="7" stroke-linecap="round"/><circle cx="792" cy="84" r="9" fill="#C99AA6"/></svg><div class="s">serenainmente</div></div>
<script>
const ease=t=>t<0?0:t>1?1:1-Math.pow(1-t,3);
window.frame=(t)=>{ // t in secondi
  document.querySelectorAll('.l').forEach((el,i)=>{const p=ease((t-0.5-i*0.9)/0.9);el.style.opacity=p;el.style.transform='translateY('+(18*(1-p))+'px)'});
  const tf=0.5+${lines.length}*0.9+0.2; const p=ease((t-tf)/1.2);
  document.querySelector('.t path').style.strokeDashoffset=600*(1-p);
  document.querySelector('.t circle').style.opacity=ease((t-tf-1.1)/0.4);
  document.querySelector('.s').style.opacity=ease((t-tf-1.3)/0.6);
};
</script>`;
(async()=>{const dir=fs.mkdtempSync('/tmp/reel-');const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p=await b.newPage({viewport:{width:1080,height:1920}});await p.setContent(html);await p.evaluate(()=>document.fonts.ready);
for(let i=0;i<N;i++){await p.evaluate(t=>window.frame(t),i/FPS);await p.screenshot({path:`${dir}/${String(i).padStart(4,'0')}.jpg`,type:'jpeg',quality:92});}
await b.close();
execSync(`ffmpeg -y -loglevel error -framerate ${FPS} -i ${dir}/%04d.jpg -c:v libx264 -pix_fmt yuv420p -profile:v high -crf 20 -movflags +faststart "${it.file}"`);
fs.rmSync(dir,{recursive:true});console.log('ok',it.file);})();
