// Copertina dei reel (1080x1920 JPG), da dare a Metricool come videoThumbnailUrl.
// Uso: node copertina.js '{"tipo":"testo","video":"../../video/AAAA-MM-GG-reel.mp4","file":"../../video/AAAA-MM-GG-reel-cover.jpg"}'
//      node copertina.js '{"tipo":"logo","sfondo":"#F2EBE3","file":"../../video/AAAA-MM-GG-reel-cover.jpg"}'
// tipo "testo": l'ultimo fotogramma del reel (frase completa con il filo). tipo "logo": il simbolo di Serena.
// I reel si alternano: uno "testo", uno "logo" (l'ultimo usato è scritto in registro-post.md).
const fs=require('fs');const path=require('path');const {execSync}=require('child_process');const { chromium } = require('playwright-core');
const it=JSON.parse(process.argv[2]);
if(it.tipo==='testo'){execSync(`ffmpeg -y -loglevel error -sseof -0.3 -i "${it.video}" -frames:v 1 -q:v 3 "${it.file}"`);console.log('ok',it.file);process.exit(0)}
const ROOT=path.join(__dirname,'..','..');const FONTS=path.join(ROOT,'assets','fonts');const f64=n=>'data:font/woff2;base64,'+fs.readFileSync(path.join(FONTS,n)).toString('base64');
// Simbolo su tinta piena (niente sfumature), sempre nei toni del rosa (decisione di Antonino 23/10: niente sabbia/marroncino; la crema-cipria va bene):
// l'intensità cambia un poco con il colore del reel nella griglia, così risalta ma resta nella palette. "sfondo" = colore del reel nella rotazione (A/B/C/D).
const PIENO={'#FBF6F4':'#EAD6D1','#F4E9EC':'#E1BCC6','#F2EBE3':'#D8ADB9','#EBD3D9':'#CB9AA8'};
const bgc=PIENO[(it.sfondo||'#F4E9EC').toUpperCase()]||'#DDB4BF';
const T={bg:bgc,c1:'#FBF5F6',c2:'#F1E2E6',s:'#C49AA6',w:'#7E4A5A'};
const LOGO=fs.readFileSync(path.join(ROOT,'assets','brand','profilo-serena.svg'),'utf8').replace(/width="1080" height="1080"/,'width="540" height="540"').replace('#F5EDEA',T.c1).replace('#EDE0E3',T.c2).replace('#DCC6CC',T.s);
const html=`<!doctype html><meta charset="utf-8"><style>@font-face{font-family:DM;font-weight:500;src:url(${f64('dm-sans-latin-500-normal.woff2')})}
body{margin:0}.c{width:1080px;height:1920px;background:${T.bg};display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative}
svg{filter:drop-shadow(0 16px 36px rgba(126,74,90,.16))}.w{position:absolute;top:1300px;font:500 48px DM;letter-spacing:11px;color:${T.w}}</style><div class="c">${LOGO}<div class="w">serenainmente</div></div>`;
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell'});
const p=await b.newPage({viewport:{width:1080,height:1920}});await p.setContent(html);await p.evaluate(()=>document.fonts.ready);
await p.screenshot({path:it.file,type:'jpeg',quality:88});await b.close();console.log('ok',it.file)})();
