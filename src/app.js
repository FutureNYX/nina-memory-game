/* ============================================================
   NINA SECHKO x ROBINEAU - page sections BELOW the animation
   ------------------------------------------------------------
   The animation itself lives in hero.js, which is loaded first.
   This file only adds the reveals, the looping film and checkout
   for the full reference page. The Tilda hero block does not
   include any of it.
   ============================================================ */
(function () {
  'use strict';

  var root = document.querySelector('.nsx');
  if (!root) return;

  var scrolly = root.querySelector('.nsx__scrolly');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var NSX_CONFIG = {
    /* asset host, used for the cart thumbnail */
    assetBase: 'https://futurenyx.github.io/nina-memory-game',

    /* ---- CHECKOUT --------------------------------------------------
       NOT WIRED YET. Needs to accept Russian cards, so nothing was
       guessed at here. Stripe is not an option - it does not process
       Russian-issued cards.

       mode: 'tilda' (default) -> pushes the product into Tilda's own cart,
                        so it settles through whichever gateway is connected
                        to the Tilda account: YooKassa, T-Bank, Robokassa,
                        CloudPayments, Sberbank or Alfa-Bank - all of which
                        take Mir and Russian-issued cards, and the first
                        three also do SBP. Requires an ST100 Store block on
                        the page (it can be hidden) so that the cart JS is
                        defined. Fill in the three tilda.* fields below.
       mode: 'link'  -> button becomes a plain link to any checkout URL.
    ------------------------------------------------------------------ */
    checkout: {
      mode: 'tilda',
      url: '',                    // only used by mode 'link'; a fallback here
                                  // is also used if the Tilda cart is missing
      tilda: {
        id: 'nsx-memori-01',
        name: 'Нина Сечко — Мемори',                     // <<REPLACE>>
        price: '4500',                                   // <<REPLACE>> per your Tilda product
        img: '/media/still-backs.webp',
        options: []
      }
    }
  };

  var BASE = NSX_CONFIG.assetBase.replace(/\/$/, '');

  /* ---------------------------------------------------------
     Reveals
     --------------------------------------------------------- */
  var rises = [].slice.call(root.querySelectorAll('.nsx__rise'));
  if ('IntersectionObserver' in window && !reduced) {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); ro.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    rises.forEach(function (el, n) {
      el.style.transitionDelay = (n % 3) * 90 + 'ms';
      ro.observe(el);
    });
  } else {
    rises.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------------------------------------------------------
     Looping film: only play while visible (saves battery, and
     iOS will not autoplay off-screen video reliably anyway)
     --------------------------------------------------------- */
  var vid = root.querySelector('.nsx__playFrame video');
  if (vid && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { var q = vid.play(); if (q && q.catch) q.catch(function () {}); }
        else { vid.pause(); }
      });
    }, { threshold: 0.25 }).observe(vid);
  }

  /* ---------------------------------------------------------
     Checkout
     --------------------------------------------------------- */
  function goCheckout(e) {
    var cfg = NSX_CONFIG.checkout;
    if (cfg.mode === 'tilda') {
      e.preventDefault();
      if (typeof window.tcart__addProduct === 'function') {
        var t = cfg.tilda;
        window.tcart__addProduct({
          id: t.id, name: t.name, price: t.price, quantity: 1,
          img: /^https?:/.test(t.img) ? t.img : BASE + t.img,
          url: window.location.href, options: t.options || []
        });
        if (typeof window.tcart__openCart === 'function') window.tcart__openCart();
      } else if (cfg.url) {
        window.location.href = cfg.url;        // fall back rather than dead-end
      } else {
        console.warn('[nsx] Tilda cart not on this page. Add an ST100 Store block, '
                   + 'or set NSX_CONFIG.checkout.url as a fallback.');
      }
      return;
    }
    /* mode: 'link' - let the anchor navigate normally */
    if (!cfg.url || cfg.url === '#') {
      e.preventDefault();
      console.warn('[nsx] No checkout URL set yet - see NSX_CONFIG.checkout.');
    }
  }

  [].slice.call(root.querySelectorAll('[data-nsx-buy]')).forEach(function (b) {
    if (NSX_CONFIG.checkout.mode === 'link' && b.tagName === 'A' && NSX_CONFIG.checkout.url) {
      b.setAttribute('href', NSX_CONFIG.checkout.url);
    }
    b.addEventListener('click', goCheckout);
  });

  /* ---------------------------------------------------------
     Sticky mobile buy dock: appears after the hero, hides once
     the real buy block is on screen.
     --------------------------------------------------------- */
  var dock = root.querySelector('.nsx__dock');
  var buySection = root.querySelector('#nsx-buy');
  if (dock && buySection && 'IntersectionObserver' in window) {
    var pastHero = false, atBuy = false;
    var sync = function () { dock.classList.toggle('is-on', pastHero && !atBuy); };
    new IntersectionObserver(function (es) {
      pastHero = !es[0].isIntersecting; sync();
    }, { rootMargin: '0px' }).observe(scrolly);
    new IntersectionObserver(function (es) {
      atBuy = es[0].isIntersecting; sync();
    }, { threshold: 0.15 }).observe(buySection);
  }

  /* expose for quick console tweaking */
  window.NSX_CONFIG = NSX_CONFIG;
})();
