// Voorstellen beoordelen: de knoppen sturen het besluit zonder de pagina te herladen, vegen doet hetzelfde
// (rechts = overnemen, links = afwijzen), en 'ongedaan maken' zet de kaart terug. Zonder JavaScript werken de formulieren.
(function () {
  var el = document.getElementById('voorstel-i18n');
  if (!el) return;
  var t = JSON.parse(el.textContent);
  function stuur(kaart, besluit) {
    return fetch('/leren/kaart/' + kaart.dataset.kaart + '/beoordeel', {
      method: 'POST', body: new URLSearchParams({ besluit: besluit }), credentials: 'same-origin',
      headers: { 'X-Requested-With': 'fetch' }
    }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  function tel(groep) {
    var n = groep.querySelectorAll('.voorstel:not(.besloten)').length;
    var teller = groep.querySelector('[data-teller]');
    if (teller) teller.textContent = n;
  }
  function besluit(kaart, wat) {
    kaart.style.transform = '';
    stuur(kaart, wat).then(function () {
      kaart.classList.add('besloten');
      kaart.querySelector('[data-uitslag]').textContent = t[wat] || wat;
      tel(kaart.closest('[data-groep]'));
    }).catch(function () {});
  }
  document.querySelectorAll('.voorstel').forEach(function (kaart) {
    kaart.querySelectorAll('.voorstel-knoppen form').forEach(function (f) {
      f.addEventListener('submit', function (e) { e.preventDefault(); besluit(kaart, f.elements.besluit.value); });
    });
    kaart.querySelector('[data-terug]').addEventListener('click', function () {
      stuur(kaart, 'terug').then(function () { kaart.classList.remove('besloten'); tel(kaart.closest('[data-groep]')); });
    });
    // Vegen: meer dan 90 px opzij, en duidelijk meer opzij dan omhoog (anders is het scrollen).
    var x0 = null, y0 = 0, dx = 0;
    kaart.addEventListener('touchstart', function (e) {
      if (kaart.classList.contains('besloten') || e.target.closest('a, button, summary')) return;
      x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; dx = 0;
    }, { passive: true });
    kaart.addEventListener('touchmove', function (e) {
      if (x0 === null) return;
      dx = e.touches[0].clientX - x0;
      if (Math.abs(e.touches[0].clientY - y0) > Math.abs(dx)) { x0 = null; kaart.style.transform = ''; return; }
      kaart.style.transform = 'translateX(' + dx + 'px)';
    }, { passive: true });
    kaart.addEventListener('touchend', function () {
      if (x0 === null) return;
      x0 = null;
      if (Math.abs(dx) > 90) besluit(kaart, dx > 0 ? 'over' : 'af');
      else kaart.style.transform = '';
    });
  });
})();
