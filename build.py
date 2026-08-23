#!/usr/bin/env python3
"""
Assembles the two deliverables from src/.

  index.html              -> standalone page (local preview + GitHub Pages)
  tilda/tilda-block.html  -> paste this into a Tilda T123 "HTML code" block

Usage:
  python build.py                       # assets served relative (local preview)
  python build.py --base https://user.github.io/repo
"""
import argparse
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    print('  %-34s %6.1f KB' % (os.path.relpath(path, HERE), len(text.encode('utf-8')) / 1024.0))


FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" '
    'href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500'
    '&family=Golos+Text:wght@400;500;600&display=swap">'
)


def build(base_standalone, base_tilda):
    page = read('page.html')
    # hero.css / hero.js are the single source of truth for the animation;
    # style.css and app.js only add the sections below it.
    css = read('hero.css') + '\n' + read('style.css')
    js = read('hero.js') + '\n' + read('app.js')

    # ---------- standalone index.html ----------
    body = page.replace('{{BASE}}', base_standalone)
    js_std = js.replace("assetBase: '.'", "assetBase: '%s'" % base_standalone)
    og = base_tilda.rstrip('/') + '/media/og.jpg'

    html = u"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Мемори — Нина Сечко × ROBINEAU</title>
<meta name="description" content="Коллекционное издание: живопись, в которую играют. Нина Сечко, издано ROBINEAU.">
<meta name="theme-color" content="#ECEDF1">
<meta property="og:type" content="product">
<meta property="og:title" content="Мемори — Нина Сечко × ROBINEAU">
<meta property="og:description" content="Коллекционное издание: живопись, в которую играют.">
<meta property="og:image" content="%(og)s">
<meta name="twitter:card" content="summary_large_image">
%(font)s
<style>
html,body{margin:0;padding:0;background:#ECEDF1}
%(css)s
</style>
</head>
<body>
%(body)s
<script>
%(js)s
</script>
</body>
</html>
""" % {'og': og, 'font': FONT_LINK, 'css': css, 'body': body, 'js': js_std}

    write(os.path.join(HERE, 'index.html'), html)

    # ---------- tilda block ----------
    body_t = page.replace('{{BASE}}', base_tilda.rstrip('/'))
    js_t = js.replace("assetBase: '.'", "assetBase: '%s'" % base_tilda.rstrip('/'))

    tilda = u"""<!-- ===========================================================
     PASTE THIS WHOLE THING INTO ONE TILDA "T123 / HTML code" BLOCK.
     Asset host: %(base)s
     Rebuild with:  python build.py --base <url>
     =========================================================== -->
%(font)s
<style>
/* let the block run edge to edge inside Tilda's container */
.t-rec .t123__wrapper,.t123 .t-container,.t123 .t-col{max-width:100%%!important;padding:0!important;margin:0!important}
.t-body{background:#ECEDF1}
%(css)s
</style>

%(body)s

<script>
%(js)s
</script>
""" % {'base': base_tilda, 'font': FONT_LINK, 'css': css, 'body': body_t, 'js': js_t}

    write(os.path.join(HERE, 'tilda', 'tilda-block.html'), tilda)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='https://REPLACE-WITH-YOUR-ASSET-HOST',
                    help='https base where /frames and /media are hosted')
    a = ap.parse_args()
    print('Building...')
    build('.', a.base)
    print('Done.')
