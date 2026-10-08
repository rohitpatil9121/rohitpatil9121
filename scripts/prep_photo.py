"""Prep a photo for ASCII conversion: isolate subject, boost contrast, put on white.

    python scripts/prep_photo.py source-photo.jpg

Writes source-prepped.png (grayscale) in the repo root. rembg and OpenCV are
optional: without rembg the background is kept, without OpenCV a global
equalization is used instead of CLAHE.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"


def remove_background(img):
    try:
        from rembg import remove
    except ImportError:
        print("rembg not installed - keeping the original background")
        return img.convert("RGBA")
    return remove(img).convert("RGBA")


def boost_contrast(gray):
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("opencv not installed - using global equalization instead of CLAHE")
        return ImageOps.autocontrast(ImageOps.equalize(gray), cutoff=1)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return Image.fromarray(clahe.apply(np.asarray(gray)))


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/prep_photo.py <photo>")
    img = ImageOps.exif_transpose(Image.open(sys.argv[1]))
    cut = remove_background(img)
    alpha = cut.getchannel("A")

    gray = boost_contrast(cut.convert("L"))

    # White background maps to the blank end of the ASCII ramp.
    out = Image.new("L", cut.size, 255)
    out.paste(gray, mask=alpha)

    # Crop to the subject so it fills the character grid.
    bbox = alpha.point(lambda a: 255 if a > 16 else 0).getbbox()
    if bbox:
        out = out.crop(bbox)

    out.save(OUT)
    print(f"wrote {OUT.name} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
