(() => {
  const header = document.getElementById('siteHeader');
  const toggle = document.getElementById('menuToggle');
  const menu = document.getElementById('mobileMenu');
  if (!header || !toggle || !menu) return;
  let lastScrollY = window.scrollY;
  const setOpen = open => {
    header.classList.toggle('mobile-menu-open',open);
    menu.classList.toggle('open',open);
    toggle.setAttribute('aria-expanded',String(open));
    toggle.setAttribute('aria-label',open?'Close menu':'Open menu');
    header.classList.remove('header-hidden');
  };
  function updateHeader() {
    const y = window.scrollY;
    header.classList.toggle('scrolled',y > 20);
    if (!header.classList.contains('mobile-menu-open')) header.classList.toggle('header-hidden',y > lastScrollY && y > 120);
    lastScrollY = y;
  }
  window.addEventListener('scroll',updateHeader,{passive:true});
  toggle.addEventListener('click',() => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click',() => setOpen(false)));
  document.addEventListener('keydown',event => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {setOpen(false);toggle.focus();}
  });
  window.addEventListener('resize',() => {if (window.innerWidth > 820 && toggle.getAttribute('aria-expanded') === 'true') setOpen(false);});
  updateHeader();
})();
