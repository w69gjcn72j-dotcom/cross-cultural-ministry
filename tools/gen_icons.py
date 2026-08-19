#!/usr/bin/env python3
"""Draw the site icon set.

The mark: two overlapping circles — two cultures, two worlds — with the
cross standing in the overlap, its foot crossing the horizon. Line art in
terracotta on teal ink, the same treatment as the study libraries in the
new palette.

Run from the repo root:   python3 tools/gen_icons.py
Only needs re-running if the mark itself changes.
"""

import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "icons")

INK        = (6, 32, 31)
INK_GLOW   = (16, 60, 57)
CLAY       = (201, 111, 76)
CLAY_SOFT  = (232, 176, 140)
HORIZON    = (146, 112, 94)

S = 1024          # design units
SS = 4            # supersample factor


def draw_mark(pad_frac=0.0):
    """Render the mark at S*SS then downsample. pad_frac shrinks the art
    inward, for maskable icons that get cropped by the launcher."""
    n = S * SS
    img = Image.new("RGB", (n, n), INK)
    d = ImageDraw.Draw(img)

    # a soft glow across the top, so it doesn't read as a flat block
    for i in range(60):
        t = i / 60.0
        y0 = int(n * 0.55 * t)
        col = tuple(
            int(INK[c] + (INK_GLOW[c] - INK[c]) * (1 - t) * 0.5) for c in range(3)
        )
        d.rectangle([0, y0, n, int(n * 0.55 * (t + 1 / 60.0))], fill=col)

    def u(v):
        """design unit -> pixel, honouring the inward padding"""
        centre = S / 2.0
        return (centre + (v - centre) * (1 - pad_frac)) * SS

    w = int(20 * SS * (1 - pad_frac))          # stroke weight

    # horizon
    d.line([u(152), u(690), u(872), u(690)], fill=HORIZON, width=max(1, int(w * 0.8)))

    # two overlapping circles
    r = 205
    for cx in (410, 614):
        d.ellipse(
            [u(cx - r), u(540 - r), u(cx + r), u(540 + r)],
            outline=CLAY, width=w,
        )

    # the cross, standing in the overlap
    d.line([u(512), u(352), u(512), u(792)], fill=CLAY_SOFT, width=int(w * 1.15))
    d.line([u(438), u(470), u(586), u(470)], fill=CLAY_SOFT, width=int(w * 1.15))

    return img.resize((S, S), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    base = draw_mark()
    maskable = draw_mark(pad_frac=0.20)

    for size in (512, 192, 180, 152, 144, 120, 96, 64, 48, 32, 16):
        base.resize((size, size), Image.LANCZOS).save(
            os.path.join(OUT, f"icon-{size}.png")
        )
    maskable.resize((512, 512), Image.LANCZOS).save(
        os.path.join(OUT, "icon-maskable-512.png")
    )
    base.save(os.path.join(OUT, "icon-1024.png"))

    # favicon.ico with the small sizes bundled
    base.resize((64, 64), Image.LANCZOS).save(
        os.path.join(os.path.dirname(HERE), "favicon.ico"),
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )
    print(f"icons written to {OUT}")


if __name__ == "__main__":
    main()
