/* ============================================================
   NINA SECHKO x ROBINEAU - scroll-scrub product page
   ------------------------------------------------------------
   EVERYTHING YOU NEED TO EDIT IS IN NSX_CONFIG BELOW.
   All visible wording lives in the HTML, not in here.
   ============================================================ */
(function () {
  'use strict';

  var NSX_CONFIG = {

    /* Where the frames / video / stills live.
       Local preview: '.'   Tilda: the full https:// base of your asset host. */
    assetBase: '.',

    /* ---- the box-opening sequence ---- */
    frameCount: 123,
    framePrefix: '/frames/f_',
    frameExt: '.webp',

    /* ---- CHECKOUT --------------------------------------------------
       mode: 'link'  -> button is a plain link (Stripe Payment Link,
                        Tilda payment page, PayPal, anything).
       mode: 'tilda' -> button pushes the product into Tilda's own cart
                        (needs a Store block on the page - see README).
    ------------------------------------------------------------------ */
    checkout: {
      mode: 'link',
      url: 'https://buy.stripe.com/REPLACE_ME',        // <<REPLACE>>
      tilda: {
        id: 'nsx-memory-01',
        name: 'Nina Sechko - The Memory Game',          // <<REPLACE>>
        price: '4500',                                  // <<REPLACE>> minor units per Tilda setup
        img: '/media/still-backs.webp',
        options: []
      }
    }
  };

  /* ==========================================================
     Nothing below here normally needs editing.
     ========================================================== */

  var root = document.querySelector('.nsx');
  if (!root) return;

  var BASE = (NSX_CONFIG.assetBase || '.').replace(/\/$/, '');
  var TOTAL = NSX_CONFIG.frameCount;
  var FRAME_W = 756, FRAME_H = 1344;
  var FRAME_AR = FRAME_W / FRAME_H;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };

  function frameUrl(i) {
    /* the self-contained preview build inlines every frame as a data URI */
    if (window.NSX_FRAMES) return window.NSX_FRAMES[i - 1];
    var n = String(i);
    while (n.length < 3) n = '0' + n;
    return BASE + NSX_CONFIG.framePrefix + n + NSX_CONFIG.frameExt;
  }

  /* ---------------------------------------------------------
     Frame loading: two passes.
     Pass 1 loads every 6th frame so the sequence is scrubbable
     after ~500KB. Pass 2 fills in the gaps. The scrubber always
     draws the nearest frame it actually has.
     --------------------------------------------------------- */
  var imgs = new Array(TOTAL + 1);
  var loadedCount = 0;
  var meterFill = root.querySelector('.nsx__meterFill');

  function bumpMeter() {
    if (!meterFill) return;
    var pct = Math.round((loadedCount / TOTAL) * 100);
    meterFill.style.width = pct + '%';
    if (pct >= 100) meterFill.style.opacity = '0';
  }

  function loadFrame(i) {
    return new Promise(function (resolve) {
      if (imgs[i]) return resolve();
      var im = new Image();
      im.decoding = 'async';
      im.onload = function () {
        imgs[i] = im; loadedCount++; bumpMeter();
        /* a sharper frame for where we are standing just arrived - redraw */
        if (i === lastFrame) lastDrawn = -1;
        resolve();
      };
      im.onerror = function () { loadedCount++; bumpMeter(); resolve(); };
      im.src = frameUrl(i);
    });
  }

  function runQueue(list, concurrency) {
    var idx = 0;
    function worker() {
      if (idx >= list.length) return Promise.resolve();
      var i = list[idx++];
      return loadFrame(i).then(worker);
    }
    var pool = [];
    for (var k = 0; k < concurrency; k++) pool.push(worker());
    return Promise.all(pool);
  }

  var coarse = [], fine = [], i;
  for (i = 1; i <= TOTAL; i++) (((i - 1) % 6 === 0) ? coarse : fine).push(i);

  /* ---------------------------------------------------------
     Canvas scrubber
     --------------------------------------------------------- */
  var scrolly = root.querySelector('.nsx__scrolly');
  var stage = root.querySelector('.nsx__stage');
  var canvas = root.querySelector('.nsx__canvas');
  var hint = root.querySelector('.nsx__hint');
  var caps = [].slice.call(root.querySelectorAll('.nsx__cap'));
  var ctx = canvas ? canvas.getContext('2d', { alpha: false }) : null;

  /* lastFrame = what the scroll position wants.
     lastDrawn = what is actually on the canvas right now. */
  var cssW = 0, cssH = 0, dpr = 1, lastFrame = 1, lastDrawn = -1, running = false;

  function sizeCanvas() {
    if (!canvas) return false;
    var r = canvas.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    var d = Math.min(window.devicePixelRatio || 1, 2);
    if (r.width === cssW && r.height === cssH && d === dpr) return false;
    dpr = d; cssW = r.width; cssH = r.height;
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    lastDrawn = -1;
    return true;
  }

  function resize() {
    if (sizeCanvas()) paint(lastFrame);
  }

  function nearestLoaded(want) {
    if (imgs[want]) return imgs[want];
    for (var d = 1; d <= TOTAL; d++) {
      if (want - d >= 1 && imgs[want - d]) return imgs[want - d];
      if (want + d <= TOTAL && imgs[want + d]) return imgs[want + d];
    }
    return null;
  }

  function paint(idx) {
    if (!ctx) return;
    var img = nearestLoaded(idx);
    if (!img) return;
    if (canvas.width < 2 && !sizeCanvas()) return;
    var cw = canvas.width, ch = canvas.height;
    var ca = cw / ch, dw, dh;
    /* cover: fill the canvas box, crop the overflow */
    if (ca < FRAME_AR) { dh = ch; dw = ch * FRAME_AR; }
    else { dw = cw; dh = cw / FRAME_AR; }
    ctx.drawImage(img, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
  }

  function capStyle(p, from, to) {
    var IN = 0.055, OUT = 0.075;
    if (p <= from - IN || p >= to + OUT) return 0;
    if (p < from) return (p - (from - IN)) / IN;
    if (p > to) return 1 - (p - to) / OUT;
    return 1;
  }

  function tick() {
    if (!running) return;
    var r = scrolly.getBoundingClientRect();
    var runway = scrolly.offsetHeight - stage.offsetHeight;
    var p = runway > 0 ? clamp(-r.top / runway, 0, 1) : 0;

    var idx = Math.round(p * (TOTAL - 1)) + 1;
    lastFrame = idx;
    if (idx !== lastDrawn) { paint(idx); lastDrawn = idx; }

    for (var c = 0; c < caps.length; c++) {
      var el = caps[c];
      var o = capStyle(p, parseFloat(el.dataset.from), parseFloat(el.dataset.to));
      if (el._o !== o) {
        el.style.opacity = o;
        el.style.transform = reduced ? '' : 'translate3d(0,' + ((1 - o) * 14).toFixed(1) + 'px,0)';
        el._o = o;
      }
    }
    if (hint) hint.style.opacity = clamp(1 - p / 0.06, 0, 1);

    requestAnimationFrame(tick);
  }

  function start() { if (!running) { running = true; requestAnimationFrame(tick); } }
  function stop() { running = false; }

  if (canvas && ctx) {
    /* ResizeObserver catches the case where layout is not settled yet on
       first run (svh units, late fonts) as well as every later resize.
       On iOS this also covers the URL-bar show/hide reflow. */
    if ('ResizeObserver' in window) {
      new ResizeObserver(resize).observe(canvas);
    }
    resize();
    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt); rt = setTimeout(resize, 150);
    }, { passive: true });
    window.addEventListener('orientationchange', function () {
      setTimeout(resize, 260);
    });
    window.addEventListener('load', resize);

    /* only burn rAF while the hero is actually on screen */
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        es[0].isIntersecting ? start() : stop();
      }, { rootMargin: '10% 0px' }).observe(scrolly);
    } else { start(); }

    loadFrame(1).then(function () {
      paint(1);
      return runQueue(coarse, 6);
    }).then(function () {
      return runQueue(fine, 6);
    });
  }

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
      } else {
        console.warn('[nsx] Tilda cart not found. Add a Store block (ST100/T754) to this page.');
      }
      return;
    }
    /* mode: 'link' - let the anchor navigate normally */
    if (!cfg.url || /REPLACE_ME/.test(cfg.url)) {
      e.preventDefault();
      console.warn('[nsx] Set NSX_CONFIG.checkout.url before going live.');
    }
  }

  [].slice.call(root.querySelectorAll('[data-nsx-buy]')).forEach(function (b) {
    if (NSX_CONFIG.checkout.mode === 'link' && b.tagName === 'A') {
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
