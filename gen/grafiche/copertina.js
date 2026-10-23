// Copertina dei reel (1080x1920 JPG), da dare a Metricool come videoThumbnailUrl.
// Uso: node copertina.js '{"tipo":"testo","video":"../../video/AAAA-MM-GG-reel.mp4","file":"../../video/AAAA-MM-GG-reel-cover.jpg"}'
//      node copertina.js '{"tipo":"logo","sfondo":"#F2EBE3","file":"../../video/AAAA-MM-GG-reel-cover.jpg"}'
// tipo "testo": l'ultimo fotogramma del reel (frase completa con il filo). tipo "logo": il simbolo di Serena.
// I reel si alternano: uno "testo", uno "logo" (l'ultimo usato è scritto in registro-post.md).
const fs=require('fs');const path=require('path');const {execSync}=require('child_process');const { chromium } = require('playwright-core');
const it=JSON.parse(process.argv[2]);
if(it.tipo==='testo'){execSync(`ffmpeg -y -loglevel error -sseof -0.3 -i "${it.video}" -frames:v 1 -q:v 3 "${it.file}"`);console.log('ok',it.file);process.exit(0)}
const ROOT=path.join(__dirname,'..','..');const FONTS=path.join(ROOT,'assets','fonts');const f64=n=>'data:font/woff2;base64,'+fs.readFileSync(path.join(FONTS,n)).toString('base64');
const LOGO=fs.readFileSync(path.join(ROOT,'assets','brand','profilo-serena-senza-s.svg'),'utf8').replace(/width="1080" height="1080"/,'width="460" height="460"');
const html=`<!doctype html><meta charset="utf-8"><style>@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
body{margin:0}.c{width:1080px;height:1920px;background:${it.sfondo||'#F4E9EC'};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:56px}
.w{font:500 44px DM;letter-spacing:10px;color:#97606F}</style><div class="c">${LOGO}<div class="w">serenainmente</div></div>`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p=await b.newPage({viewport:{width:1080,height:1920}});await p.setContent(html);await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:it.file,type:'jpeg',quality:88});await b.close();console.log('ok',it.file)})();
