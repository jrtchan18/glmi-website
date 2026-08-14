document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav toggle
  const toggle = document.getElementById('navToggle');
  const nav = document.getElementById('mainNav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', isOpen);
    });
    nav.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Products mega-menu: hover-intent with a short close delay so a diagonal
  // mouse path from the trigger into the flyout (or from a category row into
  // its item sub-panel) doesn't slip through the gap and close the menu.
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.nav-item.has-mega').forEach(item => {
      let closeTimer;
      const open = () => { clearTimeout(closeTimer); item.classList.add('mega-open'); };
      const scheduleClose = () => { closeTimer = setTimeout(() => item.classList.remove('mega-open'), 250); };
      item.addEventListener('mouseenter', open);
      item.addEventListener('mouseleave', scheduleClose);

      item.querySelectorAll('.mega-cat').forEach(cat => {
        let subCloseTimer;
        const openSub = () => { clearTimeout(subCloseTimer); clearTimeout(closeTimer); cat.classList.add('mega-open'); };
        const scheduleCloseSub = () => { subCloseTimer = setTimeout(() => cat.classList.remove('mega-open'), 250); };
        cat.addEventListener('mouseenter', openSub);
        cat.addEventListener('mouseleave', scheduleCloseSub);
      });
    });
  }

  // Products mega-menu: tap-to-expand chevron buttons (mobile, and as a
  // click fallback everywhere). The chevron only expands/collapses the list
  // in place — it never navigates. The "Products"/category NAME link next
  // to it still navigates normally, since it's a plain <a href>.
  document.querySelectorAll('.mega-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.nav-item.has-mega');
      const isOpen = item.classList.toggle('mega-open');
      btn.setAttribute('aria-expanded', String(isOpen));
    });
  });
  document.querySelectorAll('.mega-cat-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const cat = btn.closest('.mega-cat');
      const isOpen = cat.classList.toggle('mega-open');
      btn.setAttribute('aria-expanded', String(isOpen));
    });
  });

  // Carousel galleries
  document.querySelectorAll('.carousel').forEach(carousel => {
    const track = carousel.querySelector('.carousel-track');
    const slides = Array.from(track.children);
    const prevBtn = carousel.querySelector('.carousel-btn.prev');
    const nextBtn = carousel.querySelector('.carousel-btn.next');
    const dotsWrap = carousel.querySelector('.carousel-dots');
    let index = 0;

    slides.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.className = 'dot' + (i === 0 ? ' active' : '');
      dot.type = 'button';
      dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      dot.addEventListener('click', () => goTo(i));
      dotsWrap.appendChild(dot);
    });
    const dots = Array.from(dotsWrap.children);

    function goTo(i) {
      index = (i + slides.length) % slides.length;
      track.style.transform = `translateX(-${index * 100}%)`;
      dots.forEach((d, di) => d.classList.toggle('active', di === index));
    }
    if (prevBtn) prevBtn.addEventListener('click', () => goTo(index - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goTo(index + 1));

    let startX = 0;
    track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend', e => {
      const diff = e.changedTouches[0].clientX - startX;
      if (diff > 40) goTo(index - 1);
      else if (diff < -40) goTo(index + 1);
    }, { passive: true });
  });

  // Product image gallery (main + thumbnail strip)
  document.querySelectorAll('.product-gallery').forEach(g => {
    const main = g.querySelector('.gallery-main');
    const thumbs = g.querySelectorAll('.gthumb');
    thumbs.forEach(t => {
      t.addEventListener('click', () => {
        const html = t.querySelector('.thumb-visual').innerHTML;
        main.querySelector('.thumb-visual').innerHTML = html;
        thumbs.forEach(x => x.classList.remove('active'));
        t.classList.add('active');
      });
    });
  });

  // Quantity steppers
  document.querySelectorAll('.qty-stepper').forEach(stepper => {
    const input = stepper.querySelector('input');
    stepper.querySelector('.qty-minus').addEventListener('click', () => {
      input.value = Math.max(1, parseInt(input.value || '1', 10) - 1);
    });
    stepper.querySelector('.qty-plus').addEventListener('click', () => {
      input.value = parseInt(input.value || '1', 10) + 1;
    });
  });
});
