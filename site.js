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
// { url: 'cotton-gloves.html', name: 'Cotton Gloves', qty: 2 }
const QUOTE_CART_KEY = 'glmiQuoteCart';

function getQuoteCart() {
  try {
    const raw = JSON.parse(localStorage.getItem(QUOTE_CART_KEY));
    return Array.isArray(raw) ? raw : [];
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
