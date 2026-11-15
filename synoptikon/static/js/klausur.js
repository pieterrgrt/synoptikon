// Klausurtrainer: het werkblad (tabs op de telefoon, klok, automatisch bewaren, wettekst opzoeken) en de knop
// 'kaartvoorstel'. Zonder JavaScript werken de formulieren: Bewaren en Inleveren zijn gewone knoppen.
(function () {
  // Kaartvoorstel zonder de pagina te herladen.
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f.matches || !f.matches('form[data-kaartknop]')) return;
    e.preventDefault();
    fetch(f.action, { method: 'POST', body: new URLSearchParams(new FormData(f)), credentials: 'same-origin', headers: { 'X-Requested-With': 'fetch' } })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) {
        var p = document.createElement('p');
        p.className = 'klein kaartknop';
        var a = document.createElement('a');
        a.href = '/leren/voorstellen' + (d.lijst ? '?lijst=' + d.lijst : '');
        a.textContent = f.dataset.klaar;
        p.appendChild(a);
        f.replaceWith(p);
      }).catch(function () { f.submit(); });
  });

  var wb = document.getElementById('wb');
  if (!wb) return;
  var form = document.getElementById('werkblad');
  var skizze = document.getElementById('skizze'), uitwerking = document.getElementById('uitwerking');
  var stand = document.getElementById('bewaard-stand'), melding = document.getElementById('wb-melding');
  var revisie = parseInt(wb.dataset.revisie, 10) || 0;
  var sleutel = 'klausur-' + wb.dataset.poging;
  var vuil = false, bezig = false, gestopt = false;

  // --- tabs: op een smal scherm één paneel tegelijk
  var tabs = document.querySelectorAll('.wb-tabs a');
  function toon(naam) {
    wb.dataset.actief = naam;
    tabs.forEach(function (t) { if (t.dataset.paneel === naam) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current'); });
    try { sessionStorage.setItem(sleutel + '-tab', naam); } catch (e) {}
  }
  document.body.classList.add('wb-js');
  tabs.forEach(function (t) { t.addEventListener('click', function (e) { e.preventDefault(); toon(t.dataset.paneel); }); });
  var eerder = null;
  try { eerder = sessionStorage.getItem(sleutel + '-tab'); } catch (e) {}
  toon(eerder || 'sachverhalt');

  // --- woorden tellen
  var teller = document.getElementById('woorden');
  function tel() { if (teller) teller.textContent = (uitwerking.value.trim() ? uitwerking.value.trim().split(/\s+/).length : 0) + ' W.'; }
  tel();

  // --- kopie op dit apparaat: bij een verbroken verbinding of een dichtgeklapte telefoon gaat niets verloren
  function lokaal() { try { localStorage.setItem(sleutel, JSON.stringify({ s: skizze.value, u: uitwerking.value, t: Date.now() })); } catch (e) {} }
  try {
    var kopie = JSON.parse(localStorage.getItem(sleutel) || 'null');
    if (kopie && kopie.t > (parseInt(wb.dataset.bewaard, 10) || 0) && (kopie.s !== skizze.value || kopie.u !== uitwerking.value)) {
      skizze.value = kopie.s; uitwerking.value = kopie.u; vuil = true; tel();
      stand.textContent = wb.dataset.tTerug;
    }
  } catch (e) {}

  function bewaar(klaar) {
    if (bezig || gestopt) { if (klaar) klaar(false); return; }
    bezig = true; vuil = false;
    stand.textContent = wb.dataset.tBezig;
    var body = new URLSearchParams({ skizze: skizze.value, uitwerking: uitwerking.value, revisie: String(revisie) });
    fetch(form.action, { method: 'POST', body: body, credentials: 'same-origin', headers: { 'X-Requested-With': 'fetch' } })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (x) {
        bezig = false;
        if (x.ok) {
          revisie = x.d.revisie;
          var nu = new Date();
          stand.textContent = wb.dataset.tBewaard + ' ' + ('0' + nu.getHours()).slice(-2) + ':' + ('0' + nu.getMinutes()).slice(-2);
          if (!vuil) { try { localStorage.removeItem(sleutel); } catch (e) {} }
          if (typeof x.d.rest === 'number') zetRest(x.d.rest);
        } else if (x.d && x.d.conflict) {
          gestopt = true; melding.textContent = wb.dataset.tConflict; melding.hidden = false;
        } else if (x.d && x.d.ingeleverd) {
          gestopt = true; location.reload();
        }
        if (klaar) klaar(x.ok);
      }).catch(function () { bezig = false; vuil = true; stand.textContent = wb.dataset.tOffline; if (klaar) klaar(false); });
  }
  [skizze, uitwerking].forEach(function (el) { el.addEventListener('input', function () { vuil = true; lokaal(); tel(); }); });
  setInterval(function () { if (vuil) bewaar(); }, 20000);
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'hidden' && vuil) bewaar(); });
  document.getElementById('bewaar-knop').addEventListener('click', function (e) { e.preventDefault(); bewaar(); });
  var inlever = document.getElementById('inlever-knop');
  inlever.addEventListener('click', function (e) {
    if (!window.confirm(inlever.dataset.vraag)) { e.preventDefault(); return; }
    try { localStorage.removeItem(sleutel); } catch (err) {}
  });

  // --- invoegen in de skizze
  document.querySelectorAll('[data-voeg]').forEach(function (knop) {
    knop.addEventListener('click', function () {
      var a = skizze.selectionStart, tekst = skizze.value;
      var voor = tekst.slice(0, a), na = tekst.slice(skizze.selectionEnd);
      var stuk = (voor && !/\n$/.test(voor) ? '\n' : '') + knop.dataset.voeg + '\n';
      skizze.value = voor + stuk + na;
      skizze.selectionStart = skizze.selectionEnd = (voor + stuk).length;
      skizze.focus(); vuil = true; lokaal();
    });
  });

  // --- klok: de server telt; hier alleen aftellen vanaf wat de server zei
  var klok = document.getElementById('klok'), eind = null;
  function zetRest(s) { eind = Date.now() + s * 1000; }
  function tik() {
    if (eind === null) return;
    var s = Math.max(0, Math.round((eind - Date.now()) / 1000));
    var u = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), sec = s % 60;
    klok.textContent = u + ':' + ('0' + m).slice(-2) + (s < 600 ? ':' + ('0' + sec).slice(-2) : '');
    klok.classList.toggle('krap', s < 600);
    if (s === 0 && !gestopt) {
      gestopt = true; eind = null;
      melding.textContent = wb.dataset.tOm; melding.hidden = false;
      try { localStorage.removeItem(sleutel); } catch (e) {}
      form.action = form.action.replace(/bewaar$/, 'inleveren');
      form.submit();
    }
  }
  if (klok) { zetRest(parseInt(klok.dataset.rest, 10) || 0); tik(); setInterval(tik, 1000); }

  // --- wettekst
  var zoek = document.getElementById('wet-zoek'), uit = document.getElementById('wet-uit');
  function haal(q) {
    if (!q) return;
    uit.textContent = '…';
    fetch('/klausur/wet?fragment=1&q=' + encodeURIComponent(q), { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then(function (html) { uit.innerHTML = html; }).catch(function () { uit.textContent = ''; });
  }
  zoek.addEventListener('submit', function (e) { e.preventDefault(); haal(zoek.elements.q.value.trim()); });
  uit.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-wet]');
    if (a) { e.preventDefault(); zoek.elements.q.value = a.dataset.wet; haal(a.dataset.wet); }
  });
})();
