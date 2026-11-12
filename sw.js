// serenainmente.it — le pagine già aperte o salvate si rileggono anche senza rete (per esempio in ambulatorio).
// Non installa niente e non mostra inviti: tiene solo una copia nel browser. Si registra a pagina già caricata.
const C = 'serena-pagine-1';
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== C).map(n => caches.delete(n)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url); if (u.origin !== location.origin) return;            // niente di esterno (Umami compreso)
  if (/\.(mp4|xlsx)$/.test(u.pathname) || r.headers.has('range')) return;         // file grossi: sempre dalla rete
  if (r.mode === 'navigate') {                                                    // pagine: prima la rete, senza rete la copia
    e.respondWith(fetch(r).then(x => { if (x.ok) { const c = x.clone(); caches.open(C).then(k => k.put(u.pathname, c)); } return x; })
      .catch(() => caches.match(u.pathname).then(x => x || caches.match('/'))));
    return;
  }
  e.respondWith(caches.match(r).then(x => {                                       // stile, script, immagini: subito la copia, e intanto si aggiorna
    const rete = fetch(r).then(y => { if (y.ok) { const c = y.clone(); caches.open(C).then(k => k.put(r, c)); } return y; }).catch(() => x);
    return x || rete;
  }));
});
self.addEventListener('message', e => { if (e.data && e.data.salva) caches.open(C).then(k => Promise.all(e.data.salva.map(u => fetch(u).then(x => x.ok && k.put(u, x)).catch(() => {})))); });
