// Zolang Claude bezig is (opzoeking, onderzoek): het blok elke paar seconden opnieuw ophalen en vervangen.
(function () {
  function volg(el) {
    var url = el.dataset.bezig;
    var pogingen = 0;
    function stap() {
      if (++pogingen > 120) return;
      fetch(url, { credentials: 'same-origin' }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      }).then(function (html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html.trim();
        var nieuw = tmp.firstElementChild;
        if (!nieuw) return;
        el.replaceWith(nieuw);
        el = nieuw;
        if (nieuw.dataset.bezig) setTimeout(stap, 2500);
      }).catch(function () { setTimeout(stap, 5000); });
    }
    setTimeout(stap, 2500);
  }
  document.querySelectorAll('[data-bezig]').forEach(volg);
})();
