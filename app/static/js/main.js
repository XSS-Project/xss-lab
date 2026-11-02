// Shared navigation only. Module-specific preview logic belongs to TV3.
(() => {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.nav-toggle');
  const navigation = document.querySelector('#main-navigation');
  if (!header || !toggle || !navigation) return;

  header.classList.add('js-nav');
  toggle.hidden = false;

  const closeMenu = () => {
    toggle.setAttribute('aria-expanded', 'false');
    navigation.dataset.open = 'false';
  };
  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(open));
    navigation.dataset.open = String(open);
  });
  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) closeMenu();
  });
  header.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      toggle.focus();
    }
  });
})();
