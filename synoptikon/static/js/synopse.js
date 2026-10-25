// Synopse: kolommen aan/uit, verslepen, vertaling kiezen. Voorkeuren in localStorage.
(function () {
  var balk = document.getElementById('synopse-balk');
  var synopse = document.getElementById('synopse');
  if (!balk || !synopse) return;
  var sleutel = 'synopse:' + (balk.dataset.vraag || '');
  var algemeen = 'synopse:*';

  function lees(k) { try { return JSON.parse(localStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function schrijf(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }

  var kolommen = function () { return Array.prototype.slice.call(synopse.querySelectorAll('.kolom')); };
  var schakels = Array.prototype.slice.call(balk.querySelectorAll('input[data-kolom]'));

  // Herstel: volgorde en zichtbaarheid (eerst per vraag, anders algemeen).
  var staat = lees(sleutel) || lees(algemeen) || {};
  if (staat.volgorde) {
    staat.volgorde.forEach(function (code) {
      var k = synopse.querySelector('.kolom[data-kolom="' + code + '"]');
      if (k) synopse.appendChild(k);
    });
  }
  if (staat.verborgen) {
    staat.verborgen.forEach(function (code) {
      var k = synopse.querySelector('.kolom[data-kolom="' + code + '"]');
      if (k) k.hidden = true;
      schakels.forEach(function (s) { if (s.dataset.kolom === code) s.checked = false; });
    });
  }
  if (staat.analyse === false) {
    document.body.classList.add('toon-analyse-uit');
    var ta = document.getElementById('toon-analyse'); if (ta) ta.checked = false;
  }

  function bewaar() {
    var s = {
      volgorde: kolommen().map(function (k) { return k.dataset.kolom; }),
      verborgen: kolommen().filter(function (k) { return k.hidden; }).map(function (k) { return k.dataset.kolom; }),
      analyse: !document.body.classList.contains('toon-analyse-uit')
    };
    schrijf(sleutel, s); schrijf(algemeen, s);
  }

  schakels.forEach(function (s) {
    s.addEventListener('change', function () {
      var k = synopse.querySelector('.kolom[data-kolom="' + s.dataset.kolom + '"]');
      if (k) k.hidden = !s.checked;
      bewaar();
    });
  });
  // Rechtsfamilie: alle kolommen van de familie tegelijk aan of uit.
  Array.prototype.slice.call(balk.querySelectorAll('.familie-knop')).forEach(function (knop) {
    knop.addEventListener('click', function () {
      var leden = schakels.filter(function (s) { return s.dataset.familie === knop.dataset.familie; });
      var aan = !leden.every(function (s) { return s.checked; });
      leden.forEach(function (s) {
        s.checked = aan;
        var k = synopse.querySelector('.kolom[data-kolom="' + s.dataset.kolom + '"]');
        if (k) k.hidden = !aan;
      });
      bewaar();
    });
  });
  var toonAnalyse = document.getElementById('toon-analyse');
  if (toonAnalyse) toonAnalyse.addEventListener('change', function () {
    document.body.classList.toggle('toon-analyse-uit', !toonAnalyse.checked); bewaar();
  });

  var vertaal = document.getElementById('vertaal-keuze');
  if (vertaal) vertaal.addEventListener('change', function () {
    var url = new URL(window.location.href);
    if (vertaal.value) url.searchParams.set('vertaling', vertaal.value); else url.searchParams.delete('vertaling');
    window.location.href = url.toString();
  });

  // Slepen van kolomkoppen (HTML5 drag & drop; op touch valt dit weg, daar staat de volgorde vast).
  var gesleept = null;
  synopse.addEventListener('dragstart', function (e) {
    var kop = e.target.closest('.kolomkop'); if (!kop) return;
    gesleept = kop.closest('.kolom'); gesleept.classList.add('sleept');
    e.dataTransfer.effectAllowed = 'move';
    try { e.dataTransfer.setData('text/plain', gesleept.dataset.kolom); } catch (err) {}
  });
  synopse.addEventListener('dragover', function (e) {
    var doel = e.target.closest('.kolom'); if (!doel || !gesleept || doel === gesleept) return;
    e.preventDefault();
    kolommen().forEach(function (k) { k.classList.remove('doel'); });
    doel.classList.add('doel');
  });
  synopse.addEventListener('dragleave', function (e) { var k = e.target.closest('.kolom'); if (k) k.classList.remove('doel'); });
  synopse.addEventListener('drop', function (e) {
    var doel = e.target.closest('.kolom'); if (!doel || !gesleept || doel === gesleept) return;
    e.preventDefault();
    var alle = kolommen();
    if (alle.indexOf(gesleept) < alle.indexOf(doel)) doel.after(gesleept); else doel.before(gesleept);
    bewaar();
  });
  synopse.addEventListener('dragend', function () {
    kolommen().forEach(function (k) { k.classList.remove('doel', 'sleept'); }); gesleept = null;
  });
})();
