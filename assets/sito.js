/* serenainmente.it — tutto quello che si muove nel sito. Niente arriva a un server:
   ricerca, cose salvate, spunte e preferenze restano nel browser di chi legge. */
(function(){
var d=document,H=d.documentElement;
function $(s,r){return (r||d).querySelector(s)}
function $$(s,r){return [].slice.call((r||d).querySelectorAll(s))}
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);if(v===null)localStorage.removeItem(k);else localStorage.setItem(k,v)}catch(x){return null}}
function lsj(k,def){try{return JSON.parse(ls(k))||def}catch(x){return def}}
function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var TT;function toast(t){var o=$('.toast');if(o)o.remove();clearTimeout(TT);var e=d.createElement('div');e.className='toast';e.setAttribute('role','status');e.textContent=t;d.body.appendChild(e);TT=setTimeout(function(){e.remove()},2600)}
var ridotto=matchMedia('(prefers-reduced-motion: reduce)').matches;

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
 $$('[data-sharetext]').forEach(function(b){b.hidden=false;b.onclick=function(){navigator.share({text:b.dataset.sharetext}).catch(function(){})}});
}
$$('[data-copytext]').forEach(function(b){b.onclick=function(){navigator.clipboard&&navigator.clipboard.writeText(b.dataset.copytext).then(function(){toast(b.dataset.done||'Copiato')})}});

/* lista da spuntare, con l'anello che dice quanto manca */
$$('.ck').forEach(function(box){
 var cs=$$('input[data-ck]',box),N=$('[data-ckn]',box),Z=$('[data-ckreset]',box),V=$('.anello .v',box),armed=false;
 function upd(){var n=cs.filter(function(c){return c.checked}).length;
  if(N)N.textContent=n?(n===cs.length?'Tutto fatto: '+n+' su '+n:n+' su '+cs.length+' fatte'):cs.length+' cose, una alla volta';
  if(V)V.style.strokeDashoffset=125.7*(1-n/cs.length);if(Z)Z.hidden=!n}
 cs.forEach(function(c){var k='ck:'+c.dataset.ck;c.checked=ls(k)==='1';c.onchange=function(){ls(k,c.checked?'1':'0');upd()}});
 if(Z)Z.onclick=function(){if(!armed){armed=true;Z.textContent='Tocca di nuovo per azzerare';setTimeout(function(){armed=false;Z.textContent='Azzera le spunte'},4000);return}
  cs.forEach(function(c){c.checked=false;ls('ck:'+c.dataset.ck,'0')});armed=false;Z.textContent='Azzera le spunte';upd()};
 var P=$('[data-stampa-lista]',box);if(P)P.onclick=function(){d.body.classList.add('solo-lista');print()};
 var I=$('[data-ics]',box);if(I)I.onclick=function(){
  var t=new Date();t.setDate(t.getDate()+1);function p(n){return (n<10?'0':'')+n}
  var day=''+t.getFullYear()+p(t.getMonth()+1)+p(t.getDate()),n=new Date(),st=n.getUTCFullYear()+p(n.getUTCMonth()+1)+p(n.getUTCDate())+'T'+p(n.getUTCHours())+p(n.getUTCMinutes())+'00Z';
  function e(s){return s.replace(/\\/g,'\\\\').replace(/([,;])/g,'\\$1').replace(/\n/g,'\\n')}
  var voci=cs.map(function(c){return (c.checked?'[x] ':'[ ] ')+c.closest('label').textContent.trim()}).join('\n');
  var ics=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//serenainmente.it//IT','BEGIN:VEVENT','UID:'+Date.now()+'@serenainmente.it','DTSTAMP:'+st,'DTSTART:'+day+'T090000','DURATION:PT15M','SUMMARY:'+e(box.dataset.titolo),'DESCRIPTION:'+e(voci+'\n'+box.dataset.url),'URL:'+box.dataset.url,'BEGIN:VALARM','ACTION:DISPLAY','DESCRIPTION:'+e(box.dataset.titolo),'TRIGGER:PT0M','END:VALARM','END:VEVENT','END:VCALENDAR'].join('\r\n');
  var a=d.createElement('a');a.href=URL.createObjectURL(new Blob([ics],{type:'text/calendar'}));a.download='promemoria-serena.ics';d.body.appendChild(a);a.click();a.remove();toast('Promemoria per domattina alle 9')};
 upd()});
addEventListener('afterprint',function(){d.body.classList.remove('solo-lista')});

/* «Salva per dopo»: resta in questo browser */
function salvati(){return lsj('serena:salvati',[])}
$$('[data-salva]').forEach(function(b){var u=b.dataset.salva,t=b.dataset.title;
 function st(){var on=salvati().some(function(x){return x.u===u});b.setAttribute('aria-pressed',on);$('span',b).textContent=on?'Salvata per dopo':'Salva per dopo'}
 b.hidden=false;b.onclick=function(){var L=salvati(),i=-1;L.forEach(function(x,k){if(x.u===u)i=k});if(i>-1)L.splice(i,1);else L.unshift({u:u,t:t});ls('serena:salvati',JSON.stringify(L.slice(0,12)));st();toast(i>-1?'Tolta dalle cose salvate':'Serena la tiene da parte: la ritrovi nella pagina iniziale')};st()});
function href(u){var B=d.body.dataset.base||'/';return d.body.dataset.rel?B+u.slice(1)+(u.slice(-1)==='/'?'index.html':''):u}
var SV=$('[data-salvati]');
if(SV){var L=salvati();if(L.length){SV.hidden=false;$('h2',SV).textContent=L.length===1?'Serena ti ha tenuto da parte una cosa':'Serena ti ha tenuto da parte '+L.length+' cose';
 $('ul',SV).innerHTML=L.map(function(x){return '<li><a class="rowl" href="'+esc(href(x.u))+'"><span class="t"><b>'+esc(x.t)+'</b></span></a></li>'}).join('')}}

/* «Di chi ti prendi cura»: mette in cima quello che serve. Resta in questo browser */
var CU=lsj('serena:cura',{chi:[],eta:''});
function fascia(){var m={'0-1':[0,11],'1-3':[12,47],'3-6':[36,83],'6-12':[72,155],'13-18':[156,227]}[CU.eta];return m||null}
var PT=$('.per-te');
if(PT){PT.hidden=false;var EB=$('[data-eta-box]',PT),DM=$('[data-dimentica]',PT);
 function pt(){$$('[data-cura]',PT).forEach(function(b){b.setAttribute('aria-pressed',CU.chi.indexOf(b.dataset.cura)>-1)});
  $$('[data-eta]',PT).forEach(function(b){b.setAttribute('aria-pressed',CU.eta===b.dataset.eta)});
  EB.hidden=CU.chi.indexOf('bambino')<0;DM.hidden=!CU.chi.length;
  var R=$$('[data-partenze] li'),n=0;R.forEach(function(li){var t=li.dataset.tag,ok=!CU.chi.length?li.dataset.base==='1':(CU.chi.some(function(c){return t.indexOf(c)>-1}));
   if(ok&&CU.chi.length===1&&CU.chi[0]==='anziano'&&t.indexOf('anziano')<0)ok=false;li.hidden=!ok||n>=4;if(ok)n++})}
 $$('[data-cura]',PT).forEach(function(b){b.onclick=function(){var i=CU.chi.indexOf(b.dataset.cura);if(i>-1)CU.chi.splice(i,1);else CU.chi.push(b.dataset.cura);if(CU.chi.indexOf('bambino')<0)CU.eta='';ls('serena:cura',JSON.stringify(CU));pt()}});
 $$('[data-eta]',PT).forEach(function(b){b.onclick=function(){CU.eta=CU.eta===b.dataset.eta?'':b.dataset.eta;ls('serena:cura',JSON.stringify(CU));pt()}});
 DM.onclick=function(){CU={chi:[],eta:''};ls('serena:cura',null);pt();toast('Fatto: Serena non lo ricorda più')};
 pt()}
/* nelle tabelle per età, la riga che riguarda chi legge */
(function(){var f=fascia();if(!f)return;var n=0;$$('tr[data-eta]').forEach(function(tr){var p=tr.dataset.eta.split('-');if(+p[0]<=f[1]&&+p[1]>=f[0]){tr.classList.add('tua');n++}});
 if(n)$$('[data-tua-n]').forEach(function(x){x.hidden=false})})();

/* filtri per argomento nell'elenco delle guide */
var grid=$('[data-grid]');
if(grid){var chips=$$('[data-arg]'),cur='tutti',h=location.hash.slice(1);
 if(chips.some(function(c){return c.dataset.arg===h}))cur=h;
 function run(){$$('[data-a]',grid).forEach(function(c){c.hidden=!(cur==='tutti'||c.dataset.a===cur)});chips.forEach(function(ch){ch.setAttribute('aria-pressed',ch.dataset.arg===cur)})}
 chips.forEach(function(ch){ch.onclick=function(){cur=ch.dataset.arg;history.replaceState(null,'',cur==='tutti'?location.pathname:'#'+cur);run()}});run()}

/* anteprima del foglio da vicino */
$$('[data-zoom]').forEach(function(b){var D=$('dialog.zoom');if(!D||!D.showModal)return;b.onclick=function(){D.showModal()};$('.x',D).onclick=function(){D.close()}});

/* ---------- la ricerca: capisce frasi e parole di tutti i giorni, tutto in locale ---------- */
var F=$('#cerca');if(!F||!F.showModal)return;
var Q=$('input',F),OUT=$('[data-esiti]',F),PRE=$('[data-prima]',F),IDX=null,carica=false;
var STOP=' il lo la i gli le un uno una di a da in con su per tra fra e ed o ma che chi non mi ti si ci vi ne ho hai ha abbiamo hanno sono sei come cosa cose quando dove quanto quanta quanti quante perche del dello della dei delle degli al allo alla ai alle dal dalla nel nella sul sulla mio mia miei mie tuo tua suo sua nostro nostra figlio figlia figli bambino bambina bambini bimbo bimba piccolo piccola oggi stasera stanotte adesso ora devo deve posso puo vuole voglio fare fa faccio serve servono anni anno mesi mese settimane giorni piu molto poco sempre mai ancora gia anche solo ogni tutto tutti questa questo essere avere '.split(' ');
function norm(x){return (x||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,' ').trim()}
var SUF=['azione','azioni','izione','izioni','amento','amenti','mente','ando','endo','iamo','are','ere','ire','ato','ata','ati','ate','uto','uta','ito','ita','ano','ono','ale','ali'];
function radice(w){if(w.length<=4)return w;for(var i=0;i<SUF.length;i++){var s=SUF[i];if(w.length-s.length>=4&&w.slice(-s.length)===s)return w.slice(0,-s.length)}var r=w.replace(/[aeiou]+$/,'');return r.length>=3?r:w}
function radici(t){return norm(t).split(' ').filter(function(w){return w.length>1&&STOP.indexOf(w)<0&&!/^\d+$/.test(w)}).map(radice)}
function simile(a,b){if(a.length<4||b.length<4)return a===b;return a.indexOf(b)===0||b.indexOf(a)===0}
/* parole diverse, stessa cosa */
var GR=['dorm sonn nann addorment svegl risvegl sonnellin pisolin nott lett','sera serat routin buonanott','pediatr dottor dottoress medic visit ambulator controll bilanc','specialist allergolog gastroenterolog diabetolog dermatolog oculist ortoped logoped impegnativ ricett cup prenot attes','disd spost annull rimand cancell ticket pag cup sald','document cart tesser refert fascicol fse spid librett certificat modul esam analis grupp','vaccin richiam librett','scuol nido asil matern infanz iscr iscriv element primar','anzian nonn genitor madr padr mamm papa badant medicin farmac pastigl pillol compress terap','identit cie passaport espatr viagg','organizz settiman planner calendar scadenz impegn gestional promemor ricord agend','stamp pdf fogl scaric'].map(function(g){return g.split(' ')});
function gruppi(r){var o=[];GR.forEach(function(g,i){if(g.some(function(m){return simile(m,r)}))o.push(i)});return o}
/* sintomi e medicine: Serena non risponde, indica a chi chiedere */
var SINT='febbr toss vomit diarre raffredd dolor mal eruzion sfog respir convuls cadut dos dose dosi dosagg tachipirin antibiotic paracetamol ibuprofen gocc sciropp suppost ferit ustion sangue svenut'.split(' ');
function prepara(){IDX.forEach(function(x){x.A=radici(x.a);x.B=radici(x.b);x.GA=[];x.GB=[];x.A.forEach(function(r){gruppi(r).forEach(function(g){if(x.GA.indexOf(g)<0)x.GA.push(g)})});x.B.forEach(function(r){gruppi(r).forEach(function(g){if(x.GB.indexOf(g)<0)x.GB.push(g)})})})}
function cerca(t){var R=radici(t);if(!R.length)return [];var out=[];
 IDX.forEach(function(x){var s=0,k=0;R.forEach(function(r){var p=0;
   if(x.A.some(function(w){return simile(w,r)}))p=6;else if(x.B.some(function(w){return simile(w,r)}))p=2;
   var g=gruppi(r);if(g.some(function(i){return x.GA.indexOf(i)>-1}))p=Math.max(p,4);else if(!p&&g.some(function(i){return x.GB.indexOf(i)>-1}))p=1;
   if(p){k++;s+=p}});
  if(k)out.push({x:x,s:s+k*3+(x.k==='Guida'?.5:0),k:k})});
 out.sort(function(a,b){return b.s-a.s});var top=out.length?out[0].s:0;
 return out.filter(function(o){return o.s>=top*.45}).slice(0,5)}
function mesi(t){var m=/(\d{1,2})\s*(mes|ann|settiman|giorn)/.exec(norm(t));if(!m)return null;var n=+m[1];return m[2]==='ann'?n*12:m[2]==='mes'?n:0}
function etaRiga(x,t){if(!x.eta)return '';var m=mesi(t),f=fascia(),rows;
 if(m!==null)rows=x.eta.r.filter(function(r){return r[0]<=m&&m<=r[1]});else if(f)rows=x.eta.r.filter(function(r){return r[0]<=f[1]&&r[1]>=f[0]});else return '';
 return rows.map(function(r){return '<p class="eta">'+esc(x.eta.c[1])+', '+esc(r[2])+': '+esc(r[3])+(r[4]?' <span class="small">('+esc(x.eta.c[2])+': '+esc(r[4])+')</span>':'')+'</p>'}).join('')}
function riga(x){return '<li><a class="rowl" href="'+esc(href(x.u))+'">'+(x.i?'<img src="'+esc(href(x.i))+'" alt="" width="64" height="64" loading="lazy">':'')+'<span class="t"><b>'+esc(x.t)+'</b><small>'+esc(x.k)+(x.m?' · '+x.m+' min':'')+'</small></span></a></li>'}
function mostra(){var t=Q.value.trim();if(!IDX){return}
 if(norm(t).length<2){OUT.innerHTML='';PRE.hidden=false;return}
 PRE.hidden=true;var R=cerca(t),h='',sint=radici(t).some(function(r){return SINT.some(function(s){return s.length<4?r===s:r.indexOf(s)===0})});
 if(sint)h+='<p class="avviso"><b>Su sintomi e medicine Serena non dà indicazioni:</b> per quelli c\'è il pediatra o il medico. Se è urgente, chiama il 112. Serena può aiutarti a preparare la visita. <a href="'+esc(href('/strumenti/preparo-la-visita/'))+'">Apri «Preparo la visita»</a></p>';
 if(R.length){var x=R[0].x;
  h+='<article class="risp vetro"><span class="chip">'+esc(x.k)+(x.m?' · '+x.m+' min':'')+'</span><h3>'+esc(x.t)+'</h3>'+etaRiga(x,t)+'<p>'+esc(x.d)+'</p>'+(x.p&&x.p.length?'<ol>'+x.p.slice(0,5).map(function(p){return '<li>'+esc(p)+'</li>'}).join('')+'</ol>':'')+'<a class="btn" href="'+esc(href(x.u))+'" data-umami-event="cerca-apri">'+esc(x.az||'Apri')+'</a></article>';
  if(R.length>1)h+='<h2>Può servirti anche</h2><ul class="rows">'+R.slice(1).map(function(o){return riga(o.x)}).join('')+'</ul>';
 }else if(!sint){
  h+='<p class="avviso">Serena non ha ancora una guida su questo. Scrivile cosa cercavi con un messaggio su Instagram: le prossime guide nascono così.</p><h2>Intanto, le più cercate</h2><ul class="rows">'+IDX.filter(function(x){return x.top}).slice(0,4).map(riga).join('')+'</ul>';
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
window.SerenaCerca={apri:apri,prova:function(t){return cerca(t).map(function(o){return o.x.u})}};
})();
