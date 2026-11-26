(() => {
  const head = document.querySelector('.head');
  const btn = document.getElementById('menuBtn'), nav = document.getElementById('mnav');
  let menuOpen = false;
  const sync = () => head && head.classList.toggle('scrolled', menuOpen || window.scrollY > 24);
  window.addEventListener('scroll', sync, { passive: true });
  sync();
  if (!btn || !nav) return;
  const set = open => {
    menuOpen = open;
    btn.setAttribute('aria-expanded', open);
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('open', open);
    sync();
  };
  btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => set(false)));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menuOpen) { set(false); btn.focus(); } });
})();
