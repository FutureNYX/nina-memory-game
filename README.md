# Nina Sechko × ROBINEAU — scroll-opening product page

A one-page product site whose hero is your box-opening film, scrubbed by the
scroll wheel / thumb rather than played.

---

## What's here

```
src/page.html        the markup — ALL the wording lives here
src/style.css        the design
src/app.js           the scrub engine + checkout wiring
build.py             assembles the two deliverables below
index.html           standalone page (local preview / GitHub Pages)
tilda/tilda-block.html   paste-into-Tilda version
frames/  123 webp    the box-opening sequence, 756×1344   (2.7 MB)
media/               play.mp4, poster, stills, OG image   (1.2 MB)
extract.py           rebuilds frames/ + media/ from the film
shots.py             screenshots the page at iPhone + desktop sizes
```

Rebuild after any edit to `src/`:

```bash
python build.py --base https://YOUR-ASSET-HOST
```

Preview locally:

```bash
python -m http.server 8765 --directory nina-cards
```

---

## How the scroll animation actually works

**It is not a video.** Scrubbing `video.currentTime` on iOS Safari stutters
badly — Safari only repaints on seek completion, so the box judders instead of
turning. Every site that does this properly (Apple's own product pages
included) uses an **image sequence drawn to a canvas**, and so does this.

- `nina-ad-6.mp4` 0.00 s → 8.53 s was sampled at 15 fps into 123 WebP frames (756×1344, 2.7 MB total).
- Six frames were dropped at the 3.7 s mark: CapCut had a white light-leak
  transition there, which flashed on slow scroll. The box keeps turning
  smoothly across the cut.
- The tail after 8.53 s was cut — the cards had already flown off frame and it
  ended on empty white.
- A tall spacer (`400svh`) holds a `position: sticky` stage. Scroll progress
  through the spacer maps 0 → 1 onto frames 1 → 123.

### The iPhone-specific bits

| Problem | What was done |
|---|---|
| URL bar collapsing resizes the viewport mid-scroll and the hero jumps | Sizes use `svh`, never `vh`/`dvh` — `svh` is the *smallest* viewport height and never changes |
| `overflow: hidden` on any ancestor silently kills `position: sticky` | The wrapper uses `overflow-x: clip`, which doesn't create a scroll container |
| 2.7 MB of frames is a slow first paint on cellular | Frames load in two passes — every 6th first (~440 KB, scrubbable almost immediately), then the gaps fill in. The scrubber always draws the nearest frame it actually has, so it degrades instead of stalling |
| Scroll handlers janking the main thread | Nothing runs on `scroll`. A `requestAnimationFrame` loop reads the position, and it only runs while the hero is on screen |
| Retina blowing up the canvas buffer | `devicePixelRatio` capped at 2 |
| Text over the card burst becomes unreadable | A light scrim sits under the captions on phones only; on desktop the captions move out of the frame into the left gutter |
| Fat-finger targets | Buy buttons are 56 px tall, plus a sticky "Add to bag" bar that appears after the hero and hides once the real buy block is on screen |

Reduced-motion, no-JS and no-`svh` fallbacks are all in place.

---

## What you need to replace

Everything below is placeholder. Search `src/page.html` for `REPLACE`.

| Where | Placeholder now |
|---|---|
| Product name (3 places: hero `<h1>`, buy block `<h2>`, `<title>` in build.py) | "The Memory Game" |
| Hero captions ×4 | generic lines about the box |
| "The edition" statement + body | drawn from Nina's bio on robineauart.com |
| "How it plays" copy | invented rules — **check these are actually right** |
| Triptych captions ×3 | generic |
| Specification table | every value is `000` / `00 × 00 mm` |
| Price (3 places: buy block, sticky bar, and Tilda config) | £45 |
| Shipping / returns line | invented |
| Checkout URL | `https://buy.stripe.com/REPLACE_ME` in `src/app.js` |

The ROBINEAU contact block and the `N  I  N  A      S  E  C  H  K  O` lockup
are correct as-is — the lockup uses literal spaces per house rule, so don't
"tidy" them into `letter-spacing`.

---

## Putting it on Tilda

1. Create a page. **Page Settings → uncheck the header/footer** if you want it
   truly full-bleed.
2. Add **one block: "T123 — HTML code"** (Other → HTML code). Nothing else.
3. Paste the entire contents of `tilda/tilda-block.html` into it.
4. Publish.

The block already contains a small CSS override that pushes it out of Tilda's
960 px container so the hero runs edge to edge.

**The assets can't live in Tilda.** 123 separate frame files is not something
Tilda's file manager handles well. Host `frames/` and `media/` somewhere with a
plain HTTPS URL — GitHub Pages is free and fine — then rebuild with
`--base https://that-host` so every path points at it.

### Payment

`src/app.js` → `NSX_CONFIG.checkout` has two modes.

**`mode: 'link'`** (default, simplest) — the button is just a link. Paste a
Stripe Payment Link, a PayPal button URL, anything. No Tilda store needed.

**`mode: 'tilda'`** — the button pushes the product into Tilda's own cart, so
you use whatever gateway is already connected to your Tilda account. This needs
a **Store block (ST100 / T754)** somewhere on the same page — it can be styled
invisible, it just has to exist for `tcart__addProduct` to be defined. Fill in
`checkout.tilda.{id, name, price}` to match your Tilda product.

---

## Regenerating the frames

`extract.py` rebuilds `frames/` and `media/` from the film, and documents
exactly which frames get dropped and why:

```bash
python extract.py "C:/Users/elija/AppData/Local/CapCut/Videos/nina-ad-6.mp4"
```

It prints the resulting frame count — put that in `NSX_CONFIG.frameCount` in
`src/app.js`, then re-run `build.py`.

If the film is re-cut, check for new flash transitions before trusting the
output. Brightness outliers give them away:

```bash
ffmpeg -v error -i nina-ad-6.mp4 -vf "fps=10,scale=64:-1,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-" -f null -
```

A single frame ~40 points brighter than its neighbours is a light leak, not
content. Add its index to `DROP` in `extract.py`.
