#!/usr/bin/env python3
"""Screenshot the page at iPhone and desktop sizes, at several scroll depths."""
import os
import sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8765/'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots')
os.makedirs(OUT, exist_ok=True)

DEVICES = [
    # name,        width, height, dpr
    ('iphone',       393,  852,   2),
    ('desktop',     1440,  900,   1),
]

# scroll progress through the hero runway
HERO_P = [0.0, 0.30, 0.58, 0.80, 1.0]


def run():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for name, w, h, dpr in DEVICES:
            ctx = br.new_context(viewport={'width': w, 'height': h},
                                 device_scale_factor=dpr,
                                 is_mobile=(name == 'iphone'),
                                 has_touch=(name == 'iphone'))
            pg = ctx.new_page()
            pg.goto(URL, wait_until='networkidle')
            pg.wait_for_timeout(2500)

            hero = pg.evaluate("""() => {
                const s = document.querySelector('.nsx__scrolly');
                const t = document.querySelector('.nsx__stage');
                return {top: s.offsetTop, runway: s.offsetHeight - t.offsetHeight,
                        end: s.offsetTop + s.offsetHeight};
            }""")

            for i, p in enumerate(HERO_P):
                y = hero['top'] + hero['runway'] * p
                pg.evaluate('window.scrollTo(0, %f)' % y)
                pg.wait_for_timeout(700)
                pg.screenshot(path=os.path.join(OUT, '%s_hero%d.png' % (name, i)))

            # everything below the hero, viewport by viewport
            y = hero['end']
            total = pg.evaluate('document.documentElement.scrollHeight')
            n = 0
            while y < total and n < 8:
                pg.evaluate('window.scrollTo(0, %f)' % y)
                pg.wait_for_timeout(900)
                pg.screenshot(path=os.path.join(OUT, '%s_body%d.png' % (name, n)))
                y += h * 0.92
                n += 1

            errs = pg.evaluate("""() => (window.__errs||[])""")
            print('%s: %d hero + %d body shots, errors: %s' % (name, len(HERO_P), n, errs))
            ctx.close()
        br.close()


if __name__ == '__main__':
    run()
    print('shots in', OUT)
