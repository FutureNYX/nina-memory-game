#!/usr/bin/env python3
"""
Builds tilda/film-block.html - the brand film as one paste into a Tilda
T123 "HTML-код" block.

    python build_film.py --base https://futurenyx.github.io/nina-memory-game

The film is served from GitHub Pages rather than uploaded to Tilda, so it
is not squeezed through Tilda's 5 MB ceiling: 34 MB at 1080p, or 13 MB at
720p for narrow screens, chosen at load. Nothing downloads until the
visitor presses play.
"""
import argparse
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

JS = """(function () {
  'use strict';
  var wrap = document.querySelector('.nsxf');
  if (!wrap) return;
  var v = wrap.querySelector('video');
  var btn = wrap.querySelector('.nsxf__play');
  if (!v || !btn) return;

  /* Pick a file once, at load. Narrow screens and data-saver get the 13 MB
     720p; everything else the 34 MB 1080p. preload is "none", so choosing
     a source costs nothing until play is pressed. */
  function chooseSrc() {
    var conn = navigator.connection || {};
    var small = Math.min(screen.width, screen.height) < 500;
    if (conn.saveData || small) return v.getAttribute('data-src-lo');
    return v.getAttribute('data-src-hi');
  }
  v.src = chooseSrc();

  btn.addEventListener('click', function () {
    btn.hidden = true;
    var q = v.play();
    if (q && q.catch) q.catch(function () { btn.hidden = false; });
  });

  /* bring the button back when the film ends or is paused */
  v.addEventListener('ended', function () { btn.hidden = false; });
  v.addEventListener('pause', function () {
    if (v.currentTime > 0 && !v.ended && v.currentTime < v.duration) return;
    btn.hidden = false;
  });
})();"""

HEADER = """<!-- ===========================================================
     NINA SECHKO x ROBINEAU - the film

     PASTE ALL OF THIS INTO ONE TILDA BLOCK:
       Библиотека блоков -> Другое -> T123 "HTML-код"

     The film is NOT uploaded to Tilda, so Tilda's 5 MB ceiling
     does not apply to it. It streams from:
       %s
     1080p (34 MB) on a normal screen, 720p (13 MB) on a narrow
     one. Nothing downloads until the visitor presses play - a
     visitor who scrolls past pays only for the 47 KB poster.

     Worth knowing, near the top of the CSS:
       --ground      background colour of this section
       --film-max-h  how large the film is allowed to get (82svh)
     =========================================================== -->"""


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def build(base):
    base = base.rstrip('/')
    parts = [
        HEADER % base,
        '<style>\n'
        "/* let the block escape Tilda's 960px container */\n"
        '.t-rec .t123__wrapper,.t123 .t-container,.t123 .t-col'
        '{max-width:100%!important;padding:0!important;margin:0!important}\n'
        + read('film.css') + '</style>',
        read('film.html').replace('{{BASE}}', base),
        '<script>\n' + JS + '\n</script>',
    ]
    text = '\n\n'.join(parts) + '\n'

    path = os.path.join(HERE, 'tilda', 'film-block.html')
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    n = len(text.encode('utf-8'))
    print('  film-block.html  %d bytes (%.0f%% of Tilda limit)' % (n, n / 1000.0))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base',
                    default='https://futurenyx.github.io/nina-memory-game')
    a = ap.parse_args()
    print('Building film block...')
    build(a.base)
    print('Done.')
