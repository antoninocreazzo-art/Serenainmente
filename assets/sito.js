/* serenainmente.it — tutto quello che si muove nel sito. Niente arriva a un server:
   ricerca, cose salvate, spunte e preferenze restano nel browser di chi legge. */
(function(){
var d=document,H=d.documentElement;
function $(s,r){return (r||d).querySelector(s)}
function $$(s,r){return [].slice.call((r||d).querySelectorAll(s))}
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(x){return null}}
function lsj(k,def){try{return JSON.parse(ls(k))||def}catch(x){return def}}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var TT;function toast(t){var o=$('.toast');if(o)o.remove();clearTimeout(TT);var e=d.createElement('div');e.className='toast';e.setAttribute('role','status');e.textContent=t;d.body.appendChild(e);TT=setTimeout(function(){e.remove()},t.length>45?6000:2800)}
function p2(n){return (n<10?'0':'')+n}
var MESI=['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'];
function dataIt(t,senzaAnno){return t.getDate()+(t.getDate()===1?'°':'')+' '+MESI[t.getMonth()]+(senzaAnno?'':' '+t.getFullYear())}
var FILE_CAL='File scaricato. Aprilo e scegli Calendario: il promemoria entra lì solo dopo.';
/* file di calendario: righe spezzate a 75 caratteri come chiede lo standard (RFC 5545) */
function icsE(s){return String(s).replace(/\\/g,'\\\\').replace(/([,;])/g,'\\$1').replace(/\n/g,'\\n')}
function icsFile(righe,nome){var out=[];righe.forEach(function(r){var b=unescape(encodeURIComponent(r));if(b.length<=75){out.push(r);return}var cur='',n=0,primo=true;
  for(var i=0;i<r.length;i++){var ch=r[i],l=unescape(encodeURIComponent(ch)).length,max=primo?75:74;if(n+l>max){out.push((primo?'':' ')+cur);primo=false;cur='';n=0}cur+=ch;n+=l}
  if(cur)out.push((primo?'':' ')+cur)});
 var a=d.createElement('a');a.href=URL.createObjectURL(new Blob([out.join('\r\n')+'\r\n'],{type:'text/calendar'}));a.download=nome;d.body.appendChild(a);a.click();a.remove()}
function icsOra(){var n=new Date();return n.getUTCFullYear()+p2(n.getUTCMonth()+1)+p2(n.getUTCDate())+'T'+p2(n.getUTCHours())+p2(n.getUTCMinutes())+'00Z'}
function icsGiorno(t){return ''+t.getFullYear()+p2(t.getMonth()+1)+p2(t.getDate())}
function nota(t,u){var L=lsj('serena:promemoria',[]);L=L.filter(function(x){return x.t!==t});L.unshift({t:t,u:u||location.pathname,q:new Date().toISOString().slice(0,10)});ls('serena:promemoria',JSON.stringify(L.slice(0,20)))}
window.SerenaCal={e:icsE,file:icsFile,ora:icsOra,giorno:icsGiorno,nota:nota,data:dataIt};

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
  icsFile(['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//serenainmente.it//IT','BEGIN:VEVENT','UID:'+Date.now()+'@serenainmente.it','DTSTAMP:'+icsOra(),'DTSTART:'+icsGiorno(t)+'T090000','DURATION:PT15M','SUMMARY:'+icsE(box.dataset.titolo),'DESCRIPTION:'+icsE(voci+'\n'+box.dataset.url),'URL:'+box.dataset.url,'BEGIN:VALARM','ACTION:DISPLAY','DESCRIPTION:'+icsE(box.dataset.titolo),'TRIGGER:PT0M','END:VALARM','END:VEVENT','END:VCALENDAR'],'promemoria-serena.ics');nota(box.dataset.titolo,location.pathname+'#lista');
  toast(FILE_CAL)};
 upd()});
addEventListener('afterprint',function(){d.body.classList.remove('solo-lista')});

/* «Salva per dopo»: resta in questo browser, e la pagina si rilegge anche senza rete */
function salvati(){return lsj('serena:salvati',[])}
function sw(m){try{if(navigator.serviceWorker&&navigator.serviceWorker.controller)navigator.serviceWorker.controller.postMessage(m)}catch(x){}}
function domattina(titolo,url){var t=new Date();t.setDate(t.getDate()+1);
 icsFile(['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//serenainmente.it//IT','BEGIN:VEVENT','UID:'+Date.now()+'@serenainmente.it','DTSTAMP:'+icsOra(),'DTSTART:'+icsGiorno(t)+'T090000','DURATION:PT15M','SUMMARY:'+icsE('Da rileggere: '+titolo),'DESCRIPTION:'+icsE(url),'URL:'+url,'BEGIN:VALARM','ACTION:DISPLAY','DESCRIPTION:'+icsE(titolo),'TRIGGER:PT0M','END:VALARM','END:VEVENT','END:VCALENDAR'],'promemoria-serena.ics');
 nota(titolo,url.replace(/^https?:\/\/[^/]+/,''));toast(FILE_CAL)}
$$('[data-salva]').forEach(function(b){var u=b.dataset.salva,t=b.dataset.title,RB=$('[data-ricorda="'+u+'"]');
 function st(){var on=salvati().some(function(x){return x.u===u});b.setAttribute('aria-pressed',on);$('span',b).textContent=on?'Salvata per dopo':'Salva per dopo';if(RB)RB.hidden=!on}
 b.hidden=false;b.onclick=function(){var L=salvati(),i=-1;L.forEach(function(x,k){if(x.u===u)i=k});if(i>-1)L.splice(i,1);else{L.unshift({u:u,t:t});sw({salva:[u]})}ls('serena:salvati',JSON.stringify(L.slice(0,12)));st();toast(i>-1?'Tolta dalle cose salvate':'Serena la tiene da parte: la ritrovi in «I tuoi salvati», anche senza rete')};
 if(RB)RB.onclick=function(){domattina(t,'https://serenainmente.it'+u)};st()});
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
  if(!CU.eta.length)v=Math.max(v,1);else if(e)v=Math.max(v,eta.length<=2?2:(eta.length<5?1.5:1))}
 return v}
var PT=$('.per-te');
if(PT){PT.hidden=false;var EB=$('[data-eta-box]',PT),DM=$('[data-dimentica]',PT),UL=$('[data-partenze]'),LI=$$('li',UL);
 LI.forEach(function(li,i){li.dataset.i=i});
 function pt(){$$('[data-cura]',PT).forEach(function(b){b.setAttribute('aria-pressed',CU.chi.indexOf(b.dataset.cura)>-1)});
  $$('[data-eta]',PT).forEach(function(b){b.setAttribute('aria-pressed',CU.eta.indexOf(b.dataset.eta)>-1)});
  EB.hidden=CU.chi.indexOf('bambino')<0;DM.hidden=!CU.chi.length;
  var ord=LI.map(function(li){return {li:li,v:CU.chi.length?adatto(li.dataset.tag,li.dataset.fasce?li.dataset.fasce.split(' '):[]):(li.dataset.base==='1'?1:0),i:+li.dataset.i}});
  ord.sort(function(a,b){return b.v-a.v||(CU.chi.length?(+(b.li.dataset.pri||0))-(+(a.li.dataset.pri||0)):0)||a.i-b.i});var n=0;
  ord.forEach(function(o){UL.appendChild(o.li);var ok=o.v>0&&n<(CU.chi.length?5:4);o.li.hidden=!ok;if(ok)n++});
  var T=$('[data-partenze-t]'),PV=$('[data-per-voi]'),CASA=$('[data-partenze-casa]');if(T)T.textContent=CU.chi.length?'Serena ha messo in cima queste':'Le ultime guide';
  /* con una scelta fatta, l'elenco sale in cima alla pagina, subito sotto la casella, e prende il posto della scheda dell'ora */
  if(PV&&CASA){var su=CU.chi.length>0;if(su){PV.appendChild(T);PV.appendChild(UL)}else{CASA.appendChild(T);CASA.appendChild(UL)}PV.hidden=!su;$$('.ora-card').forEach(function(c){c.hidden=su});var EX=$('[data-esempi]');if(EX)EX.hidden=su}}
 $$('[data-cura]',PT).forEach(function(b){b.onclick=function(){var i=CU.chi.indexOf(b.dataset.cura);if(i>-1)CU.chi.splice(i,1);else CU.chi.push(b.dataset.cura);if(CU.chi.indexOf('bambino')<0)CU.eta=[];salvaCU();pt()}});
 $$('[data-eta]',PT).forEach(function(b){b.onclick=function(){var i=CU.eta.indexOf(b.dataset.eta);if(i>-1)CU.eta.splice(i,1);else CU.eta.push(b.dataset.eta);salvaCU();pt()}});
 DM.onclick=function(){CU={chi:[],eta:[]};salvaCU();pt();toast('Fatto: Serena non lo ricorda più')};
 pt()}
/* «I tuoi salvati»: pagine salvate, liste cominciate, strumenti, promemoria. Tutto letto dal browser, niente da un server */
var TU=$('[data-tuoi]');
if(TU){var GT=JSON.parse(TU.dataset.guide||'{}'),qualcosa=false;
 function sez(nome,righe){var S1=$('[data-t-'+nome+']',TU);if(!righe.length)return;qualcosa=true;S1.hidden=false;$('ul',S1).innerHTML=righe.join('')}
 function r(u,t,sotto){return '<li><a class="rowl" href="'+esc(href(u))+'"><span class="t"><b>'+esc(t)+'</b>'+(sotto?'<small>'+esc(sotto)+'</small>':'')+'</span></a></li>'}
 sez('salvati',salvati().map(function(x){return r(x.u,x.t,'')}));
 var liste=[];Object.keys(GT).forEach(function(sl){var n=0;for(var i=0;i<12;i++)if(ls('ck:'+sl+'-'+i)==='1')n++;if(n)liste.push(r('/guide/'+sl+'/#lista',GT[sl],n+(n===1?' cosa spuntata':' cose spuntate')))});sez('liste',liste);
 var st=[],pv=lsj('serena:preparo-visita',null),md=lsj('serena:medicine',null);
 if(pv&&((pv.q&&pv.q.length)||pv.chi||pv.notato))st.push(r('/strumenti/preparo-la-visita/','Preparo la visita',(pv.q&&pv.q.length?pv.q.length+(pv.q.length===1?' domanda':' domande'):'Cominciata')+(pv.chi?' · per '+pv.chi:'')));
 if(md&&md.m&&md.m.length)st.push(r('/strumenti/medicine-di-casa/','Medicine di casa',md.m.length+(md.m.length===1?' medicina in lista':' medicine in lista')));sez('strumenti',st);
 sez('promemoria',lsj('serena:promemoria',[]).map(function(x){var g=new Date(x.q+'T12:00');return r(x.u,x.t,'File preparato il '+dataIt(g,true))}));
 if(qualcosa){$('[data-t-inizio]',TU).hidden=true;var SVU=$('[data-t-svuota]',TU),arm=false;SVU.hidden=false;SVU.onclick=function(){if(!arm){arm=true;SVU.textContent='Tocca di nuovo: pagine salvate e promemoria spariscono da qui';setTimeout(function(){arm=false;SVU.textContent='Dimentica tutto quello che è in questa pagina'},4000);return}ls('serena:salvati',null);ls('serena:promemoria',null);location.reload()}}}
/* nelle tabelle per età, le righe che riguardano chi legge */
(function(){if(!CU.eta.length)return;var n=0;$$('tr[data-eta]').forEach(function(tr){var p=tr.dataset.eta.split('-');if(CU.eta.some(function(k){var f=FASCE[k];return f&&+p[0]<=f[1]&&+p[1]>=f[0]})){tr.classList.add('tua');n++}});
 if(n)$$('[data-tua-n]').forEach(function(x){x.hidden=false})})();

/* filtri per argomento nell'elenco delle guide */
var grid=$('[data-grid]');
if(grid){var chips=$$('[data-arg]'),cur='tutti',h=location.hash.slice(1);
 if(chips.some(function(c){return c.dataset.arg===h}))cur=h;
 function run(){$$('[data-a]',grid).forEach(function(c){c.hidden=!(cur==='tutti'||c.dataset.a===cur)});chips.forEach(function(ch){ch.setAttribute('aria-pressed',ch.dataset.arg===cur)})}
 chips.forEach(function(ch){ch.onclick=function(){cur=ch.dataset.arg;history.replaceState(null,'',cur==='tutti'?location.pathname:'#'+cur);run()}});run()}

/* una sola via alla volta: dove la casella è in pagina, «Cerca» nella barra in basso compare solo quando la casella non si vede più */
var TC=$('.tab-c[data-con-casella]'),CA=$('main .chiedi');
if(TC&&CA){if('IntersectionObserver' in window)new IntersectionObserver(function(es){TC.hidden=es[es.length-1].isIntersecting},{rootMargin:'-64px 0px -84px 0px'}).observe(CA);else TC.hidden=false}
/* passi richiudibili: l'indirizzo #passo-3 lo apre; in stampa si aprono tutti */
function apriPasso(){var x=location.hash&&d.getElementById(location.hash.slice(1));if(x&&x.tagName==='DETAILS'){x.open=true;x.scrollIntoView({block:'start'})}}
addEventListener('hashchange',apriPasso);apriPasso();
addEventListener('beforeprint',function(){$$('.passi details').forEach(function(x){x.dataset.era=x.open?'1':'';x.open=true})});
addEventListener('afterprint',function(){$$('.passi details').forEach(function(x){if(x.dataset.era==='')x.open=false})});
/* anteprima del foglio da vicino */
$$('[data-zoom]').forEach(function(b){var D=$('dialog.zoom');if(!D||!D.showModal)return;b.onclick=function(){D.showModal()};$('.x',D).onclick=function(){D.close()}});

/* «Ascolta la guida»: la legge il telefono, con la sua sintesi vocale. Niente esce dal telefono */
var AB=$('[data-ascolta]');
if(AB&&'speechSynthesis' in window&&window.SpeechSynthesisUtterance){AB.hidden=false;var parla=false;
 function fine(){parla=false;$('span',AB).textContent='Ascolta la guida';AB.setAttribute('aria-pressed','false')}
 function scegli(){return speechSynthesis.getVoices().filter(function(v){return /^it/i.test(v.lang)&&v.localService})[0]||null}
 try{speechSynthesis.getVoices()}catch(x){}
 AB.onclick=function(){if(parla){speechSynthesis.cancel();fine();return}
  var v=scegli();if(!v){AB.disabled=true;$('span',AB).textContent='Su questo telefono la lettura non è disponibile';return} /* niente voci online: il testo non deve uscire dal telefono */
  var pezzi=$$('[data-leggi]').map(function(el){return el.textContent.replace(/\s+/g,' ').trim()}).filter(Boolean);speechSynthesis.cancel();
  pezzi.forEach(function(t,i){var u=new SpeechSynthesisUtterance(t);u.lang='it-IT';u.voice=v;u.rate=.95;if(i===pezzi.length-1)u.onend=fine;speechSynthesis.speak(u)});
  parla=true;$('span',AB).textContent='Ferma la lettura';AB.setAttribute('aria-pressed','true')};
 addEventListener('pagehide',function(){speechSynthesis.cancel()})}

/* «Calcola la scadenza»: il conto lo fa il telefono, con la regola scritta nella guida */
$$('[data-calc]').forEach(function(box){var tipo=box.dataset.calc,N=$('[data-nascita]',box),R=$('[data-rilascio]',box),O=$('[data-esito]',box),B=$('[data-cal]',box),sc=null;
 function fmt(t){return dataIt(t)}
 function calc(){sc=null;B.hidden=true;O.textContent='';if(!R.value)return;var r=new Date(R.value+'T12:00');if(isNaN(r))return;
  if(tipo==='anno'){sc=new Date(r);sc.setFullYear(sc.getFullYear()+1);O.textContent='Vale un anno dal rilascio: fino al '+fmt(sc)+'.'}
  else{if(!N.value)return;var n=new Date(N.value+'T12:00');if(isNaN(n)||n>r)return;var eta=(r-n)/31557600000,anni=eta<3?3:eta<18?5:10,min=new Date(r);min.setFullYear(min.getFullYear()+anni);
   sc=new Date(n);sc.setFullYear(min.getFullYear());if(sc<min)sc.setFullYear(sc.getFullYear()+1);
   O.textContent='Rilasciata a '+(eta<3?'meno di 3 anni':eta<18?'un\'età tra 3 e 18 anni':'più di 18 anni')+': vale '+anni+' anni e scade al compleanno successivo, il '+fmt(sc)+'.'}
  var oggi=new Date();oggi.setHours(12,0,0,0);
  if(sc<oggi){var gg=Math.round((oggi-sc)/86400000),mm=Math.floor(gg/30.44);O.textContent=(tipo==='cie'?'È già scaduta da ':'È già scaduto da ')+(mm>=2?mm+' mesi':gg+(gg===1?' giorno':' giorni'))+' (il '+fmt(sc)+'): va '+(tipo==='cie'?'rinnovata.':'rinnovato.');sc=null;return}
  B.hidden=false}
 [N,R].forEach(function(el){if(el)el.addEventListener('input',calc)});
 B.onclick=function(){if(!sc)return;var av=new Date(sc);av.setMonth(av.getMonth()-(tipo==='anno'?1:2));var dom=new Date();dom.setDate(dom.getDate()+1);dom.setHours(12,0,0,0);if(av<dom)av=dom; /* mai un promemoria nel passato */var tit=box.dataset.titolo+' entro il '+fmt(sc);
  icsFile(['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//serenainmente.it//IT','BEGIN:VEVENT','UID:'+Date.now()+'@serenainmente.it','DTSTAMP:'+icsOra(),'DTSTART;VALUE=DATE:'+icsGiorno(av),'SUMMARY:'+icsE(tit),'DESCRIPTION:'+icsE('Scadenza calcolata con '+box.dataset.url+'\nFa fede la data scritta sul documento.'),'BEGIN:VALARM','ACTION:DISPLAY','DESCRIPTION:'+icsE(tit),'TRIGGER:PT9H','END:VALARM','END:VEVENT','END:VCALENDAR'],'scadenza-serena.ics');nota(tit,location.pathname);
  toast(FILE_CAL)}});

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
/* PRIMA LA SITUAZIONE, POI LE PAROLE.
   1) urgenza: se la frase parla di un'urgenza o di un sintomo, Serena non risponde con una guida: indica a chi chiedere, con il 112 in vista.
   Le liste si riducono alla radice come le parole di chi scrive, così il confronto è alla pari. Queste parole non danno punti. */
var URG_FRASI=[/ non si sveglia /,/ non respira /,/ respira (male|a fatica|con fatica) /,/ fa(tica)? (fatica )?a respirare /,/ (gli |le |mi )?manca (il fiato|il respiro|l aria) /,/ non riesce (a|ad|piu a|piu ad) (parlare|respirare|muovere|muoversi|alzarsi|svegliarsi|stare in piedi) /,/ non si alza /,/ (pres[oaie]|dat[oaie]|ingerit[oaie]) troppe? /,/ troppe (pastiglie|medicine|gocce|pillole|compresse) /,/ sbagliat\w* (le |la |il )?(pastigli\w*|medicin\w*|dose|dosi|farmac\w*) /,/ (doppio della dose|dose doppia|doppia dose) /,
 / (pres[oaie]|ingoiat\w*|inghiottit\w*|mangiat\w*|bevut\w*) (le |la |delle |una |un |il |i |dei |gli )?(pastigli\w*|medicin\w*|farmac\w*|pillol\w*|compress\w*|gocce|sciroppo) (di|del|della|dello|dei|delle|degli|non) /,
 / (dolore|male|peso|fitta) (forte |fortissimo |improvviso )?al petto /,/ pronto soccorso /,/ (battuto|battuta|batte|sbattuto|sbattuta|sbatte|picchiato|picchiata|picchia|preso un colpo|colpo) (la |alla |in |con la )?testa /,/ perde (molto |tanto )?sangue /,/ (esce|uscito) (molto |tanto )?sangue /,/ (vomita|vomitato|sputa|sputato|tossisce) (del )?sangue /,/ sangue (dal|dalla|dalle|nel|nelle|in) /,/ non risponde /,/ labbra (blu|viola) /,/ confus\w* (improvvis\w*|all improvviso) /,/ (improvvis\w*|all improvviso) confus\w* /,/ bocca storta /,/ (chiamo|chiamare) (il |l )?(112|118|ambulanza) /,/ 112 /,/ 118 /,/ ha (bevuto|mangiato) (la |il |un |una |del |della )?(candeggina|detersivo|medicin\w*|pastigli\w*|pillol\w*) /,/ non (mi )?riconosce /,/ parla (male|strano) /,/ si e (bruciat|ustionat|scottat)\w* /];
var SINT_FRASI=[/ attacco di panico /,/ macchie (rosse|sulla pelle|sul corpo) /,/ (sta|sto|stanno) (molto )?male /,/ gira la testa /];
/* parole di salute: scritte per intero, servono anche a perdonare un errore di una lettera («febre», «ingoito», «tachipirna») */
var URG_P='svenuto svenuta svenimento svenire svengo sviene convulsioni convulsione soffoca soffocando soffocamento ingoiato ingerito inghiottito avvelenamento avvelenato veleno bruciato bruciata ustione scottato scottata trauma botta emorragia incosciente ictus infarto paralisi annegato folgorato emergenza urgente urgenza caduta caduto cade cadere cadendo cascata cascato sbattuto ambulanza'.split(' ');
var SINT_P='febbre tosse vomito vomitato vomita diarrea raffreddore dolore mal male eruzione sfogo respiro dose dosi dosaggio tachipirina antibiotico paracetamolo ibuprofene gocce sciroppo supposta ferita sangue otite bronchite prurito influenza infezione allergia allergica pancia gola orecchio dentini puntura morso lividi livido gonfio gonfia sanguina catarro muco stitico stitichezza disidratato pallido formicolio vertigini'.split(' ');
var URG=URG_P.map(radice),SINT=SINT_P.map(radice);
/* parole normali che somigliano a parole di salute: non devono far scattare niente */
var NON_SINT=['allergolog','sanguign','febbrai'],FALSI=' tasse tassa colore colori corso corsi costa testo testi dolce dolci posta moto molle bollo bolla casse cassa caduco dosi nido male mali gole sole pacco '.split(' ');
function lev1(a,b){if(a===b)return true;var la=a.length,lb=b.length;if(Math.abs(la-lb)>1)return false;var i=0;while(i<la&&i<lb&&a[i]===b[i])i++;var x=la,y=lb;while(x>i&&y>i&&a[x-1]===b[y-1]){x--;y--}return x-i<=1&&y-i<=1}
function quasi(L,w){return w.length>=5&&FALSI.indexOf(w)<0&&L.some(function(p){return p.length>=5&&p[0]===w[0]&&lev1(p,w)})}
function tra(L,r){if(NON_SINT.some(function(n){return r.indexOf(n)===0}))return false;return L.some(function(s){return s.length<4||r.length<4?r===s:(r.indexOf(s)===0||(r.length>=5&&s.length-r.length<=2&&s.indexOf(r)===0))})}
function sintomo(r){return tra(SINT,r)||tra(URG,r)}
function pulisci(raw){return raw.replace(/ nn /g,' non ').replace(/ febbraio /g,' mese ').replace(/ (caduta|cadono|cade|caduti|cadere) (dei |i |il |di )?(dent\w+|capell\w+) /g,' denti ')}
function situazione(t){var raw=pulisci(' '+norm(t)+' '),W=raw.trim().split(' ').filter(function(w){return w.length>1}),T=W.map(radice);
 if(URG_FRASI.some(function(f){return f.test(raw)})||T.some(function(r){return tra(URG,r)})||W.some(function(w){return quasi(URG_P,w)}))return 2;
 if(T.some(function(r){return tra(SINT,r)})||W.some(function(w){return quasi(SINT_P,w)})||SINT_FRASI.some(function(f){return f.test(raw)}))return 1;
 return (!/ pidocch/.test(raw)&&/ (testa|petto|cuore|occhio|occhi|orecchie|schiena|stomaco) /.test(raw))?1:0} /* parti del corpo: parole intere, non radici («testa» non deve diventare «testo») */
/* parole che dicono «si parla di salute» anche senza un sintomo: se la guida manca, niente elenco di guide, solo a chi chiedere */
var SALUTE='pidocch malatt malat ammalat salut sintom cura curar guarir dottor medic pediatr ospedal vaccin gravid incint allatt svezz dent pelle occhi orecch peso cresc cammin parla mangi bere beve dorm sonn pannolin cacca pipi ciucc gattonar dermatit cicl mestruaz pressione glicemi diabet memori dimentic anzian nonn'.split(' ');
function diSalute(R){return R.some(function(r){return SALUTE.some(function(s){return r.indexOf(s)===0})})}
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
function cerca(t){var raw=pulisci(' '+norm(t)+' '),T=radici(raw),sint=situazione(t),R=T.filter(function(r){return !sintomo(r)});
 if(sint)return {sint:sint,sicura:false,esiti:[],R:R};
 if(!R.length)return {sint:0,sicura:false,esiti:[],R:R};
 var problema=/ (non|mai|sveglia|svegli\w*|piange|rifiuta|capricci|fatica|aiuto|cosa fare|come fare|come faccio|come si fa) /.test(raw),dato=/ (quant[oaie]|ore|quando|entro|scade|scadenza|vale|validita|dura|eta) /.test(raw);
 var m=mesi(t),fq=m===null?null:fasciaDi(m),out=[],df=R.map(function(){return 0});
 var anz=/ (nonn[oaie]|anzian\w*|suocer[oa]|mia madre|mio padre|mamma anziana|papa anziano|badante) /.test(raw),bimbo=m!==null&&m<216||/ (figli[oae]?|bimb[oaie]|bambin[oaie]|neonat[oaie]|piccol[oa]) /.test(raw);
 IDX.forEach(function(x){var s=0,k=0,forti=0;R.forEach(function(r,i){var p=punti(x,r);if(p){k++;s+=p;df[i]++;if(p>=4)forti++}});
  if(!k)return;s+=k*3;R.forEach(function(r){if(x.T.some(function(w){return simile(w,r)}))s+=2});
  if(problema&&!dato)s+=x.g==='dati'?-5:(x.k==='Guida'?2:0);if(dato&&x.g==='dati')s+=4;
  if(fq&&x.fa&&x.fa.indexOf(fq)>-1&&x.fa.length<5)s+=3;
  if(anz&&!bimbo)s+=x.c==='anziano'?3:(x.c==='bambino'?-4:0);if(bimbo&&!anz&&x.c==='anziano')s-=4;
  if(!anz&&CU.chi.length===1&&CU.chi[0]==='bambino'&&x.c==='anziano')s-=8; /* scelti solo bambini: niente guide per anziani */
  if(x.fr&&x.fr.some(function(f){return new RegExp(' '+f).test(raw)}))s+=9; /* modi di dire che portano a una guida precisa */
  s+=adatto(x.c,x.fa)*3;if(!dato&&!problema&&x.g==='dati')s-=1;if(x.k.indexOf('fonti')>-1)s-=3;else if(x.k!=='Pagina')s+=2;
  out.push({x:x,s:s,k:k,forti:forti})});
 out.sort(function(a,b){return b.s-a.s});
 var n=R.length,vuote=df.filter(function(v){return !v}).length,top=out[0],sicura=!!top&&top.forti>=1&&(n<=3?vuote===0:vuote<=1&&vuote<n/2)&&top.k>=Math.ceil(n*.6);
 var lim=top?top.s*.5:0;if(top&&top.s<=0)sicura=false;return {salute:diSalute(R),fq:fq,anz:anz,sint:0,sicura:sicura,esiti:out.filter(function(o){return o.s>=lim}).slice(0,sicura?4:3),R:R,dato:dato,problema:problema}}
function etaRiga(x,t){if(!x.eta)return '';var m=mesi(t),rows;
 if(m!==null)rows=x.eta.r.filter(function(r){return r[0]<=m&&m<=r[1]});else if(CU.eta.length)rows=x.eta.r.filter(function(r){return CU.eta.some(function(k){var f=FASCE[k];return r[0]<=f[1]&&r[1]>=f[0]})});else return '';
 return rows.map(function(r){return '<p class="eta"><b>'+esc(r[2])+':</b> '+esc(r[3])+(r[4]?'. <span class="small">'+esc(x.eta.c[2])+': '+esc(r[4])+'</span>':'')+'</p>'}).join('')}
function passo(x,R){if(!x.PS||!x.PS.length)return null;var best=0,bp=-1;x.PS.forEach(function(s,i){var p=0;R.forEach(function(r){if(s[0].some(function(w){return simile(w,r)}))p+=2;else if(s[1].some(function(w){return simile(w,r)}))p+=1});if(p>bp){bp=p;best=i}});return {i:best,s:x.ps[best],p:bp}}
function domande(E){var Dm=window.SERENA_DOMANDE;if(!Dm)return '';var NOME={'0-1':'meno di 1 anno','1-3':'1-3 anni','3-6':'3-6 anni','6-12':'6-12 anni','13-18':'13-18 anni','anziano':'persona anziana'};
 var K=E.anz?['anziano']:(E.fq?[E.fq]:CU.eta.slice().concat(CU.chi.indexOf('anziano')>-1?['anziano']:[]));if(!K.length)K=[''];K=K.slice(0,3);
 var tutte=[],per=K.length>1?2:5,h=K.map(function(k){var qs=[];(Dm.e[k]||Dm.e['']).forEach(function(i){Dm.t[i][1].forEach(function(q){if(qs.length<per&&tutte.indexOf(q)<0){qs.push(q);tutte.push(q)}})});
  return (k?'<p class="dq-k">Per '+(k==='anziano'?'una ':'chi ha ')+NOME[k]+'</p>':'')+'<ol>'+qs.map(function(q){return '<li>'+esc(q)+'</li>'}).join('')+'</ol>'}).join('');
 return '<div class="gesto dq"><span class="eyebrow">Domande pronte</span>'+h+'<button class="btn" type="button" data-porta="'+esc(JSON.stringify(tutte))+'" data-umami-event="cerca-domande-pronte">Portale in «Preparo la visita»</button></div>'}
function riga(x){return '<li><a class="rowl" href="'+esc(href(x.u))+'">'+(x.i?'<img src="'+esc(href(x.i))+'" alt="" width="64" height="64" loading="lazy">':'')+'<span class="t"><b>'+esc(x.t)+'</b><small>'+esc(x.k)+(x.m?' · '+x.m+' min':'')+'</small></span></a></li>'}
function mostra(){var t=Q.value.trim();if(!IDX){return}
 if(norm(t).length<2){OUT.innerHTML='';PRE.hidden=false;return}
 PRE.hidden=true;var E=cerca(t),h='';
 if(E.sint===2){
  h='<div class="avviso sicuro urgente"><p class="u112"><b>Se è un\'urgenza, chiama subito il 112.</b></p><a class="btn" href="tel:112" data-umami-event="cerca-urgenza-112">Chiama il 112</a><ul><li>Se non è urgente, chiama il pediatra o il medico di famiglia.</li><li>Di notte e nei giorni festivi c\'è la guardia medica.</li></ul><p class="small">Su sintomi, medicine e cadute Serena non dà indicazioni: non ha una guida da proporti qui.</p></div>';
 }else if(E.sint){
  h='<div class="avviso sicuro"><p><b>Su sintomi e medicine Serena non dà indicazioni.</b></p><ul><li>Chiama il pediatra o il medico di famiglia.</li><li>Di notte e nei giorni festivi c\'è la guardia medica.</li><li><b>Se è urgente, chiama il 112.</b></li></ul><p>Intanto puoi scrivere cosa hai notato, per raccontarlo bene.</p><a class="btn" href="'+esc(href('/strumenti/preparo-la-visita/'))+'" data-umami-event="cerca-sintomi-preparo">Apri «Preparo la visita»</a></div>';
 }else if(E.sicura){var x=E.esiti[0].x,ps=passo(x,E.R),er=(E.dato||x.g==='dati')?etaRiga(x,t):'';if(ps&&er)ps=null;else if(ps&&ps.p<2)ps={i:0,s:x.ps[0],p:0};
  h='<article class="risp vetro"><span class="chip">'+esc(x.k)+(x.m?' · '+x.m+' min':'')+'</span><h3>'+esc(x.t)+'</h3>'+er+
   (er?'<p>'+esc(x.d)+'</p>':'')+(ps?'<div class="gesto"><span class="eyebrow">'+(ps.i===0?'Per cominciare':'Il punto che cerchi')+'</span><p><b>'+esc(ps.s[0])+'.</b> '+esc(ps.s[1])+'</p></div>':(er?'':'<p>'+esc(x.d)+'</p>'))+
   (x.ag?'<p class="small">Dalla guida di Serena · fonti controllate il '+esc(x.ag)+'</p>':'')+
   (x.dq?domande(E):'')+'<a class="btn'+(x.dq?' btn-line':'')+'" href="'+esc(href(x.u)+(ps&&ps.i>0?'#passo-'+(ps.i+1):''))+'" data-umami-event="cerca-apri">'+esc(x.az||'Apri')+(x.m?' · '+x.m+' min':'')+'</a></article>';
  if(E.esiti.length>1)h+='<h2>Può servirti anche</h2><ul class="rows">'+E.esiti.slice(1).map(function(o){return riga(o.x)}).join('')+'</ul>';
 }else{
  if(E.salute){h='<div class="avviso manca"><p><b>Serena non ha ancora una guida su questo.</b></p><p>Per un dubbio di salute chiedi al pediatra o al medico di famiglia. <b>Se è urgente, chiama il 112.</b></p><a class="btn" href="tel:112" data-umami-event="cerca-manca-112">Chiama il 112</a><p class="small">Se vuoi, scrivi a privacy@serenainmente.it cosa cercavi: le prossime guide nascono così.</p></div>';OUT.innerHTML=h;return}
  h='<p class="avviso">Serena non ha ancora una guida su questo. Se vuoi, scrivilo a privacy@serenainmente.it: le prossime guide nascono così. <b>Se è urgente, chiama il 112.</b></p>';
  if(E.esiti.length)h+='<h2>Le più vicine</h2><ul class="rows">'+E.esiti.map(function(o){return riga(o.x)}).join('')+'</ul>';
  else h+='<h2>Le più cercate</h2><ul class="rows">'+IDX.filter(function(x){return x.top}).slice(0,4).map(riga).join('')+'</ul>';
  if(window.umami&&!F.dataset.vuota){F.dataset.vuota=1;try{umami.track('cerca-senza-esito')}catch(e){}}
 }
 OUT.innerHTML=h}
function apri(q){if(!F.open)F.showModal();if(q!==undefined)Q.value=q;Q.focus();
 if(!IDX&&!carica){carica=true;var s=d.createElement('script');s.src=F.dataset.src;s.onload=function(){IDX=window.SERENA_INDICE||[];prepara();mostra()};d.head.appendChild(s)}else mostra()}
Q.addEventListener('input',mostra);
Q.addEventListener('keydown',function(e){if(e.key==='Escape'){e.preventDefault();F.close()}});
OUT.addEventListener('click',function(e){var b=e.target.closest('[data-porta]');if(!b)return;var S0=lsj('serena:preparo-visita',{q:[],c:{}});S0.q=S0.q||[];JSON.parse(b.dataset.porta).forEach(function(t){if(!S0.q.some(function(q){return q.t===t}))S0.q.push({t:t,ok:false,r:''})});ls('serena:preparo-visita',JSON.stringify(S0));location.href=href('/strumenti/preparo-la-visita/')});
$('form',F).onsubmit=function(e){e.preventDefault();var a=$('.risp a.btn',OUT);if(a)location.href=a.href};
$('[data-chiudi]',F).onclick=function(){F.close()};
F.addEventListener('click',function(e){if(e.target===F)F.close()});
$$('[data-cerca]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();apri(b.dataset.cerca||undefined)})});
$$('[data-q]',F).forEach(function(b){b.onclick=function(){Q.value=b.dataset.q;mostra();Q.focus()}});
d.addEventListener('keydown',function(e){if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test((d.activeElement||{}).tagName||'')&&!e.metaKey&&!e.ctrlKey){e.preventDefault();apri()}});
var qp=new URLSearchParams(location.search).get('q');if(qp||location.hash==='#cerca')apri(qp||undefined);
window.SerenaCerca={apri:apri,situazione:situazione,prova:function(t){var E=cerca(t);return {sint:E.sint,sicura:E.sicura,u:E.esiti.map(function(o){return o.x.u})}}};
})();
