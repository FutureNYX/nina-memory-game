#!/usr/bin/env python3
"""
Builds the drop-in Tilda blocks for the box-opening animation.

    python build_hero.py --base https://futurenyx.github.io/nina-memory-game

Four variants. They differ only in how much text they carry and how far the
picture blends into the page:

  hero-block-title.html           big title, SHORT fade  (17% / 6%)
  hero-block-title-longfade.html  big title, LONG fade   (39% / 15%)
  hero-block.html                 small captions only, short fade
  hero-block-plain.html           no text at all, short fade

Each is one self-contained paste into a single Tilda "T123 / HTML-код" block.
"""
import argparse
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

GOLOS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Golos+Text:wght@400;500;600&display=swap">'
)

# ---- caption sets -----------------------------------------------------

CAP_TITLE = """        <!-- Opening card. nsx__title is the big display line.
             It is a <p> rather than an <h1> on purpose: the cover block
             above already carries the page's H1, and two would compete in
             search results. The styling is identical either way. -->
        <div class="nsx__cap" data-from="0.00" data-to="0.16" style="opacity:1">
          <p class="nsx__eyebrow">ROBINEAU GALLERY</p>
          <p class="nsx__title">МЕМО</p>
          <p class="nsx__capText">Авторская игра в оформлении Нины Сечко.</p>
        </div>
"""

CAP_NOTITLE = """        <!-- opening line, no big display type -->
        <div class="nsx__cap" data-from="0.00" data-to="0.16" style="opacity:1">
          <p class="nsx__eyebrow">ROBINEAU GALLERY</p>
          <p class="nsx__capText">Авторская игра МЕМО в оформлении Нины Сечко.</p>
        </div>
"""

CAP_REST = """
        <!-- as the box splits open -->
        <div class="nsx__cap" data-from="0.28" data-to="0.44">
          <p class="nsx__eyebrow">Коробка</p>
          <p class="nsx__capText">Раскрывается сразу на четыре стороны.</p>
        </div>

        <!-- box lying open -->
        <div class="nsx__cap" data-from="0.56" data-to="0.72">
          <p class="nsx__eyebrow">Внутри</p>
          <p class="nsx__capText">50 парных карточек с картинами Нины Сечко.</p>
        </div>

        <!-- as the cards burst out -->
        <div class="nsx__cap" data-from="0.86" data-to="1.00">
          <p class="nsx__eyebrow">Игра</p>
          <p class="nsx__capText">Знакомые правила — и путешествие по миру художницы.</p>
        </div>"""

HINT = """      <div class="nsx__hint" aria-hidden="true">
        <span>Листайте</span>
        <span class="nsx__hintBar"></span>
      </div>"""

HEADER = """<!-- ===========================================================
     NINA SECHKO x ROBINEAU - the box-opening animation
     %(blurb)s

     PASTE ALL OF THIS INTO ONE TILDA BLOCK:
       Библиотека блоков -> Другое -> T123 "HTML-код"

     Move it anywhere on the page with the up/down arrows in the
     block's control panel. It works in any position.

     Two settings near the top of the CSS are worth knowing:
       --ground / --ground-rgb  background colour of this section
       --fade-y / --fade-x      how far the picture blends into it
                                (this build: %(fy)s and %(fx)s)

     Frames are served from:
       %(base)s
     Tilda cannot host them - that is Tilda's own rule, not a
     workaround. See HOW-TO-ADD-TO-TILDA.md.
     =========================================================== -->"""

# ---- variants ---------------------------------------------------------

VARIANTS = [
    dict(out='hero-block-title.html',
         blurb='big title + captions, SHORT fade - blend stops clear of the box',
         title=True, captions=True, hint=True, golos=True, fy='17%', fx='6%'),
    dict(out='hero-block-title-longfade.html',
         blurb='big title + captions, LONG fade - softer join, reaches into the box',
         title=True, captions=True, hint=True, golos=True, fy='39%', fx='15%'),
    dict(out='hero-block.html',
         blurb='small captions only, no big title, short fade',
         title=False, captions=True, hint=False, golos=False, fy='17%', fx='6%'),
    dict(out='hero-block-plain.html',
         blurb='no text at all - just the animation',
         title=False, captions=False, hint=False, golos=False, fy='17%', fx='6%'),
]

TILDA_SANS_BLOCK = (
    '  /* TildaSans is already loaded on any Tilda page, so the captions match\n'
    '     the rest of the site and cost no extra network request. */\n'
    '  --sans:"TildaSans","Golos Text",')

GOLOS_BLOCK = (
    '  /* Golos Text is a contemporary Russian family drawn Cyrillic-first, so\n'
    '     the type is not Latin metrics with Cyrillic bolted on. To use the\n'
    "     site's own TildaSans instead, swap the first two names round. */\n"
    '  --sans:"Golos Text","TildaSans",')


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def build_one(v, base):
    base = base.rstrip('/')

    if not v['captions']:
        caps = '        <!-- no captions in this version -->'
    else:
        caps = (CAP_TITLE if v['title'] else CAP_NOTITLE) + CAP_REST

    body = read('hero.html').replace('{{BASE}}', base)
    body = body.replace('{{CAPTIONS}}', caps)
    body = body.replace('{{HINT}}', HINT if v['hint'] else '')

    css = read('hero.css')
    css = css.replace('--fade-y:17%;', '--fade-y:%s;' % v['fy'])
    css = css.replace('--fade-x:6%;', '--fade-x:%s;' % v['fx'])
    if v['golos']:
        assert TILDA_SANS_BLOCK in css, 'font block not found in hero.css'
        css = css.replace(TILDA_SANS_BLOCK, GOLOS_BLOCK)

    js = read('hero.js').replace(
        "assetBase: 'https://futurenyx.github.io/nina-memory-game'",
        "assetBase: '%s'" % base)

    parts = [HEADER % {'blurb': v['blurb'], 'base': base,
                       'fy': v['fy'], 'fx': v['fx']}]
    if v['golos']:
        parts.append(GOLOS_LINK)
    parts.append('<style>\n'
                 "/* let the block escape Tilda's 960px container */\n"
                 '.t-rec .t123__wrapper,.t123 .t-container,.t123 .t-col'
                 '{max-width:100%!important;padding:0!important;margin:0!important}\n'
                 + css + '</style>')
    parts.append(body)
    parts.append('<script>\n' + js + '</script>')

    text = '\n\n'.join(parts) + '\n'
    path = os.path.join(HERE, 'tilda', v['out'])
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    n = len(text.encode('utf-8'))
    print('  %-32s %6d bytes (%2.0f%% of limit)  fade %s / %s'
          % (v['out'], n, n / 1000.0, v['fy'], v['fx']))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base',
                    default='https://futurenyx.github.io/nina-memory-game')
    a = ap.parse_args()
    print('Building hero blocks...')
    for v in VARIANTS:
        build_one(v, a.base)
    print('Done.')
