#!/usr/bin/env python3
"""
Builds tilda/play-block.html - the "Как играть" section as one paste into a
Tilda T123 "HTML-код" block.

    python build_play.py --base https://futurenyx.github.io/nina-memory-game
"""
import argparse
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

JS = """(function () {
  'use strict';
  var v = document.querySelector('.nsxp__film video');
  if (!v) return;
  /* Play only while on screen. Saves battery, and iOS will not reliably
     autoplay an off-screen video anyway. */
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { var q = v.play(); if (q && q.catch) q.catch(function () {}); }
        else { v.pause(); }
      });
    }, { threshold: 0.25 }).observe(v);
  } else {
    var q = v.play(); if (q && q.catch) q.catch(function () {});
  }
})();"""

HEADER = """<!-- ===========================================================
     NINA SECHKO x ROBINEAU - "Как играть" section

     PASTE ALL OF THIS INTO ONE TILDA BLOCK:
       Библиотека блоков -> Другое -> T123 "HTML-код"

     Worth knowing, near the top of the CSS:
       --ground      background colour of this section
       --film-max-h  how large the film is allowed to get (78svh)

     The film is served from:
       %s
     =========================================================== -->"""


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def build(base):
    base = base.rstrip('/')
    body = read('play.html').replace('{{BASE}}', base)
    css = read('play.css')

    parts = [
        HEADER % base,
        '<style>\n'
        "/* let the block escape Tilda's 960px container */\n"
        '.t-rec .t123__wrapper,.t123 .t-container,.t123 .t-col'
        '{max-width:100%!important;padding:0!important;margin:0!important}\n'
        + css + '</style>',
        body,
        '<script>\n' + JS + '\n</script>',
    ]
    text = '\n\n'.join(parts) + '\n'

    path = os.path.join(HERE, 'tilda', 'play-block.html')
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    n = len(text.encode('utf-8'))
    print('  play-block.html  %d bytes (%.0f%% of Tilda limit)' % (n, n / 1000.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base',
                    default='https://futurenyx.github.io/nina-memory-game')
    a = ap.parse_args()
    print('Building play block...')
    build(a.base)
    print('Done.')
