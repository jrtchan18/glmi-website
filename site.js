// ===== EmailJS credentials (Request a Quote page) =====
// Fill these in from your EmailJS account (dashboard.emailjs.com):
// Public Key: Account -> General. Service ID: Email Services -> your
// connected Gmail. Template ID: Email Templates -> the template you make
// for this form. Until these are real values, the quote form shows a
// friendly "not set up yet" message instead of silently failing.
const QUOTE_EMAILJS_PUBLIC_KEY = 'dxT-e_jskt7ic6Qcd';
const QUOTE_EMAILJS_SERVICE_ID = 'service_3d2q6dy';
const QUOTE_EMAILJS_TEMPLATE_ID = 'template_e31ibb4';
const QUOTE_EMAIL_TO = 'jrtchan18@gmail.com';

// ===== Quote cart (localStorage) =====
// Shared across every page (product pages add to it, the nav badge reads
// it, request-quote.html renders and submits it). Item shape:
// { url: 'items/cotton-gloves.html', name: 'Cotton Gloves', qty: 2 }
//
// `url` is always stored site-root-relative ("items/x.html"), never relative
// to the page that did the adding — request-quote.html sits at the root and
// renders these straight into hrefs, so a "../"-prefixed value would break
// there. The add-to-quote buttons emit the root-relative form directly.
const QUOTE_CART_KEY = 'glmiQuoteCart';

// Product pages used to live at the repo root, so carts saved before that
// move hold bare filenames ("cotton-gloves.html") that now 404. Rewrite those
// on read. Safe to delete once no visitor could still be holding an old cart.
function normalizeCartUrl(url) {
  if (typeof url !== 'string' || url.includes('/')) return url;
  return 'items/' + url;
}

function getQuoteCart() {
  try {
    const raw = JSON.parse(localStorage.getItem(QUOTE_CART_KEY));
    if (!Array.isArray(raw)) return [];
    return raw.map((i) => ({ ...i, url: normalizeCartUrl(i.url) }));
  } catch (e) {
    return [];
  }
}

function saveQuoteCart(cart) {
  localStorage.setItem(QUOTE_CART_KEY, JSON.stringify(cart));
  updateQuoteBadge();
}

function addToQuoteCart(item) {
  const cart = getQuoteCart();
  const existing = cart.find((i) => i.url === item.url);
  if (existing) {
    existing.qty += item.qty;
  } else {
    cart.push(item);
  }
  saveQuoteCart(cart);
}

function removeFromQuoteCart(url) {
  saveQuoteCart(getQuoteCart().filter((i) => i.url !== url));
}

function updateQuoteBadge() {
  const badge = document.getElementById('quoteCount');
  if (!badge) return;
  const count = getQuoteCart().reduce((sum, i) => sum + i.qty, 0);
  badge.textContent = String(count);
  badge.hidden = count === 0;
}

document.addEventListener('DOMContentLoaded', () => {
  updateQuoteBadge();

  // "Add to Quote" buttons on product pages — reads the page's own
  // quantity stepper, adds/merges into the cart, gives brief visual
  // confirmation. Never navigates (type="button").
  document.querySelectorAll('.add-to-quote').forEach((btn) => {
    btn.addEventListener('click', () => {
      const qtyInput = btn.closest('.inquire-box')?.querySelector('.qty-stepper input');
      const qty = qtyInput ? Math.max(1, parseInt(qtyInput.value, 10) || 1) : 1;
      addToQuoteCart({ url: btn.dataset.url, name: btn.dataset.name, qty });
      const label = btn.querySelector('.btn-txt');
      const original = label ? label.textContent : btn.textContent;
      if (label) label.textContent = 'Added ✓'; else btn.textContent = 'Added ✓';
      btn.classList.add('added');
      setTimeout(() => {
        if (label) label.textContent = original; else btn.textContent = original;
        btn.classList.remove('added');
      }, 1600);
    });
  });

  // Request a Quote page — only runs where #quoteItems exists.
  const quoteItemsEl = document.getElementById('quoteItems');
  if (quoteItemsEl) {
    const emptyState = document.getElementById('quoteEmptyState');
    const successState = document.getElementById('quoteSuccessState');
    const formWrap = document.getElementById('quoteForm');
    const form = document.getElementById('quoteContactForm');
    const statusEl = document.getElementById('quoteStatus');
    const submitBtn = document.getElementById('quoteSubmitBtn');

    function showStatus(msg, isError) {
      statusEl.textContent = msg;
      statusEl.hidden = false;
      statusEl.classList.toggle('error', isError);
      statusEl.classList.toggle('success', !isError);
    }

    function renderQuoteItems() {
      const cart = getQuoteCart();
      if (!cart.length) {
        emptyState.hidden = false;
        formWrap.hidden = true;
        return;
      }
      emptyState.hidden = true;
      formWrap.hidden = false;
      quoteItemsEl.innerHTML = cart.map((item) => `
        <div class="quote-item" data-url="${item.url}">
          <a href="${item.url}" class="quote-item-name">${item.name}</a>
          <div class="qty-stepper">
            <button type="button" class="qty-minus" aria-label="Decrease quantity">&minus;</button>
            <input type="text" value="${item.qty}" inputmode="numeric" aria-label="Quantity">
            <button type="button" class="qty-plus" aria-label="Increase quantity">+</button>
          </div>
          <button type="button" class="quote-item-remove" aria-label="Remove ${item.name}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
          </button>
        </div>
      `).join('');

      quoteItemsEl.querySelectorAll('.quote-item').forEach((row) => {
        const url = row.dataset.url;
        row.querySelector('.qty-minus').addEventListener('click', () => {
          const cart2 = getQuoteCart();
          const item = cart2.find((i) => i.url === url);
          if (item) { item.qty = Math.max(1, item.qty - 1); saveQuoteCart(cart2); renderQuoteItems(); }
        });
        row.querySelector('.qty-plus').addEventListener('click', () => {
          const cart2 = getQuoteCart();
          const item = cart2.find((i) => i.url === url);
          if (item) { item.qty += 1; saveQuoteCart(cart2); renderQuoteItems(); }
        });
        row.querySelector('.quote-item-remove').addEventListener('click', () => {
          removeFromQuoteCart(url);
          renderQuoteItems();
        });
      });
    }
    renderQuoteItems();

    if (window.emailjs) {
      emailjs.init({ publicKey: QUOTE_EMAILJS_PUBLIC_KEY });
    }

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const name = document.getElementById('qfName').value.trim();
      const phone = document.getElementById('qfPhone').value.trim();
      const email = document.getElementById('qfEmail').value.trim();
      const cart = getQuoteCart();
      if (!name) { showStatus('Please enter your name.', true); return; }
      if (!phone && !email) { showStatus('Please provide a phone number or email so we can reach you.', true); return; }
      if (!cart.length) { showStatus('Your quote list is empty.', true); return; }
      if (!window.emailjs || QUOTE_EMAILJS_SERVICE_ID.startsWith('YOUR_')) {
        showStatus('The quote form isn’t fully set up yet — please call or email us directly for now.', true);
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending...';

      const itemsList = cart.map((i) => `- ${i.name} (x${i.qty})`).join('\n');
      const params = {
        to_email: QUOTE_EMAIL_TO,
        from_name: name,
        company: document.getElementById('qfCompany').value.trim(),
        phone: phone,
        reply_to: email,
        notes: document.getElementById('qfNotes').value.trim(),
        items_list: itemsList,
      };

      emailjs.send(QUOTE_EMAILJS_SERVICE_ID, QUOTE_EMAILJS_TEMPLATE_ID, params)
        .then(() => {
          saveQuoteCart([]);
          form.reset();
          // Show a dedicated thank-you state — NOT renderQuoteItems(), which
          // would just show the generic "cart is empty" message now that
          // the cart's been cleared and bury the confirmation.
          emptyState.hidden = true;
          formWrap.hidden = true;
          successState.hidden = false;
        })
        .catch(() => {
          showStatus('Something went wrong sending your request. Please call or email us directly.', true);
        })
        .finally(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Send Quote Request';
        });
    });
  }

  // Homepage scroll-reveal (anime.js) — elements marked [data-reveal] fade
  // + slide up as they enter the viewport. [data-reveal-delay] (ms) staggers
  // items within a grid (set per-element in generate.py). Not used on the
  // Products mega-menu or any other page — this only runs where anime.js is
  // actually loaded (homepage only, see ANIME_JS_TAG in generate.py) and
  // where reduced-motion isn't requested.
  const revealEls = document.querySelectorAll('[data-reveal]');
  if (revealEls.length) {
    if (window.anime && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      const revealed = new WeakSet();
      const reveal = (el) => {
        if (revealed.has(el)) return;
        revealed.add(el);
        anime({
          targets: el,
          opacity: [0, 1],
          translateY: [24, 0],
          duration: 550,
          easing: 'easeOutQuad',
          delay: Number(el.dataset.revealDelay || 0),
        });
      };
      anime.set(revealEls, { opacity: 0, translateY: 24 });
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          io.unobserve(entry.target);
          reveal(entry.target);
        });
      }, { threshold: 0.15, rootMargin: '0px 0px -60px 0px' });
      revealEls.forEach((el) => io.observe(el));
      // Safety net: IntersectionObserver should always fire for in-view
      // elements on page load, but if it doesn't (older browser, odd edge
      // case), don't leave content permanently invisible — force it in.
      setTimeout(() => {
        revealEls.forEach((el) => {
          if (!revealed.has(el)) { io.unobserve(el); reveal(el); }
        });
      }, 2500);
    } else {
      // anime.js failed to load (e.g. offline) or reduced-motion requested —
      // make sure content is just visible, not stuck hidden.
      revealEls.forEach((el) => { el.style.opacity = '1'; });
    }
  }

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
    const count = slides.length;

    // Optional seamless looping, opted into with
    // <div class="carousel" data-loop> — currently only the homepage hero.
    // Without it a carousel rewinds visibly from the last slide back to the
    // first; with it, stepping past either end keeps moving in the SAME
    // direction into a cloned copy of the opposite slide, then silently snaps
    // to the real one once the animation finishes. The clones are decorative
    // duplicates, so they're hidden from assistive tech.
    const loop = carousel.hasAttribute('data-loop') && count > 1;
    if (loop) {
      const head = slides[0].cloneNode(true);
      const tail = slides[count - 1].cloneNode(true);
      [head, tail].forEach(c => {
        c.setAttribute('aria-hidden', 'true');
        c.removeAttribute('id');
        c.querySelectorAll('[id]').forEach(n => n.removeAttribute('id'));
      });
      track.appendChild(head);
      track.insertBefore(tail, slides[0]);
    }

    let index = 0;              // real slide index — drives the dots
    let pos = loop ? 1 : 0;     // track offset, including the leading clone

    slides.forEach((_, i) => {
      const dot = document.createElement('button');
      dot.className = 'dot' + (i === 0 ? ' active' : '');
      dot.type = 'button';
      dot.setAttribute('aria-label', 'Go to slide ' + (i + 1));
      dot.addEventListener('click', () => goToManual(i));
      dotsWrap.appendChild(dot);
    });
    const dots = Array.from(dotsWrap.children);

    function render(animate) {
      track.style.transition = animate ? '' : 'none';
      track.style.transform = `translateX(-${pos * 100}%)`;
      if (!animate) {
        void track.offsetWidth;   // flush the jump before re-enabling easing
        track.style.transition = '';
      }
      dots.forEach((d, di) => d.classList.toggle('active', di === index));
    }

    // Once a wrap animation finishes we're parked on a clone; jump (without
    // animating) to the identical real slide so the next move continues
    // normally instead of rewinding across the whole track.
    let snapTimer = null;
    function snapIfOnClone() {
      if (!loop) return;
      if (pos === 0)              { pos = count; render(false); }   // leading clone  -> real last
      else if (pos === count + 1) { pos = 1;     render(false); }   // trailing clone -> real first
    }

    function goTo(i) {
      if (loop) {
        // i of -1 or count means "step past the edge" — land on a clone so the
        // motion continues in the same direction, then snap back.
        if (i < 0)           { index = count - 1; pos = 0; }
        else if (i >= count) { index = 0;         pos = count + 1; }
        else                 { index = i;         pos = i + 1; }
      } else {
        index = (i + count) % count;
        pos = index;
      }
      render(true);

      if (loop && (pos === 0 || pos === count + 1)) {
        clearTimeout(snapTimer);
        // transitionend below normally handles the snap. This timer is the
        // safety net for when it never fires — backgrounding a tab suspends
        // CSS transitions, and a missed event would strand the track on a
        // clone. Deliberate belt-and-braces; don't remove it.
        snapTimer = setTimeout(snapIfOnClone, 600);
      }
    }

    if (loop) {
      track.addEventListener('transitionend', e => {
        if (e.target !== track || e.propertyName !== 'transform') return;
        clearTimeout(snapTimer);
        snapIfOnClone();
      });
    }

    render(false);

    // Optional autoplay, opted into per-carousel with
    // <div class="carousel" data-autoplay="6000"> — currently only the
    // homepage hero. Carousels without the attribute behave exactly as before.
    const autoplayMs = parseInt(carousel.dataset.autoplay || '0', 10);
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let timer = null;

    function stopAuto() {
      if (timer) { clearInterval(timer); timer = null; }
    }
    function startAuto() {
      if (!autoplayMs || reduceMotion || count < 2) return;
      stopAuto();
      timer = setInterval(() => goTo(index + 1), autoplayMs);
    }
    // Manual navigation restarts the clock, so a slide the visitor just picked
    // doesn't get yanked away a fraction of a second later.
    function goToManual(i) { goTo(i); startAuto(); }

    // Pause while the visitor is reading (hover / keyboard focus) or when the
    // tab is in the background.
    carousel.addEventListener('mouseenter', stopAuto);
    carousel.addEventListener('mouseleave', startAuto);
    carousel.addEventListener('focusin', stopAuto);
    carousel.addEventListener('focusout', startAuto);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) stopAuto(); else startAuto();
    });

    if (prevBtn) prevBtn.addEventListener('click', () => goToManual(index - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goToManual(index + 1));

    let startX = 0;
    track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend', e => {
      const diff = e.changedTouches[0].clientX - startX;
      if (diff > 40) goToManual(index - 1);
      else if (diff < -40) goToManual(index + 1);
    }, { passive: true });

    startAuto();
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
