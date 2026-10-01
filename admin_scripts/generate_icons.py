#!/usr/bin/env python3
"""
FED-SPA icon generator.

Takes the generated 1024x1024 logo and fans it out into every icon size
the project needs:

  web/icons/        icon-192.png, icon-512.png, maskable-512.png
  extension/icons/  icon-16.png, icon-32.png, icon-48.png, icon-128.png
  social banner     FED-SPA/social-image.png (1536x1024 copy)

Strategy:
  * The logo has two zones: the teal emblem (top ~62%) and the wordmark
    (bottom). Tiny icons (16/32) can't render the wordmark, so those use
    an emblem-only crop, auto-detected by scanning for teal pixels.
  * maskable-512.png follows the Android/Chrome maskable convention:
    full-bleed background with content inside the central 80% safe zone.
  * LANCZOS resampling throughout; PNG saved with a matching background
    (no alpha surprises on dark or light toolbars).

Pure Pillow - no third-party services, consistent with the project rules.
"""

import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, '..', 'generated_images',
                    'generated_image_d0736a0b-d0e6-4ee3-b9e0-db94658ecd41_0.png')
BANNER = os.path.join(ROOT, '..', 'generated_images',
                      'generated_image_6ba4e145-1a91-403d-a070-0d63f15af95d_0.png')

WEB_ICONS = os.path.join(ROOT, 'web', 'icons')
EXT_ICONS = os.path.join(ROOT, 'extension', 'icons')


def find_emblem_box(im):
    """Scan for the teal emblem region and return (left, top, right, bottom)."""
    px = im.convert('RGB')
    w, h = px.size
    small = px.resize((256, 256))  # speed: scan a downscaled copy
    sw, sh = small.size
    left, top, right, bottom = sw, sh, 0, 0
    for y in range(sh):
        for x in range(sw):
            r, g, b = small.getpixel((x, y))
            # teal/mint: green strongly dominant, moderate blue, low red
            if g > 140 and b > 90 and b < 200 and r < 110 and g > r + 60:
                if x < left:   left = x
                if x > right:  right = x
                if y < top:    top = y
                if y > bottom: bottom = y
    # scale back up to full resolution
    sx, sy = w / sw, h / sh
    return (int(left * sx), int(top * sy), int(right * sx), int(bottom * sy))


def pad_box(box, frac, w, h):
    """Expand a box outward by frac of its size, clamped to the canvas."""
    l, t, r, b = box
    bw, bh = r - l, b - t
    dx, dy = int(bw * frac), int(bh * frac)
    return (max(0, l - dx), max(0, t - dy), min(w, r + dx), min(h, b + dy))


def square_crop(im, box):
    """Make a box square (grow the short axis) and return the cropped image."""
    l, t, r, b = box
    w, h = im.size
    bw, rh = r - l, b - t
    if bw > rh:
        need = bw - rh
        t = max(0, t - need // 2)
        b = min(h, t + bw)
    else:
        need = rh - bw
        l = max(0, l - need // 2)
        r = min(w, l + rh)
    return im.crop((l, t, r, b))


def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, 'PNG', optimize=True)
    print('  wrote', os.path.relpath(path, ROOT), im.size)


def main():
    logo = Image.open(LOGO).convert('RGB')
    banner = Image.open(BANNER).convert('RGB')
    W, H = logo.size

    print('Detecting emblem region...')
    emblem = find_emblem_box(logo)
    print('  emblem box:', emblem)

    # Emblem-only source: teal mark + breathing room, squared up.
    # The wordmark starts around y=752; cap the bottom padding so the
    # crop never bleeds into the "FED-SPA" text.
    l, t, r, b = pad_box(emblem, 0.16, W, H)
    b = min(b, 740)
    emblem_src = square_crop(logo, (l, t, r, b))

    # Full-logo source: square already (1024x1024), everything visible.
    full_src = logo

    # ---------------- web icons ----------------
    print('Web icons:')
    save(full_src.resize((192, 192), Image.LANCZOS),
         os.path.join(WEB_ICONS, 'icon-192.png'))
    save(full_src.resize((512, 512), Image.LANCZOS),
         os.path.join(WEB_ICONS, 'icon-512.png'))

    # Maskable: emblem inside the 80% safe zone on a full-bleed background.
    # Background sampled from the logo's own corner so it matches the brand.
    corner = logo.getpixel((10, 10))
    canvas = Image.new('RGB', (512, 512), corner)
    safe = int(512 * 0.80)                 # 409 -> content diameter
    mark = emblem_src.resize((safe, safe), Image.LANCZOS)
    canvas.paste(mark, ((512 - safe) // 2, (512 - safe) // 2))
    save(canvas, os.path.join(WEB_ICONS, 'maskable-512.png'))

    # ---------------- extension icons ----------------
    print('Extension icons:')
    # 16/32 are too small for the wordmark -> emblem only.
    save(emblem_src.resize((16, 16), Image.LANCZOS),
         os.path.join(EXT_ICONS, 'icon-16.png'))
    save(emblem_src.resize((32, 32), Image.LANCZOS),
         os.path.join(EXT_ICONS, 'icon-32.png'))
    save(full_src.resize((48, 48), Image.LANCZOS),
         os.path.join(EXT_ICONS, 'icon-48.png'))
    save(full_src.resize((128, 128), Image.LANCZOS),
         os.path.join(EXT_ICONS, 'icon-128.png'))

    # ---------------- social preview ----------------
    print('Social image:')
    save(banner, os.path.join(ROOT, 'social-image.png'))

    print('Done.')


if __name__ == '__main__':
    main()
