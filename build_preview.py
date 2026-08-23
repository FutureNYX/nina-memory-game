#!/usr/bin/env python3
"""
Builds preview.html - the same page with every asset inlined as a data URI,
so it can be published somewhere with a strict CSP (or emailed, or opened
straight off a phone) with no asset host at all.

This is a PREVIEW of the design and the scroll feel only. The real build
streams frames in two passes; this one waits for the whole file. Use
build.py for anything that ships.
"""
import base64
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')

MIME = {'.webp': 'image/webp', '.jpg': 'image/jpeg',
        '.png': 'image/png', '.mp4': 'video/mp4'}


def read(name):
    with io.open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return fh.read()


def datauri(path):
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'rb') as fh:
        return 'data:%s;base64,%s' % (MIME[ext],
                                      base64.b64encode(fh.read()).decode('ascii'))


def main():
    page, css, js = read('page.html'), read('style.css'), read('app.js')

    frames = sorted(f for f in os.listdir(os.path.join(HERE, 'frames'))
                    if f.endswith('.webp'))
    uris = [datauri(os.path.join(HERE, 'frames', f)) for f in frames]
    frames_js = 'window.NSX_FRAMES=[\n' + ',\n'.join('"%s"' % u for u in uris) + '\n];'

    # swap every {{BASE}}/media/... reference for its data URI
    body = page
    for f in os.listdir(os.path.join(HERE, 'media')):
        token = '{{BASE}}/media/' + f
        if token in body:
            body = body.replace(token, datauri(os.path.join(HERE, 'media', f)))
    body = body.replace('{{BASE}}', '.')

    html = u"""<title>Sechko Memory Game</title>
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ECEDF1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500&family=Golos+Text:wght@400;500;600&display=swap">
<style>
html,body{margin:0;padding:0;background:#ECEDF1}
%(css)s
</style>
%(body)s
<script>document.documentElement.lang="ru";</script>
<script>%(frames)s</script>
<script>
%(js)s
</script>
""" % {'css': css, 'body': body, 'frames': frames_js, 'js': js}

    out = os.path.join(HERE, 'preview.html')
    with io.open(out, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(html)
    print('preview.html  %.2f MB  (%d frames inlined)'
          % (len(html.encode('utf-8')) / 1048576.0, len(uris)))


if __name__ == '__main__':
    main()
