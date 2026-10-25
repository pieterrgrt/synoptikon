// Algemeen: thema-schakelaar en bevestigingsdialogen. Geen afhankelijkheden.
(function () {
  var root = document.documentElement;
  var knop = document.getElementById('thema-knop');
  function huidig() {
    var t = root.dataset.theme;
    if (t === 'auto' || !t) return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    return t;
  }
  if (knop) {
    knop.addEventListener('click', function () {
      var nieuw = huidig() === 'dark' ? 'light' : 'dark';
      root.dataset.theme = nieuw;
      try { localStorage.setItem('thema', nieuw); } catch (e) {}
      if (window.zetFavicon) window.zetFavicon();
    });
  }
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f.dataset && f.dataset.bevestig && !window.confirm(f.dataset.bevestig)) e.preventDefault();
  });
  // Formulieren die bij wijziging direct verzenden (filters, keuzelijsten).
  document.addEventListener('change', function (e) {
    var el = e.target;
    if (el.matches && el.matches('select.auto-submit') && el.form) el.form.submit();
    // Stelselkeuze → taalveld invullen en systematiek-opties filteren.
    if (el.matches && el.matches('select[name="stelsel_code"]')) {
      var opt = el.selectedOptions[0], form = el.form;
      if (!form || !opt) return;
      var taal = form.querySelector('input[name="taal"]');
      if (taal && opt.dataset.taal) { if (taal.classList.contains('taal-veld')) taal.placeholder = opt.dataset.taal; else taal.value = opt.dataset.taal; }
      filterSystematiek(form, el.value);
    }
  });
  function filterSystematiek(form, code) {
    var sys = form.querySelector('select[name="systematiek_id"]');
    if (!sys) return;
    Array.prototype.forEach.call(sys.options, function (o) { if (o.value) o.hidden = o.dataset.stelsel !== code; });
    if (sys.selectedOptions[0] && sys.selectedOptions[0].hidden) sys.value = '';
  }
  document.querySelectorAll('form select[name="stelsel_code"]').forEach(function (s) { filterSystematiek(s.form, s.value); });
  // Sluit open menu's bij klik erbuiten.
  document.addEventListener('click', function (e) {
    document.querySelectorAll('details.menu[open]').forEach(function (d) { if (!d.contains(e.target)) d.removeAttribute('open'); });
  });
})();
