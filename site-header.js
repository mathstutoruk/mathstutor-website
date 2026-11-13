(() => {
  const header = document.getElementById('siteHeader');
  const toggle = document.getElementById('menuToggle');
  const menu = document.getElementById('mobileMenu');
  if (!header || !toggle || !menu) return;

  const mobile = window.matchMedia('(width < 851px)');
  let lastScrollY = window.scrollY;
  const isOpen = () => toggle.getAttribute('aria-expanded') === 'true';

  const setOpen = open => {
    header.classList.toggle('mobile-menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };

  function updateHeader() {
    const y = window.scrollY;
    header.classList.toggle('scrolled', y > 20);
    header.classList.toggle('header-hidden', !mobile.matches && y > lastScrollY && y > 120);
    lastScrollY = y;
  }

  window.addEventListener('scroll', updateHeader, {passive:true});
  toggle.addEventListener('click', () => setOpen(!isOpen()));

  document.addEventListener('click', event => {
    if (!isOpen() || toggle.contains(event.target)) return;
    if (!menu.contains(event.target) || event.target.closest('a')) setOpen(false);
  });

  document.addEventListener('focusin', event => {
    if (isOpen() && !header.contains(event.target)) setOpen(false);
  });

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !isOpen()) return;
    event.preventDefault();
    setOpen(false);
    toggle.focus();
  });

  mobile.addEventListener('change', () => {
    setOpen(false);
    updateHeader();
  });
  updateHeader();
})();
