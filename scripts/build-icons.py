#!/usr/bin/env python3
"""Готовит иконки для манифеста и PWA из brand/logo-tile-512.png.

Запуск: python3 scripts/build-icons.py
Результат: brand/icon-192.png, brand/icon-512.png, brand/icon-maskable-512.png
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
SOURCE = BRAND / "logo-tile-512.png"

NAVY = (11, 18, 32, 255)


def square(size: int) -> Image.Image:
    return Image.open(SOURCE).convert("RGBA").resize((size, size), Image.LANCZOS)


def maskable(size: int, safe: float = 0.72) -> Image.Image:
    """Иконка с безопасной зоной: логотип занимает 72% полотна, края — фон."""
    canvas = Image.new("RGBA", (size, size), NAVY)
    inner = square(int(size * safe))
    offset = (size - inner.width) // 2
    canvas.alpha_composite(inner, (offset, offset))
    return canvas


def main() -> None:
    square(192).save(BRAND / "icon-192.png")
    square(512).save(BRAND / "icon-512.png")
    maskable(512).save(BRAND / "icon-maskable-512.png")
    maskable(192).save(BRAND / "icon-maskable-192.png")

    for name in ("icon-192.png", "icon-512.png", "icon-maskable-512.png", "icon-maskable-192.png"):
        path = BRAND / name
        with Image.open(path) as im:
            print(f"{name}: {im.size[0]}x{im.size[1]}, {path.stat().st_size // 1024} КБ")


if __name__ == "__main__":
    main()
