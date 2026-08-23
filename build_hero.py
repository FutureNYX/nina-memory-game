#!/usr/bin/env python3
"""
Builds the drop-in Tilda blocks for the box-opening animation.

    python build_hero.py --base https://futurenyx.github.io/nina-memory-game

Produces:
  tilda/hero-block.html         animation + the four timed captions
  tilda/hero-block-plain.html   animation only, no text at all

Each is one self-contained paste into a single Tilda "T123 / HTML-код" block.
"""
import argparse
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

FONT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=Golos+Text:wght@400;500;600&display=swap">'
)

CAPTIONS = """        <!-- caption 1 - while the box is still closed.
             Deliberately NOT an <h1>: the page already has one in the
             cover block above, and two would confuse search engines. -->
        <div class="nsx__cap" data-from="0.00" data-to="0.16" style="opacity:1">
          <p class="nsx__eyebrow">ROBINEAU GALLERY</p>
          <p class="nsx__capText">Авторская игра МЕМО в оформлении Нины Сечко.</p>
        </div>

        <!-- caption 2 - as the box splits open -->
        <div class="nsx__cap" data-from="0.28" data-to="0.44">
          <p class="nsx__eyebrow">Коробка</p>
          <p class="nsx__capText">Раскрывается сразу на четыре стороны.</p>
        </div>

        <!-- caption 3 - box lying open -->
        <div class="nsx__cap" data-from="0.56" data-to="0.72">
          <p class="nsx__eyebrow">Внутри</p>
          <p class="nsx__capText">50 парных карточек с картинами Нины Сечко.</p>
        </div>

        <!-- caption 4 - as the cards burst out -->
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
     %s

     PASTE ALL OF THIS INTO ONE TILDA BLOCK:
       Библиотека блоков -> Другое -> T123 "HTML-код"

     Move it anywhere on the page with the up/down arrows in the
     block's control panel. It works in any position.

     Background of this section is set by --ground near the top of
     the CSS below. #ECEDF1 is sampled from the film's own backdrop;
     #FFFFFF or #F2F2F2 also work if you want it to match a
     neighbouring block exactly.

     Frames are served from:
       %s
     Tilda cannot host them - that is Tilda's own rule, not a
     workaround. See the README.
     =========================================================== -->"""


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def build_one(out_name, blurb, base, with_text):
    body = read('hero.html').replace('{{BASE}}', base.rstrip('/'))
    body = body.replace('{{CAPTIONS}}', CAPTIONS if with_text else
                        '        <!-- no captions in this version -->')
    # her cover block already shows a scroll chevron, so the hint is off
    body = body.replace('{{HINT}}', '')

    css = read('hero.css')
    js = read('hero.js').replace(
        "assetBase: 'https://futurenyx.github.io/nina-memory-game'",
        "assetBase: '%s'" % base.rstrip('/'))

    parts = [HEADER % (blurb, base.rstrip('/'))]
    parts.append('<style>\n'
                 '/* let the block escape Tilda\'s 960px container */\n'
                 '.t-rec .t123__wrapper,.t123 .t-container,.t123 .t-col'
                 '{max-width:100%!important;padding:0!important;margin:0!important}\n'
                 + css + '</style>')
    parts.append(body)
    parts.append('<script>\n' + js + '</script>')

    text = '\n\n'.join(parts) + '\n'
    path = os.path.join(HERE, 'tilda', out_name)
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    n = len(text.encode('utf-8'))
    print('  %-30s %6d bytes  (%.0f%% of Tilda\'s 100000 limit)'
          % (out_name, n, n / 1000.0))
    return n


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='https://futurenyx.github.io/nina-memory-game')
    a = ap.parse_args()
    print('Building hero blocks...')
    build_one('hero-block.html', 'version WITH four short captions that fade in and out',
              a.base, True)
    build_one('hero-block-plain.html', 'version with NO text - animation only',
              a.base, False)
    print('Done.')
