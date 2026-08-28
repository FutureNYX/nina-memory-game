/* ============================================================
   NINA SECHKO x ROBINEAU - scroll-opening hero

   Scrubs a 123-frame image sequence with the scroll position.
   It is NOT a video: scrubbing video.currentTime on iOS Safari
   judders, because Safari only repaints when a seek completes.

   The only thing you normally need to touch is NSX_HERO.assetBase.
   ============================================================ */
(function () {
  'use strict';

  var NSX_HERO = {
    /* Where the frames live. Must be an https:// base with the frame
       folders under it. Tilda cannot host these - see the README. */
    assetBase: 'https://futurenyx.github.io/nina-memory-game',
    frameCount: 123,
    frameExt: '.webp',

    /* Two frame sets at different resolutions. The page picks one at load
       from screen width x pixel density, so a 3x phone gets the sharp set
       and an older 2x phone is not made to download it.
       To force one, set the other to null. */
    std: { dir: '/frames/f_',    width: 756  },   /* ~5.4 MB */
    hi:  { dir: '/frames-hi/f_', width: 1080 }    /* ~15 MB, source resolution at WebP q95 */
  };

  /* ---------------------------------------------------------- */

  var root = document.querySelector('.nsx');
  if (!root) return;

  var BASE = (NSX_HERO.assetBase || '.').replace(/\/$/, '');
  var TOTAL = NSX_HERO.frameCount;
  var FRAME_AR = 9 / 16;
  var MAX_DPR = 3;

  /* ---------------------------------------------------------
     Which frame set to download.

     The canvas is the largest 9:16 box that fits the screen, so the pixels
     actually needed are (that box's CSS width) x (pixel density). If the
     small set would have to be stretched more than ~15% we fetch the big
     one; otherwise the small one is already sharp and 1.8 MB lighter.

     Overridden down to the small set when the device reports little memory
     or the user has asked for reduced data, because holding 123 decoded
     1080x1920 frames is not free.
     --------------------------------------------------------- */
  function pickSet() {
    var std = NSX_HERO.std, hi = NSX_HERO.hi;
    if (!hi) return std;
    if (!std) return hi;

    var conn = navigator.connection || {};
    if (conn.saveData) return std;
    if (navigator.deviceMemory && navigator.deviceMemory < 4) return std;

    var d = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    var vw = document.documentElement.clientWidth || window.innerWidth;
    var vh = window.innerHeight;
    var cssW = Math.min(vw, vh * FRAME_AR);
    return (cssW * d) > std.width * 1.15 ? hi : std;
  }

  var SET = pickSet();

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }

  function frameUrl(i) {
    /* the self-contained preview build inlines every frame as a data URI */
    if (window.NSX_FRAMES) return window.NSX_FRAMES[i - 1];
    var n = String(i);
    while (n.length < 3) n = '0' + n;
    return BASE + SET.dir + n + NSX_HERO.frameExt;
  }

  /* ---------------------------------------------------------
     Frame loading, in two passes.
     Pass 1 grabs every 6th frame, so the sequence is scrubbable
     after ~440 KB instead of the full 2.7 MB. Pass 2 fills the
     gaps in. The scrubber always draws the nearest frame it
     actually has, so it degrades rather than stalling.
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

  function loadFrame(i, attempt) {
    return new Promise(function (resolve) {
      if (imgs[i]) return resolve();
      var im = new Image();
      im.decoding = 'async';
      im.onload = function () {
        imgs[i] = im; loadedCount++; bumpMeter();
        if (i === lastFrame) lastDrawn = -1;   /* sharper frame arrived */
        resolve();
      };
      im.onerror = function () {
        /* CDNs throttle a burst of 123 requests and phones drop off
           mid-scroll. Retry twice before giving up. */
        var n = attempt || 0;
        if (n < 2) {
          setTimeout(function () { resolve(loadFrame(i, n + 1)); }, 400 * (n + 1));
          return;
        }
        loadedCount++; bumpMeter(); resolve();
      };
      im.src = frameUrl(i) + (attempt && !window.NSX_FRAMES ? '?r=' + attempt : '');
    });
  }

  function runQueue(list, concurrency) {
    var idx = 0;
    function worker() {
      if (idx >= list.length) return Promise.resolve();
      return loadFrame(list[idx++]).then(worker);
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
  if (!scrolly || !stage || !ctx) return;

  var cssW = 0, cssH = 0, dpr = 1, lastFrame = 1, lastDrawn = -1, running = false;
  var cropTop = 0;

  /* How much of the top of the frame to cut, read from the --crop-top CSS
     custom property so it lives next to the other visual settings. */
  function readCrop() {
    var v = parseFloat(getComputedStyle(root).getPropertyValue('--crop-top'));
    var n = isNaN(v) ? 0 : v / 100;
    return n < 0 ? 0 : n > 0.4 ? 0.4 : n;
  }

  function sizeCanvas() {
    var r = canvas.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return false;
    var d = Math.min(window.devicePixelRatio || 1, MAX_DPR);
    if (r.width === cssW && r.height === cssH && d === dpr
        && cropTop === readCrop()) return false;
    dpr = d; cssW = r.width; cssH = r.height; cropTop = readCrop();
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssH * dpr);
    lastDrawn = -1;
    return true;
  }

  function resize() { if (sizeCanvas()) paint(lastFrame); }

  function nearestLoaded(want) {
    if (imgs[want]) return imgs[want];
    for (var d = 1; d <= TOTAL; d++) {
      if (want - d >= 1 && imgs[want - d]) return imgs[want - d];
      if (want + d <= TOTAL && imgs[want + d]) return imgs[want + d];
    }
    return null;
  }

  function paint(idx) {
    var img = nearestLoaded(idx);
    if (!img) return;
    if (canvas.width < 2 && !sizeCanvas()) return;

    /* take a slice off the top of the source, then fill the canvas with
       what is left - so the dead space above the box goes and the box
       ends up larger, rather than the picture simply sliding upwards. */
    var sw = img.naturalWidth || 756;
    var sy = Math.round((img.naturalHeight || 1344) * cropTop);
    var sh = (img.naturalHeight || 1344) - sy;
    var ar = sw / sh;

    var cw = canvas.width, ch = canvas.height;
    var dw, dh;
    if (cw / ch < ar) { dh = ch; dw = ch * ar; }
    else { dw = cw; dh = cw / ar; }
    ctx.drawImage(img, 0, sy, sw, sh, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
  }

  function capOpacity(p, from, to) {
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
      var o = capOpacity(p, parseFloat(el.getAttribute('data-from')),
                            parseFloat(el.getAttribute('data-to')));
      if (el._o !== o) {
        el.style.opacity = o;
        el.style.transform = reduced ? '' : 'translate3d(0,' + ((1 - o) * 14).toFixed(1) + 'px,0)';
        el._o = o;
      }
    }
    if (hint) hint.style.opacity = clamp(1 - p / 0.06, 0, 1);

    requestAnimationFrame(tick);
  }

  /* ResizeObserver catches layout not being settled on first run (svh
     units, late fonts) as well as every later resize. On iOS it also
     covers the URL-bar show/hide reflow. */
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(canvas);
  resize();

  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt); rt = setTimeout(resize, 150);
  }, { passive: true });
  window.addEventListener('orientationchange', function () { setTimeout(resize, 260); });
  window.addEventListener('load', resize);

  /* only burn rAF while the hero is actually on screen */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      running = es[0].isIntersecting;
      if (running) requestAnimationFrame(tick);
    }, { rootMargin: '10% 0px' }).observe(scrolly);
  } else {
    running = true; requestAnimationFrame(tick);
  }

  loadFrame(1)
    .then(function () { paint(1); return runQueue(coarse, 6); })
    .then(function () { return runQueue(fine, 6); });

  /* handy when checking which set a real device chose */
  window.NSX_HERO_SET = SET;
})();
