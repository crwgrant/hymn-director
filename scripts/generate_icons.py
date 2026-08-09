#!/usr/bin/env python3
"""Generate platform icon files from the master PNG."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ICONS_DIR = PROJECT_ROOT / "assets" / "icons"
SOURCE = ICONS_DIR / "hymn-director-1024.png"

ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
ICNS_SIZES = [16, 32, 64, 128, 256, 512, 1024]


def generate_png_sizes(image: Image.Image) -> None:
    for size in (256, 128, 64, 48, 32, 16):
        target = ICONS_DIR / f"hymn-director-{size}.png"
        resized = image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(target, format="PNG")
        print(f"Wrote {target.relative_to(PROJECT_ROOT)}")


def generate_ico(image: Image.Image) -> None:
    target = ICONS_DIR / "hymn-director.ico"
    images = [
        image.resize((size, size), Image.Resampling.LANCZOS) for size in ICO_SIZES
    ]
    images[0].save(
        target,
        format="ICO",
        sizes=[(size, size) for size in ICO_SIZES],
        append_images=images[1:],
    )
    print(f"Wrote {target.relative_to(PROJECT_ROOT)}")


def generate_icns(image: Image.Image) -> None:
    target = ICONS_DIR / "hymn-director.icns"
    if sys.platform != "darwin":
        print("Skipping ICNS generation (requires macOS iconutil).")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        iconset = Path(temp_dir) / "hymn-director.iconset"
        iconset.mkdir()

        for size in ICNS_SIZES:
            resized = image.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(iconset / f"icon_{size}x{size}.png", format="PNG")
            if size <= 512:
                double = size * 2
                doubled = image.resize((double, double), Image.Resampling.LANCZOS)
                doubled.save(iconset / f"icon_{size}x{size}@2x.png", format="PNG")

        subprocess.run(
            ["iconutil", "-c", "icns", str(iconset), "-o", str(target)],
            check=True,
        )

    print(f"Wrote {target.relative_to(PROJECT_ROOT)}")


def main() -> int:
    if not SOURCE.exists():
        print(f"Missing source icon: {SOURCE}", file=sys.stderr)
        return 1

    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(SOURCE).convert("RGBA")

    generate_png_sizes(image)
    generate_ico(image)
    generate_icns(image)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
