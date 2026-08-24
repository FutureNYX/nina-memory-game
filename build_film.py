#!/usr/bin/env python3
"""
Builds the film blocks - each one paste into a Tilda T123 "HTML-код" block.

    python build_film.py --base https://futurenyx.github.io/nina-memory-game

  film-block.html        vertical 9:16 cut,  1080x1920 / 720x1280
  film-wide-block.html   landscape 16:9 cut, 1920x1080 / 1280x720

The films are served from GitHub Pages rather than uploaded to Tilda, so
Tilda's 5 MB ceiling never applies to them. Nothing downloads until the
visitor presses play: preload="none" behind a poster image.
"""
import argparse
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

JS = """(function () {
  'use strict';
  var wraps = document.querySelectorAll('.nsxf');
  Array.prototype.forEach.call(wraps, function (wrap) {
    var v = wrap.querySelector('video');
    var btn = wrap.querySelector('.nsxf__play');
    if (!v || !btn || v.src) return;

    /* Pick a file once, at load. Narrow screens and data-saver get the
       small one. preload is "none", so choosing a source costs nothing
       until play is actually pressed. */
    var conn = navigator.connection || {};
    var small = Math.min(screen.width, screen.height) < 500;
    v.src = (conn.saveData || small)
      ? v.getAttribute('data-src-lo')
      : v.getAttribute('data-src-hi');

    btn.addEventListener('click', function () {
      btn.hidden = true;
      var q = v.play();
      if (q && q.catch) q.catch(function () { btn.hidden = false; });
    });
    v.addEventListener('ended', function () { btn.hidden = false; });
    v.addEventListener('pause', function () {
      if (v.currentTime > 0 && !v.ended && v.currentTime < v.duration) return;
      btn.hidden = false;
    });
  });
})();"""

HEADER = """<!-- ===========================================================
     NINA SECHKO x ROBINEAU - the film (%(shape)s)

     PASTE ALL OF THIS INTO ONE TILDA BLOCK:
       Библиотека блоков -> Другое -> T123 "HTML-код"

     The film is NOT uploaded to Tilda, so Tilda's 5 MB ceiling
     does not apply to it. It streams from:
       %(base)s
     %(hi_note)s on a normal screen, %(lo_note)s on a narrow one,
     chosen automatically. Nothing downloads until the visitor
     presses play - scrolling past costs only the poster image.

     Worth knowing, near the top of the CSS:
       --ground                 background colour of this section
       --film-ar / --film-ar-num  shape of the film (%(ar)s)
       --film-max-h / --film-max-w  how large it is allowed to get
     =========================================================== -->"""

FILMS = [
    dict(out='film-block.html',
         shape='vertical', ar='9/16', ar_num='0.5625',
         hi='/media/film.mp4', lo='/media/film-720.mp4',
         poster='/media/film-poster.webp',
         hi_note='1080x1920 (34 MB)', lo_note='720x1280 (13 MB)',
         caption='Фильм со звуком &mdash; 43 секунды'),
    dict(out='film-wide-block.html',
         shape='landscape', ar='16/9', ar_num='1.7778',
         hi='/media/film-wide.mp4', lo='/media/film-wide-720.mp4',
         poster='/media/film-wide-poster.webp',
         hi_note='1920x1080 (37 MB)', lo_note='1280x720 (12 MB)',
         caption='Фильм со звуком &mdash; 42 секунды'),
]


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def build_one(f, base):
    base = base.rstrip('/')

    css = read('film.css')
    css = css.replace('  --film-ar:9/16;\n  --film-ar-num:0.5625;',
                      '  --film-ar:%s;\n  --film-ar-num:%s;' % (f['ar'], f['ar_num']))

    body = read('film.html')
    body = body.replace('{{POSTER}}', base + f['poster'])
    body = body.replace('{{SRC_HI}}', base + f['hi'])
    body = body.replace('{{SRC_LO}}', base + f['lo'])
    body = body.replace('{{CAPTION}}', f['caption'])

    parts = [
        HEADER % {'shape': f['shape'], 'base': base, 'ar': f['ar'],
                  'hi_note': f['hi_note'], 'lo_note': f['lo_note']},
        '<style>\n'
        "/* let the block escape Tilda's 960px container */\n"
        '.t-rec .t123__wrapper,.t123 .t-container,.t123 .t-col'
        '{max-width:100%!important;padding:0!important;margin:0!important}\n'
        + css + '</style>',
        body,
        '<script>\n' + JS + '\n</script>',
    ]
    text = '\n\n'.join(parts) + '\n'

    path = os.path.join(HERE, 'tilda', f['out'])
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with io.open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)
    n = len(text.encode('utf-8'))
    print('  %-24s %5d bytes (%.0f%% of limit)  %s %s'
          % (f['out'], n, n / 1000.0, f['shape'], f['ar']))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--base',
                    default='https://futurenyx.github.io/nina-memory-game')
    a = ap.parse_args()
    print('Building film blocks...')
    for f in FILMS:
        build_one(f, a.base)
    print('Done.')
