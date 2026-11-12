/* serenainmente.it — tutto quello che si muove nel sito. Niente arriva a un server:
   ricerca, cose salvate, spunte e preferenze restano nel browser di chi legge. */
(function(){
var d=document,H=d.documentElement;
function $(s,r){return (r||d).querySelector(s)}
function $$(s,r){return [].slice.call((r||d).querySelectorAll(s))}
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(x){return null}}
function lsj(k,def){try{return JSON.parse(ls(k))||def}catch(x){return def}}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var TT;function toast(t){var o=$('.toast');if(o)o.remove();clearTimeout(TT);var e=d.createElement('div');e.className='toast';e.setAttribute('role','status');e.textContent=t;d.body.appendChild(e);TT=setTimeout(function(){e.remove()},2800)}
function p2(n){return (n<10?'0':'')+n}
/* file di calendario: righe spezzate a 75 caratteri come chiede lo standard (RFC 5545) */
function icsE(s){return String(s).replace(/\\/g,'\\\\').replace(/([,;])/g,'\\$1').replace(/\n/g,'\\n')}
function icsFile(righe,nome){var out=[];righe.forEach(function(r){var b=unescape(encodeURIComponent(r));if(b.length<=75){out.push(r);return}var cur='',n=0,primo=true;
  for(var i=0;i<r.length;i++){var ch=r[i],l=unescape(encodeURIComponent(ch)).length,max=primo?75:74;if(n+l>max){out.push((primo?'':' ')+cur);primo=false;cur='';n=0}cur+=ch;n+=l}
  if(cur)out.push((primo?'':' ')+cur)});
 var a=d.createElement('a');a.href=URL.createObjectURL(new Blob([out.join('\r\n')+'\r\n'],{type:'text/calendar'}));a.download=nome;d.body.appendChild(a);a.click();a.remove()}
function icsOra(){var n=new Date();return n.getUTCFullYear()+p2(n.getUTCMonth()+1)+p2(n.getUTCDate())+'T'+p2(n.getUTCHours())+p2(n.getUTCMinutes())+'00Z'}
function icsGiorno(t){return ''+t.getFullYear()+p2(t.getMonth()+1)+p2(t.getDate())}
window.SerenaCal={e:icsE,file:icsFile,ora:icsOra,giorno:icsGiorno};

/* aspetto chiaro o scuro, e grandezza del testo */
var TB=$('[data-tema-btn]');
function temaLab(){if(TB)TB.setAttribute('aria-label',H.dataset.tema==='scuro'?'Passa all\'aspetto chiaro':'Passa all\'aspetto scuro');var m=$('meta[name=theme-color]');if(m)m.content=H.dataset.tema==='scuro'?'#1C1618':'#FBF6F4'}
if(TB){TB.onclick=function(){var t=H.dataset.tema==='scuro'?'chiaro':'scuro';H.dataset.tema=t;ls('serena:aspetto',t);temaLab();toast(t==='scuro'?'Aspetto scuro':'Aspetto chiaro')}}
temaLab();
var AU=$('[data-tema-auto]');if(AU){AU.hidden=!ls('serena:aspetto');AU.onclick=function(){ls('serena:aspetto',null);location.reload()}}
var AA=$('[data-aa]'),LIV=['','112.5%','128%'],NOMI=['Testo normale','Testo grande','Testo molto grande'];
if(AA)AA.onclick=function(){var n=((+ls('serena:testo')||0)+1)%3;ls('serena:testo',n||null);H.style.fontSize=LIV[n];toast(NOMI[n])};

/* manda, copia */
var mobile=matchMedia('(pointer:coarse)').matches||/Android|iPhone|iPad/i.test(navigator.userAgent);
if(navigator.share&&mobile){
 $$('[data-share]').forEach(function(b){b.hidden=false;b.onclick=function(){navigator.share({title:b.dataset.title,text:b.dataset.title,url:b.dataset.url}).catch(function(x){if(x&&x.name!=='AbortError')open('https://wa.me/?text='+encodeURIComponent(b.dataset.title+' '+b.dataset.url))})}});
 $$('[data-sharetext]').forEach(function(b){b.hidden=false;if(!b.closest('.ck'))b.onclick=function(){navigator.share({text:b.dataset.sharetext}).catch(function(){})}});
}
$$('[data-copytext]').forEach(function(b){b.onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copytext).then(function(){toast(b.dataset.done||'Copiato')})}});

/* lista da spuntare, con l'anello che dice quanto manca */
$$('.ck').forEach(function(box){
 var cs=$$('input[data-ck]',box),N=$('[data-ckn]',box),Z=$('[data-ckreset]',box),V=$('.anello .v',box),armed=false;
 function voce(c){return c.closest('label').textContent.trim()}
 function testo(){return box.dataset.titolo+'\n'+cs.map(function(c){return (c.checked?'☑ ':'☐ ')+voce(c)}).join('\n')+'\n'+box.dataset.url.replace('https://','')}
 function upd(){var n=cs.filter(function(c){return c.checked}).length;
  if(N)N.textContent=n?(n===cs.length?'Tutto fatto: '+n+' su '+n:n+' su '+cs.length+' fatte'):cs.length+' cose, una alla volta';
  if(V)V.style.strokeDashoffset=125.7*(1-n/cs.length);if(Z)Z.hidden=!n}
 cs.forEach(function(c){var k='ck:'+c.dataset.ck;c.checked=ls(k)==='1';c.onchange=function(){ls(k,c.checked?'1':'0');upd()}});
 if(Z)Z.onclick=function(){if(!armed){armed=true;Z.textContent='Tocca di nuovo per azzerare';setTimeout(function(){armed=false;Z.textContent='Azzera le spunte'},4000);return}
  cs.forEach(function(c){c.checked=false;ls('ck:'+c.dataset.ck,'0')});armed=false;Z.textContent='Azzera le spunte';upd()};
 var C=$('[data-copialista]',box);if(C)C.onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(testo()).then(function(){toast('Lista copiata, con le spunte')})};
 var Sh=$('[data-sharetext]',box);if(Sh)Sh.onclick=function(){navigator.share({text:testo()}).catch(function(){})};
 var P=$('[data-stampa-lista]',box);if(P)P.onclick=function(){var o=$('.toast');if(o)o.remove();d.body.classList.add('solo-lista');print()};
 var I=$('[data-ics]',box);if(I)I.onclick=function(){
  var t=new Date();t.setDate(t.getDate()+1);
  var voci=cs.map(function(c){return (c.checked?'[x] ':'[ ] ')+voce(c)}).join('\n');
  icsFile(['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//serenainmente.it//IT','BEGIN:VEVENT','UID:'+Date.now()+'@serenainmente.it','DTSTAMP:'+icsOra(),'DTSTART:'+icsGiorno(t)+'T090000','DURATION:PT15M','SUMMARY:'+icsE(box.dataset.titolo),'DESCRIPTION:'+icsE(voci+'\n'+box.dataset.url),'URL:'+box.dataset.url,'BEGIN:VALARM','ACTION:DISPLAY','DESCRIPTION:'+icsE(box.dataset.titolo),'TRIGGER:PT0M','END:VALARM','END:VEVENT','END:VCALENDAR'],'promemoria-serena.ics');
  toast('Promemoria per domattina alle 9')};
 upd()});
addEventListener('afterprint',function(){d.body.classList.remove('solo-lista')});

/* «Salva per dopo»: resta in questo browser, e la pagina si rilegge anche senza rete */
function salvati(){return lsj('serena:salvati',[])}
function sw(m){try{if(navigator.serviceWorker&&navigator.serviceWorker.controller)navigator.serviceWorker.controller.postMessage(m)}catch(x){}}
$$('[data-salva]').forEach(function(b){var u=b.dataset.salva,t=b.dataset.title;
 function st(){var on=salvati().some(function(x){return x.u===u});b.setAttribute('aria-pressed',on);$('span',b).textContent=on?'Salvata per dopo':'Salva per dopo'}
 b.hidden=false;b.onclick=function(){var L=salvati(),i=-1;L.forEach(function(x,k){if(x.u===u)i=k});if(i>-1)L.splice(i,1);else{L.unshift({u:u,t:t});sw({salva:[u]})}ls('serena:salvati',JSON.stringify(L.slice(0,12)));st();toast(i>-1?'Tolta dalle cose salvate':'Serena la tiene da parte: la ritrovi nella pagina iniziale, anche senza rete')};st()});
function href(u){var B=d.body.dataset.base||'/';return d.body.dataset.rel?B+u.slice(1)+(u.slice(-1)==='/'?'index.html':''):u}
var SV=$('[data-salvati]');
if(SV){var L0=salvati();if(L0.length){SV.hidden=false;$('h2',SV).textContent=L0.length===1?'Serena ti ha tenuto da parte una cosa':'Serena ti ha tenuto da parte '+L0.length+' cose';
 $('ul',SV).innerHTML=L0.map(function(x){return '<li><a class="rowl" href="'+esc(href(x.u))+'"><span class="t"><b>'+esc(x.t)+'</b></span></a></li>'}).join('')}}

/* «Di chi ti prendi cura»: più persone, più età. Mette in cima quello che serve, qui e nella ricerca. Resta in questo browser */
var CU=lsj('serena:cura',{chi:[],eta:[]});if(!Array.isArray(CU.eta))CU.eta=CU.eta?[CU.eta]:[];if(!Array.isArray(CU.chi))CU.chi=[];
var FASCE={'0-1':[0,11],'1-3':[12,35],'3-6':[36,71],'6-12':[72,155],'13-18':[156,227]};
function salvaCU(){ls('serena:cura',CU.chi.length?JSON.stringify(CU):null)}
function adatto(chi,eta){ /* 0 = non c'entra, 1 = per quella persona, 2 = proprio per quell'età */
 if(!CU.chi.length)return 0;var v=0;chi=chi||'';eta=eta||[];
 if(CU.chi.indexOf('anziano')>-1&&chi.indexOf('anziano')>-1)v=chi==='anziano'?2:1;
 if(CU.chi.indexOf('bambino')>-1&&chi.indexOf('bambino')>-1){var e=CU.eta.filter(function(x){return eta.indexOf(x)>-1}).length;
  if(!CU.eta.length)v=Math.max(v,1);else if(e)v=Math.max(v,eta.length<5?2:1)}
 return v}
var PT=$('.per-te');
if(PT){PT.hidden=false;var EB=$('[data-eta-box]',PT),DM=$('[data-dimentica]',PT),UL=$('[data-partenze]'),LI=$$('li',UL);
 LI.forEach(function(li,i){li.dataset.i=i});
 function pt(){$$('[data-cura]',PT).forEach(function(b){b.setAttribute('aria-pressed',CU.chi.indexOf(b.dataset.cura)>-1)});
  $$('[data-eta]',PT).forEach(function(b){b.setAttribute('aria-pressed',CU.eta.indexOf(b.dataset.eta)>-1)});
  EB.hidden=CU.chi.indexOf('bambino')<0;DM.hidden=!CU.chi.length;
  var ord=LI.map(function(li){return {li:li,v:CU.chi.length?adatto(li.dataset.tag,li.dataset.eta?li.dataset.eta.split(' '):[]):(li.dataset.base==='1'?1:0),i:+li.dataset.i}});
  ord.sort(function(a,b){return b.v-a.v||(CU.chi.length?(+(b.li.dataset.pri||0))-(+(a.li.dataset.pri||0)):0)||a.i-b.i});var n=0;
  ord.forEach(function(o){UL.appendChild(o.li);var ok=o.v>0&&n<(CU.chi.length?5:4);o.li.hidden=!ok;if(ok)n++});
  var T=$('[data-partenze-t]');if(T)T.textContent=CU.chi.length?'Serena ha messo in cima queste':'Le ultime guide'}
 $$('[data-cura]',PT).forEach(function(b){b.onclick=function(){var i=CU.chi.indexOf(b.dataset.cura);if(i>-1)CU.chi.splice(i,1);else CU.chi.push(b.dataset.cura);if(CU.chi.indexOf('bambino')<0)CU.eta=[];salvaCU();pt()}});
 $$('[data-eta]',PT).forEach(function(b){b.onclick=function(){var i=CU.eta.indexOf(b.dataset.eta);if(i>-1)CU.eta.splice(i,1);else CU.eta.push(b.dataset.eta);salvaCU();pt()}});
 DM.onclick=function(){CU={chi:[],eta:[]};salvaCU();pt();toast('Fatto: Serena non lo ricorda più')};
 pt()}
/* nelle tabelle per età, le righe che riguardano chi legge */
(function(){if(!CU.eta.length)return;var n=0;$$('tr[data-eta]').forEach(function(tr){var p=tr.dataset.eta.split('-');if(CU.eta.some(function(k){var f=FASCE[k];return f&&+p[0]<=f[1]&&+p[1]>=f[0]})){tr.classList.add('tua');n++}});
 if(n)$$('[data-tua-n]').forEach(function(x){x.hidden=false})})();

/* filtri per argomento nell'elenco delle guide */
var grid=$('[data-grid]');
if(grid){var chips=$$('[data-arg]'),cur='tutti',h=location.hash.slice(1);
 if(chips.some(function(c){return c.dataset.arg===h}))cur=h;
 function run(){$$('[data-a]',grid).forEach(function(c){c.hidden=!(cur==='tutti'||c.dataset.a===cur)});chips.forEach(function(ch){ch.setAttribute('aria-pressed',ch.dataset.arg===cur)})}
 chips.forEach(function(ch){ch.onclick=function(){cur=ch.dataset.arg;history.replaceState(null,'',cur==='tutti'?location.pathname:'#'+cur);run()}});run()}

/* anteprima del foglio da vicino */
$$('[data-zoom]').forEach(function(b){var D=$('dialog.zoom');if(!D||!D.showModal)return;b.onclick=function(){D.showModal()};$('.x',D).onclick=function(){D.close()}});

/* «Ascolta la guida»: la legge il telefono, con la sua sintesi vocale. Niente esce dal telefono */
var AB=$('[data-ascolta]');
if(AB&&'speechSynthesis' in window&&window.SpeechSynthesisUtterance){AB.hidden=false;var parla=false;
 function fine(){parla=false;$('span',AB).textContent='Ascolta la guida';AB.setAttribute('aria-pressed','false')}
 AB.onclick=function(){if(parla){speechSynthesis.cancel();fine();return}
  var pezzi=$$('[data-leggi]').map(function(el){return el.innerText.replace(/\s+/g,' ').trim()}).filter(Boolean);speechSynthesis.cancel();
  pezzi.forEach(function(t,i){var u=new SpeechSynthesisUtterance(t);u.lang='it-IT';u.rate=.95;if(i===pezzi.length-1)u.onend=fine;speechSynthesis.speak(u)});
  parla=true;$('span',AB).textContent='Ferma la lettura';AB.setAttribute('aria-pressed','true')};
 addEventListener('pagehide',function(){speechSynthesis.cancel()})}

/* «Calcola la scadenza»: il conto lo fa il telefono, con la regola scritta nella guida */
$$('[data-calc]').forEach(function(box){var tipo=box.dataset.calc,N=$('[data-nascita]',box),R=$('[data-rilascio]',box),O=$('[data-esito]',box),B=$('[data-cal]',box),sc=null;
 function fmt(t){return t.toLocaleDateString('it-IT',{day:'numeric',month:'long',year:'numeric'})}
 function calc(){sc=null;B.hidden=true;O.textContent='';if(!R.value)return;var r=new Date(R.value+'T12:00');if(isNaN(r))return;
  if(tipo==='anno'){sc=new Date(r);sc.setFullYear(sc.getFullYear()+1);O.textContent='Vale un anno dal rilascio: fino al '+fmt(sc)+'.'}
  else{if(!N.value)return;var n=new Date(N.value+'T12:00');if(isNaN(n)||n>r)return;var eta=(r-n)/31557600000,anni=eta<3?3:eta<18?5:10,min=new Date(r);min.setFullYear(min.getFullYear()+anni);
   sc=new Date(n);sc.setFullYear(min.getFullYear());if(sc<min)sc.setFullYear(sc.getFullYear()+1);
   O.textContent='Rilasciata a '+(eta<3?'meno di 3 anni':eta<18?'un\'età tra 3 e 18 anni':'più di 18 anni')+': vale '+anni+' anni e scade al compleanno successivo, il '+fmt(sc)+'.'}
  B.hidden=false}
 [N,R].forEach(function(el){if(el)el.addEventListener('input',calc)});
 B.onclick=function(){if(!sc)return;var av=new Date(sc);av.setMonth(av.getMonth()-(tipo==='anno'?1:2));var tit=box.dataset.titolo+' entro il '+fmt(sc);
  icsFile(['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//serenainmente.it//IT','BEGIN:VEVENT','UID:'+Date.now()+'@serenainmente.it','DTSTAMP:'+icsOra(),'DTSTART;VALUE=DATE:'+icsGiorno(av),'SUMMARY:'+icsE(tit),'DESCRIPTION:'+icsE('Scadenza calcolata con '+box.dataset.url+'\nFa fede la data scritta sul documento.'),'BEGIN:VALARM','ACTION:DISPLAY','DESCRIPTION:'+icsE(tit),'TRIGGER:PT9H','END:VALARM','END:VEVENT','END:VCALENDAR'],'scadenza-serena.ics');
  toast('Promemoria pronto per il calendario')}});

/* le pagine già aperte si rileggono anche senza rete (per esempio in ambulatorio). Si prepara a pagina caricata, senza rallentarla */
if('serviceWorker' in navigator&&location.protocol==='https:'||location.hostname==='localhost'){addEventListener('load',function(){var f=function(){try{navigator.serviceWorker.register(href('/sw.js')).then(function(){var L=salvati().map(function(x){return x.u});if(L.length)setTimeout(function(){sw({salva:L})},1500)}).catch(function(){})}catch(x){}};
 if(window.requestIdleCallback)requestIdleCallback(f,{timeout:4000});else setTimeout(f,2500)})}

/* ---------- la ricerca: trova nelle guide la risposta, tutto in locale ---------- */
var F=$('#cerca');if(!F||!F.showModal)return;
var Q=$('input',F),OUT=$('[data-esiti]',F),PRE=$('[data-prima]',F),IDX=null,carica=false;
var STOP=' il lo la i gli le un uno una di a da in con su per tra fra e ed o ma che chi non mi ti si ci vi ne ho hai ha abbiamo hanno sono sei come cosa cose quando dove quanto quanta quanti quante perche del dello della dei delle degli al allo alla ai alle dal dalla nel nella sul sulla mio mia miei mie tuo tua suo sua nostro nostra figlio figlia figli bambino bambina bambini bimbo bimba piccolo piccola oggi stasera stanotte adesso ora devo deve posso puo vuole voglio fare fa faccio serve servono anni anno mesi mese settimane giorni piu molto poco tanto tanta tanti tante sempre mai ancora gia anche solo ogni tutto tutti questa questo essere avere volte due tre prende trovo '.split(' ');
function norm(x){return (x||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim()}
var SUF=['azione','azioni','izione','izioni','amento','amenti','mente','ando','endo','iamo','are','ere','ire','ato','ata','ati','ate','uto','uta','ito','ita','ano','ono','ale','ali'];
function radice(w){if(w.length<=4)return w;for(var i=0;i<SUF.length;i++){var s=SUF[i];if(w.length-s.length>=4&&w.slice(-s.length)===s)return w.slice(0,-s.length)}var r=w.replace(/[aeiou]+$/,'');return r.length>=3?r:w}
/* sintomi, medicine da dosare, cadute: Serena non risponde, indica a chi chiedere. Queste parole non danno punti */
var SINT='febbr toss vomit diarre raffredd dolor mal male eruzion sfog respir convuls cadut cade casc dos dose dosi dosagg tachipirin antibiotic paracetamol ibuprofen gocc sciropp suppost ferit ustion sangue svenut sveniment otit bronch prurit influenz infezion allergi pancia gola orecch dentin testa botta trauma emergenz urgent pronto'.split(' ');
function sintomo(r){return SINT.some(function(s){return s.length<5?r===s:r.indexOf(s)===0})}
function radici(t){return norm(t).split(' ').filter(function(w){return w.length>1&&STOP.indexOf(w)<0&&!/^\d+$/.test(w)}).map(radice)}
function simile(a,b){if(a.length<4||b.length<4)return a===b;if((a==='medic'&&b.indexOf('medicin')===0)||(b==='medic'&&a.indexOf('medicin')===0))return false; /* medico non è medicina */return a.indexOf(b)===0||b.indexOf(a)===0}
/* parole diverse, stessa cosa */
var GR=['dorm sonn nann addorment svegl risvegl sonnellin pisolin nott lett','sera serat routin buonanott capricc','pediatr dottor dottoress medic ambulator','visit controll bilanc appuntament','specialist allergolog gastroenterolog diabetolog dermatolog oculist ortoped logoped impegnativ ricett cup prenot attes','disd spost annull rimand cancell ticket pag cup','document cart tesser refert fascicol fse spid librett modul esam analis','vaccin richiam','scuol nido asil matern infanz iscr iscriv element primar','anzian nonn genitor madr padr mamm papa badant','medicin farmac pastigl pillol compress terap','identit cie passaport espatr viagg','organizz settiman planner calendar scadenz impegn gestional promemor ricord agend','stamp pdf fogl scaric','sport palestr piscin calci nuot danz ginnast agonist moviment'].map(function(g){return g.split(' ')});
function gruppi(r){var o=[];GR.forEach(function(g,i){if(g.some(function(m){return simile(m,r)}))o.push(i)});return o}
function prepara(){IDX.forEach(function(x){x.T=radici(x.t);x.A=radici(x.a);x.B=radici(x.b);x.C=radici(x.c2||'');x.GA=[];x.GB=[];
  x.A.forEach(function(r){gruppi(r).forEach(function(g){if(x.GA.indexOf(g)<0)x.GA.push(g)})});x.B.forEach(function(r){gruppi(r).forEach(function(g){if(x.GB.indexOf(g)<0)x.GB.push(g)})});
  if(x.ps)x.PS=x.ps.map(function(s){return [radici(s[0]),radici(s[1])]})})}
function mesi(t){var m=/(\d{1,2})\s*(mes|ann|settiman|giorn)/.exec(norm(t));if(!m)return null;var n=+m[1];return m[2]==='ann'?n*12:m[2]==='mes'?n:0}
function fasciaDi(m){for(var k in FASCE)if(FASCE[k][0]<=m&&m<=FASCE[k][1])return k;return null}
function punti(x,r){var p=0;if(x.A.some(function(w){return simile(w,r)}))p=6;else if(x.B.some(function(w){return simile(w,r)}))p=2;else if(x.C.some(function(w){return simile(w,r)}))p=1;
 var g=gruppi(r);if(g.some(function(i){return x.GA.indexOf(i)>-1}))p=Math.max(p,4);else if(!p&&g.some(function(i){return x.GB.indexOf(i)>-1}))p=1;return p}
/* cerca(t) → {sint, sicura, esiti:[{x,s}], R} */
function cerca(t){var raw=' '+norm(t)+' ',T=radici(t),sint=T.some(sintomo),R=T.filter(function(r){return !sintomo(r)});
 if(sint)return {sint:true,sicura:false,esiti:[],R:R};
 if(!R.length)return {sint:false,sicura:false,esiti:[],R:R};
 var problema=/ (non|mai|sveglia|svegli\w*|piange|rifiuta|capricci|fatica|aiuto|cosa fare|come fare|come faccio|come si fa) /.test(raw),dato=/ (quant[oaie]|ore|quando|entro|scade|scadenza|vale|validita|dura|eta) /.test(raw);
 var m=mesi(t),fq=m===null?null:fasciaDi(m),out=[],df=R.map(function(){return 0});
 IDX.forEach(function(x){var s=0,k=0,forti=0;R.forEach(function(r,i){var p=punti(x,r);if(p){k++;s+=p;df[i]++;if(p>=4)forti++}});
  if(!k)return;s+=k*3;R.forEach(function(r){if(x.T.some(function(w){return simile(w,r)}))s+=2});
  if(problema&&!dato)s+=x.g==='dati'?-5:(x.k==='Guida'?2:0);if(dato&&x.g==='dati')s+=4;
  if(fq&&x.fa&&x.fa.indexOf(fq)>-1&&x.fa.length<5)s+=3;
  s+=adatto(x.c,x.fa)*1.5;if(x.k.indexOf('fonti')>-1)s-=3;else if(x.k!=='Pagina')s+=2;
  out.push({x:x,s:s,k:k,forti:forti})});
 out.sort(function(a,b){return b.s-a.s});
 var n=R.length,vuote=df.filter(function(v){return !v}).length,top=out[0],sicura=!!top&&top.forti>=1&&(n<=3?vuote===0:vuote<=1&&vuote<n/2)&&top.k>=Math.ceil(n*.6);
 var lim=top?top.s*.5:0;return {sint:false,sicura:sicura,esiti:out.filter(function(o){return o.s>=lim}).slice(0,sicura?4:3),R:R,dato:dato,problema:problema}}
function etaRiga(x,t){if(!x.eta)return '';var m=mesi(t),rows;
 if(m!==null)rows=x.eta.r.filter(function(r){return r[0]<=m&&m<=r[1]});else if(CU.eta.length)rows=x.eta.r.filter(function(r){return CU.eta.some(function(k){var f=FASCE[k];return r[0]<=f[1]&&r[1]>=f[0]})});else return '';
 return rows.map(function(r){return '<p class="eta"><b>'+esc(r[2])+':</b> '+esc(r[3])+(r[4]?'. <span class="small">'+esc(x.eta.c[2])+': '+esc(r[4])+'</span>':'')+'</p>'}).join('')}
function passo(x,R){if(!x.PS||!x.PS.length)return null;var best=0,bp=-1;x.PS.forEach(function(s,i){var p=0;R.forEach(function(r){if(s[0].some(function(w){return simile(w,r)}))p+=2;else if(s[1].some(function(w){return simile(w,r)}))p+=1});if(p>bp){bp=p;best=i}});return {i:best,s:x.ps[best],p:bp}}
function riga(x){return '<li><a class="rowl" href="'+esc(href(x.u))+'">'+(x.i?'<img src="'+esc(href(x.i))+'" alt="" width="64" height="64" loading="lazy">':'')+'<span class="t"><b>'+esc(x.t)+'</b><small>'+esc(x.k)+(x.m?' · '+x.m+' min':'')+'</small></span></a></li>'}
function mostra(){var t=Q.value.trim();if(!IDX){return}
 if(norm(t).length<2){OUT.innerHTML='';PRE.hidden=false;return}
 PRE.hidden=true;var E=cerca(t),h='';
 if(E.sint){
  h='<div class="avviso sicuro"><p><b>Su sintomi, medicine e cadute Serena non dà indicazioni.</b></p><ul><li>Chiama il pediatra o il medico di famiglia.</li><li>Di notte e nei giorni festivi c\'è la guardia medica.</li><li>Se è urgente, chiama il 112.</li></ul><p>Intanto puoi scrivere cosa hai notato, per raccontarlo bene.</p><a class="btn" href="'+esc(href('/strumenti/preparo-la-visita/'))+'" data-umami-event="cerca-sintomi-preparo">Apri «Preparo la visita»</a></div>';
 }else if(E.sicura){var x=E.esiti[0].x,ps=passo(x,E.R),er=(E.dato||x.g==='dati')?etaRiga(x,t):'';if(ps&&er)ps=null;else if(ps&&ps.p<2)ps={i:0,s:x.ps[0],p:0};
  h='<article class="risp vetro"><span class="chip">'+esc(x.k)+(x.m?' · '+x.m+' min':'')+'</span><h3>'+esc(x.t)+'</h3>'+er+
   (er?'<p>'+esc(x.d)+'</p>':'')+(ps?'<div class="gesto"><span class="eyebrow">'+(ps.i===0?'Per cominciare':'Il punto che cerchi')+'</span><p><b>'+esc(ps.s[0])+'.</b> '+esc(ps.s[1])+'</p></div>':(er?'':'<p>'+esc(x.d)+'</p>'))+
   (x.ag?'<p class="small">Dalla guida di Serena · fonti controllate il '+esc(x.ag)+'</p>':'')+
   '<a class="btn" href="'+esc(href(x.u)+(ps&&ps.i>0?'#passo-'+(ps.i+1):''))+'" data-umami-event="cerca-apri">'+esc(x.az||'Apri')+(x.m?' · '+x.m+' min':'')+'</a></article>';
  if(E.esiti.length>1)h+='<h2>Può servirti anche</h2><ul class="rows">'+E.esiti.slice(1).map(function(o){return riga(o.x)}).join('')+'</ul>';
 }else{
  h='<p class="avviso">Serena non ha ancora una guida su questo. Se vuoi, scrivilo a privacy@serenainmente.it: le prossime guide nascono così.</p>';
  if(E.esiti.length)h+='<h2>Le più vicine</h2><ul class="rows">'+E.esiti.map(function(o){return riga(o.x)}).join('')+'</ul>';
  else h+='<h2>Le più cercate</h2><ul class="rows">'+IDX.filter(function(x){return x.top}).slice(0,4).map(riga).join('')+'</ul>';
  if(window.umami&&!F.dataset.vuota){F.dataset.vuota=1;try{umami.track('cerca-senza-esito')}catch(e){}}
 }
 OUT.innerHTML=h}
function apri(q){if(!F.open)F.showModal();if(q!==undefined)Q.value=q;Q.focus();
 if(!IDX&&!carica){carica=true;var s=d.createElement('script');s.src=F.dataset.src;s.onload=function(){IDX=window.SERENA_INDICE||[];prepara();mostra()};d.head.appendChild(s)}else mostra()}
Q.addEventListener('input',mostra);
$('form',F).onsubmit=function(e){e.preventDefault();var a=$('.risp .btn',OUT);if(a)location.href=a.href};
$('[data-chiudi]',F).onclick=function(){F.close()};
F.addEventListener('click',function(e){if(e.target===F)F.close()});
$$('[data-cerca]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();apri(b.dataset.cerca||undefined)})});
$$('[data-q]',F).forEach(function(b){b.onclick=function(){Q.value=b.dataset.q;mostra();Q.focus()}});
d.addEventListener('keydown',function(e){if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test((d.activeElement||{}).tagName||'')&&!e.metaKey&&!e.ctrlKey){e.preventDefault();apri()}});
var qp=new URLSearchParams(location.search).get('q');if(qp||location.hash==='#cerca')apri(qp||undefined);
window.SerenaCerca={apri:apri,prova:function(t){var E=cerca(t);return {sint:E.sint,sicura:E.sicura,u:E.esiti.map(function(o){return o.x.u})}}};
})();
