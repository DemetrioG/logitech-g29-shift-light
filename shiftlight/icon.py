"""Ícone: 5 LEDs. Coloridos quando conectado ao jogo, cinza quando ocioso."""
from PIL import Image, ImageDraw

COLORS = ("#2ecc71", "#2ecc71", "#f1c40f", "#e67e22", "#e74c3c")


def make_icon(lit: bool = True, size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, size * 0.25, size - 1, size * 0.75), radius=size * 0.12, fill="#1e1e24")
    r = size * 0.075
    for i, color in enumerate(COLORS):
        cx = size * (0.14 + 0.18 * i)
        cy = size * 0.5
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color if lit else "#5a5a66")
    return img
