#!/usr/bin/env python3
"""
Rebuilds frames/ and media/ from the source film.

    python extract.py "C:/path/to/nina-ad-6.mp4"

What it does, and why:

  * Samples 0.00 - 9.60 s at 15 fps into 756x1344 WebP (q72). That window is
    closed box -> box opens -> cards burst out. Everything after it is the
    gameplay demo, which becomes media/play.mp4 instead.
  * Drops sampled frames 56-61. CapCut put a white light-leak transition at
    ~3.7 s; on a slow scroll it reads as a glitch. The box keeps turning
    smoothly across the cut, so removing them is invisible in motion.
  * Drops everything after frame 123 (~8.5 s), where the cards have left the
    frame and it is just empty white.
  * Renumbers what is left to f_001..f_123 contiguously.

If you re-cut the film, run this, then set NSX_CONFIG.frameCount in
src/app.js to the printed count and re-run build.py.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SEQ_START, SEQ_DUR, FPS = 0.0, 9.60, 15
W, H = 756, 1344
DROP = set(range(56, 62))     # the light-leak transition
KEEP_UNTIL = 129              # sampled-frame index; 123 survive after DROP

PLAY_START, PLAY_DUR = 10.30, 9.90

STILLS = [(6.40, 'still-open'), (10.80, 'still-spread'),
          (13.20, 'still-backs'), (16.40, 'still-play')]


def run(*args):
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error'] + list(args))


def main(src):
    frames = os.path.join(HERE, 'frames')
    media = os.path.join(HERE, 'media')
    tmp = os.path.join(HERE, '_raw')
    for d in (frames, media, tmp):
        if not os.path.isdir(d):
            os.makedirs(d)
    for f in os.listdir(frames):
        os.remove(os.path.join(frames, f))
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))

    print('sampling sequence...')
    run('-ss', str(SEQ_START), '-t', str(SEQ_DUR), '-i', src,
        '-vf', 'fps=%d,scale=%d:%d:flags=lanczos' % (FPS, W, H),
        '-c:v', 'libwebp', '-quality', '72', '-compression_level', '6',
        '-preset', 'photo', os.path.join(tmp, 'r_%03d.webp'))

    n = 0
    for i in range(1, KEEP_UNTIL + 1):
        srcf = os.path.join(tmp, 'r_%03d.webp' % i)
        if i in DROP or not os.path.exists(srcf):
            continue
        n += 1
        os.replace(srcf, os.path.join(frames, 'f_%03d.webp' % n))
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)

    print('gameplay loop...')
    run('-ss', str(PLAY_START), '-t', str(PLAY_DUR), '-i', src, '-an',
        '-vf', 'scale=720:1280:flags=lanczos', '-c:v', 'libx264',
        '-profile:v', 'high', '-level', '4.0', '-crf', '27', '-preset', 'slow',
        '-pix_fmt', 'yuv420p', '-g', '60', '-movflags', '+faststart',
        os.path.join(media, 'play.mp4'))

    print('poster, og, stills...')
    run('-ss', '0', '-i', src, '-frames:v', '1',
        '-vf', 'scale=%d:%d:flags=lanczos' % (W, H),
        '-c:v', 'libwebp', '-quality', '88', os.path.join(media, 'poster.webp'))
    run('-ss', '2.9', '-i', src, '-frames:v', '1',
        '-vf', 'scale=1200:-2:flags=lanczos,crop=1200:630',
        '-q:v', '4', os.path.join(media, 'og.jpg'))
    for t, name in STILLS:
        run('-ss', str(t), '-i', src, '-frames:v', '1',
            '-vf', 'scale=900:1600:flags=lanczos',
            '-c:v', 'libwebp', '-quality', '80',
            os.path.join(media, name + '.webp'))

    kb = sum(os.path.getsize(os.path.join(frames, f))
             for f in os.listdir(frames)) / 1024.0
    print('\n%d frames, %.1f MB' % (n, kb / 1024.0))
    print('-> set NSX_CONFIG.frameCount = %d in src/app.js, then run build.py' % n)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
