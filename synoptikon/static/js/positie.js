// Scrollpositie behouden als een formulier of herladen de pagina opnieuw laadt.
// Vóór het versturen bewaren we de stand van het venster en van elk gescrold vak (bv. de
// synopse-kolommen); na het laden zetten we die terug, alleen op dezelfde pagina en kort
// daarna. Dat wint ook van een #anker in de redirect: je blijft waar je was.
// Het verstuurde formulier is het anker: komt er iets boven bij of gaat er iets weg, dan blijft
// het formulier op zijn plek. Uitzetten per formulier: data-scroll="boven".
(function () {
  var SLEUTEL = 'synoptikon:positie', MAX_LEEFTIJD = 120000;

  function selector(el) {
    var delen = [];
    while (el && el.nodeType === 1 && el.tagName !== 'BODY' && el.tagName !== 'HTML') {
      if (el.id) { delen.unshift('#' + CSS.escape(el.id)); return delen.join(' > '); }
      var i = 1;
      for (var s = el.previousElementSibling; s; s = s.previousElementSibling) if (s.tagName === el.tagName) i++;
      delen.unshift(el.tagName.toLowerCase() + ':nth-of-type(' + i + ')');
      el = el.parentElement;
    }
    delen.unshift('body');
    return delen.join(' > ');
  }

  function sleutelVan(form) {
    var delen = [form.getAttribute('action') || ''];
    form.querySelectorAll('input[type=hidden]').forEach(function (i) { if (i.name) delen.push(i.name + '=' + i.value); });
    return delen.join('&');
  }

  function vindForm(anker) {
    var zelfde = Array.prototype.filter.call(document.forms, function (f) { return sleutelVan(f) === anker[2]; });
    if (zelfde.length === 1) return zelfde[0];
    var el = document.querySelector(anker[0]);
    return el && el.tagName === 'FORM' ? el : null;
  }

  function scrollbaar(el) {
    return el.scrollHeight > el.clientHeight && /auto|scroll/.test(getComputedStyle(el).overflowY);
  }

  function bewaar(form) {
    if (form && form.dataset && form.dataset.scroll === 'boven') return;
    var panelen = [];
    document.querySelectorAll('body *').forEach(function (el) {
      if (el.scrollTop || el.scrollLeft) panelen.push([selector(el), el.scrollTop, el.scrollLeft]);
    });
    var stand = { pad: location.pathname, tijd: Date.now(), x: window.scrollX, y: window.scrollY, panelen: panelen };
    if (form) stand.anker = [selector(form), form.getBoundingClientRect().top, sleutelVan(form)];
    try { sessionStorage.setItem(SLEUTEL, JSON.stringify(stand)); } catch (e) {}
  }

  function zet(stand) {
    window.scrollTo(stand.x, stand.y);
    stand.panelen.forEach(function (p) {
      var el = document.querySelector(p[0]);
      if (el) { el.scrollTop = p[1]; el.scrollLeft = p[2]; }
    });
    var form = stand.anker && vindForm(stand.anker);
    if (!form) return;
    var verschil = form.getBoundingClientRect().top - stand.anker[1];
    if (Math.abs(verschil) < 1) return;
    var doos = form.parentElement;
    while (doos && doos !== document.body && !scrollbaar(doos)) doos = doos.parentElement;
    if (doos && doos !== document.body) doos.scrollTop += verschil; else window.scrollBy(0, verschil);
  }

  function herstel() {
    var stand = null;
    try { stand = JSON.parse(sessionStorage.getItem(SLEUTEL)); sessionStorage.removeItem(SLEUTEL); } catch (e) {}
    var leeftijd = stand ? Date.now() - stand.tijd : -1;
    if (!stand || stand.pad !== location.pathname || leeftijd < 0 || leeftijd >= MAX_LEEFTIJD) return;
    zet(stand);
    // Nog eens als lettertypen en beelden er zijn, tenzij je intussen zelf scrolde.
    var zelf = false;
    ['wheel', 'touchstart', 'keydown', 'mousedown'].forEach(function (t) {
      window.addEventListener(t, function () { zelf = true; }, { once: true, passive: true });
    });
    function nogEens() { if (!zelf) zet(stand); }
    if (document.readyState === 'complete') requestAnimationFrame(nogEens);
    else window.addEventListener('load', function () { requestAnimationFrame(nogEens); }, { once: true });
  }

  // Op window, dus na de bevestigingsvraag in app.js (die op document luistert).
  window.addEventListener('submit', function (e) {
    var f = e.target;
    if (e.defaultPrevented || (f.target && f.target !== '_self')) return;
    bewaar(f);
  });
  window.bewaarPositie = bewaar;  // voor form.submit() en location.reload(), die geen submit geven
  herstel();
})();
