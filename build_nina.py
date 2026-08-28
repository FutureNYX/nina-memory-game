#!/usr/bin/env python3
"""
Re-encodes the two Nina films from their 4K masters to full HD for the web.

    python build_nina.py

The masters live in _orig/ (pulled from Drive, "Nina's videos") and are 4K
HEVC at ~36 Mbps, which no browser should be asked to stream. Each becomes:

  media/nina-wide.mp4      1920x1080  CRF 19, the desktop hero
  media/nina-wide-720.mp4  1280x720   CRF 23, narrow screens and data-saver
  media/nina-vertical.mp4  1080x1920  CRF 19, the phone hero
  media/nina-vertical-720.mp4  720x1280

New filenames on purpose: film.mp4 and film-wide.mp4 stay put so the old
blocks keep working, and a changed name defeats the CDN and browser caches
that would otherwise keep serving the softer file.

CRF 19 at 1080p downscaled from 4K is visually transparent at normal viewing
distance; the previous 7 Mbps encode was not, which is the whole reason for
this pass. -movflags +faststart puts the index at the front so playback can
begin on the first range request instead of after a full download.
"""
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(HERE, '_orig')
MEDIA = os.path.join(HERE, 'media')

# (master, output stem, full-HD scale, fallback scale, poster timestamp)
JOBS = [
    ('Nina wide.MOV',     'nina-wide',     '1920:1080', '1280:720',  '1.0'),
    ('Nina vertical.MOV', 'nina-vertical', '1080:1920', '720:1280',  '1.0'),
]


def run(*args):
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-stats'] + list(args))


def encode(src, dst, scale, crf, abr):
    run('-i', src,
        '-vf', 'scale=%s:flags=lanczos' % scale,
        '-c:v', 'libx264', '-profile:v', 'high', '-preset', 'slow',
        '-crf', str(crf), '-pix_fmt', 'yuv420p',
        # keyframe every 2 s: enough for responsive seeking without
        # inflating the file the way an all-intra encode would
        '-g', '60', '-keyint_min', '60', '-sc_threshold', '0',
        '-c:a', 'aac', '-b:a', abr, '-ar', '48000', '-ac', '2',
        '-movflags', '+faststart',
        dst)


def poster(src, dst, scale, ts):
    run('-ss', ts, '-i', src, '-frames:v', '1',
        '-vf', 'scale=%s:flags=lanczos' % scale,
        '-c:v', 'libwebp', '-quality', '82', dst)


def main():
    os.makedirs(MEDIA, exist_ok=True)
    for master, stem, hi, lo, ts in JOBS:
        src = os.path.join(ORIG, master)
        if not os.path.exists(src):
            raise SystemExit('missing master: ' + src)
        print('==', stem, 'full HD')
        encode(src, os.path.join(MEDIA, stem + '.mp4'), hi, 19, '160k')
        print('==', stem, 'fallback')
        encode(src, os.path.join(MEDIA, stem + '-720.mp4'), lo, 23, '128k')
        print('==', stem, 'poster')
        poster(src, os.path.join(MEDIA, stem + '-poster.webp'), hi, ts)
        for suffix in ('.mp4', '-720.mp4', '-poster.webp'):
            p = os.path.join(MEDIA, stem + suffix)
            print('   %-28s %6.1f MB' % (stem + suffix, os.path.getsize(p) / 1e6))


if __name__ == '__main__':
    main()
