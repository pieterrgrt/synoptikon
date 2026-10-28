// Oefenen: kaart na kaart omdraaien en 'gekend / nog niet' doorgeven. Geen planning (die doet Wunderkammer).
(function () {
  var box = document.getElementById('oefenen');
  if (!box) return;
  var kaarten = JSON.parse(document.getElementById('kaarten-data').textContent);
  var t = JSON.parse(document.getElementById('oefen-i18n').textContent);
  function fmt(s, w) { return s.replace(/\{(\w+)\}/g, function (_, k) { return w[k]; }); }
  // Door elkaar (Fisher-Yates).
  for (var i = kaarten.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var x = kaarten[i]; kaarten[i] = kaarten[j]; kaarten[j] = x; }
  var $ = function (id) { return document.getElementById(id); };
  var pos = 0, gekend = 0, omgedraaid = false;
  function toon() {
    if (pos >= kaarten.length) return klaar();
    var k = kaarten[pos];
    omgedraaid = false;
    $('flits-soort').textContent = k.soort;
    $('flits-voor').innerHTML = k.voor;
    $('flits-achter').innerHTML = k.achter;
    $('flits-achter').hidden = true;
    $('knoppen-voor').hidden = false;
    $('knoppen-achter').hidden = true;
    $('flits-link').hidden = true;
    if (k.url) $('flits-link').href = k.url;
    $('oefen-teller').textContent = fmt(t.van, { i: pos + 1, n: kaarten.length });
    $('oefen-balk').style.width = (100 * pos / kaarten.length) + '%';
    $('flits').focus({ preventScroll: true });
  }
  function draai() {
    if (omgedraaid || pos >= kaarten.length) return;
    omgedraaid = true;
    $('flits-achter').hidden = false;
    $('knoppen-voor').hidden = true;
    $('knoppen-achter').hidden = false;
    $('flits-link').hidden = !kaarten[pos].url;
  }
  function antwoord(ok) {
    if (!omgedraaid) return;
    var k = kaarten[pos];
    if (ok) gekend++;
    var data = new FormData();
    data.append('gekend', ok ? '1' : '0');
    fetch('/leren/kaart/' + k.id + '/oefen', { method: 'POST', body: data, credentials: 'same-origin' }).catch(function () {});
    pos++;
    toon();
    window.scrollTo({ top: box.offsetTop - 80 });
  }
  function klaar() {
    ['flits', 'knoppen-voor', 'knoppen-achter', 'flits-link'].forEach(function (id) { $(id).hidden = true; });
    $('oefen-balk').style.width = '100%';
    $('oefen-teller').textContent = fmt(t.van, { i: kaarten.length, n: kaarten.length });
    $('oefen-uitslag').textContent = fmt(t.uitslag, { a: gekend, n: kaarten.length });
    $('oefen-klaar').hidden = false;
  }
  $('flits').addEventListener('click', function (e) { if (!e.target.closest('a')) draai(); });
  $('draai').addEventListener('click', draai);
  $('gekend').addEventListener('click', function () { antwoord(true); });
  $('nog').addEventListener('click', function () { antwoord(false); });
  document.addEventListener('keydown', function (e) {
    if (e.target.matches('input, textarea, select')) return;
    if (e.key === ' ' || e.key === 'Enter') { if (!omgedraaid) { e.preventDefault(); draai(); } }
    else if (e.key === '1') antwoord(false);
    else if (e.key === '2') antwoord(true);
  });
  toon();
})();
