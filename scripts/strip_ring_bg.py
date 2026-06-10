"""Convert the hero ring PNGs from black-background to true alpha transparency.

Alpha is derived from pixel luminance (max channel), then color is
unpremultiplied so strands stay vivid when composited over any backdrop.
"""

from PIL import Image

JOBS = [
    (r"C:\Users\Prince\Downloads\ring 1.png", r"src\assets\ring-1.png", None),
    (r"C:\Users\Prince\Downloads\ring 2.png", r"src\assets\ring-2.png", 880),
]


def to_alpha(src: str, dst: str, max_width: int | None) -> None:
    img = Image.open(src).convert("RGB")
    if max_width and img.width > max_width:
        img = img.resize((max_width, round(img.height * max_width / img.width)), Image.LANCZOS)
    pixels = img.load()
    out = Image.new("RGBA", img.size)
    out_pixels = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            a = max(r, g, b)
            if a == 0:
                out_pixels[x, y] = (0, 0, 0, 0)
            else:
                out_pixels[x, y] = (
                    min(255, r * 255 // a),
                    min(255, g * 255 // a),
                    min(255, b * 255 // a),
                    a,
                )
    out.save(dst, optimize=True)
    print(f"{dst}: {img.width}x{img.height}")


if __name__ == "__main__":
    for src, dst, max_width in JOBS:
        to_alpha(src, dst, max_width)
