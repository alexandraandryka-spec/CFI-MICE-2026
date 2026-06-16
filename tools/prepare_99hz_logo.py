from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(
    r"C:\Users\Rafal\AppData\Local\Temp\codex-clipboard-0221408a-6eb4-46c6-913d-78a23fc97263.png"
)
ASSETS = ROOT / "deliverables" / "cfi_mice_newsletter" / "assets"


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    source.save(ASSETS / "99hz-logo-source.png")

    luminance = source.convert("L")
    alpha = luminance.point(lambda value: max(0, min(255, round((value - 155) * 5.1))))
    logo = Image.new("RGBA", source.size, (255, 255, 255, 0))
    logo.putalpha(alpha)
    logo = logo.resize((1196, 1032), Image.Resampling.LANCZOS)
    logo.save(ASSETS / "99hz-logo-white.png", optimize=True)


if __name__ == "__main__":
    main()
