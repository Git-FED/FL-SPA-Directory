#!/usr/bin/env python3
"""
FED-SPA Android mipmap generator.

Produces launcher icons in the five standard densities:
  mdpi 48px, hdpi 72px, xhdpi 96px, xxhdpi 144px, xxxhdpi 192px

Two flavors per density:
  ic_launcher.png        (adaptive-style square, full logo with wordmark zone)
  ic_launcher_round.png  (circular crop of the emblem zone)

All from the same source logo used by web/extension icons, so every
platform shares one brand asset. Pure Pillow.
"""

import os
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(ROOT, '..', 'generated_images',
                    'generated_image_d0736a0b-d0e6-4ee3-b9e0-db94658ecd41_0.png')

RES = os.path.join(ROOT, 'android', 'app', 'src', 'main', 'res')

DENSITIES = {
    'mipmap-mdpi':    48,
    'mipmap-hdpi':    72,
    'mipmap-xhdpi':   96,
    'mipmap-xxhdpi':  144,
    'mipmap-xxxhdpi': 192,
}


def main():
    logo = Image.open(LOGO).convert('RGB')
    W, H = logo.size

    # emblem zone (must match generate_icons.py: teal mark, capped above
    # the wordmark at y=740)
    l, t, r, b = 232, 128, 788, 740
    emblem = logo.crop((l, t, r, b))
    # square it up
    ew, eh = emblem.size
    side = max(ew, eh)
    emblem = ImageOps.pad(emblem, (side, side), method=Image.LANCZOS,
                          color=logo.getpixel((10, 10)))

    for folder, size in DENSITIES.items():
        out_dir = os.path.join(RES, folder)
        os.makedirs(out_dir, exist_ok=True)

        # square launcher: whole logo (emblem + wordmark zones)
        square = logo.resize((size, size), Image.LANCZOS)
        square.save(os.path.join(out_dir, 'ic_launcher.png'), 'PNG', optimize=True)
        print(f'  wrote android res/{folder}/ic_launcher.png {size}x{size}')

        # round launcher: circular emblem
        big = emblem.resize((size, size), Image.LANCZOS).convert('RGBA')
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        big.putalpha(mask)
        big.save(os.path.join(out_dir, 'ic_launcher_round.png'), 'PNG', optimize=True)
        print(f'  wrote android res/{folder}/ic_launcher_round.png {size}x{size}')

    print('Done.')


if __name__ == '__main__':
    main()
