from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work" / "pdf_inspection"
OUT = ROOT / "deliverables" / "cfi_mice_newsletter" / "assets"


def save_cover(source: Path, target: Path, size: tuple[int, int], crop=None) -> None:
    image = Image.open(source).convert("RGB")
    if crop:
        image = image.crop(crop)
    image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(1.04)
    image = ImageEnhance.Color(image).enhance(0.94)
    image.save(target, "JPEG", quality=91, optimize=True, progressive=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    hz = SOURCE / "99hz" / "images"
    tektura = SOURCE / "tektura" / "images"

    save_cover(
        hz / "page-02-img-01-xref-18.jpeg",
        OUT / "99hz-banquet.jpg",
        (1400, 900),
        crop=(1310, 0, 2600, 1463),
    )
    save_cover(
        hz / "page-03-img-01-xref-22.jpeg",
        OUT / "99hz-conference.jpg",
        (1400, 900),
        crop=(0, 0, 1325, 1463),
    )
    save_cover(
        hz / "page-04-img-01-xref-26.jpeg",
        OUT / "99hz-theatre.jpg",
        (1000, 1200),
        crop=(1280, 0, 2600, 1463),
    )

    save_cover(
        tektura / "page-02-img-01-xref-3.jpeg",
        OUT / "tektura-exterior.jpg",
        (1000, 1200),
    )
    save_cover(
        tektura / "page-11-img-02-xref-53.jpeg",
        OUT / "tektura-hall.jpg",
        (1400, 1000),
    )
    save_cover(
        tektura / "page-08-img-01-xref-38.jpeg",
        OUT / "tektura-evening.jpg",
        (1400, 900),
    )
    save_cover(
        tektura / "page-14-img-01-xref-68.jpeg",
        OUT / "tektura-detail.jpg",
        (1000, 1200),
    )

    tektura_slide = Image.open(
        SOURCE / "tektura" / "pages" / "page-08.png"
    ).convert("RGB")
    tektura_slide = tektura_slide.resize((1600, 900), Image.Resampling.LANCZOS)
    tektura_slide.save(
        OUT / "tektura-collage.jpg",
        "JPEG",
        quality=92,
        optimize=True,
        progressive=True,
    )

    polmo_page = Image.open(
        SOURCE / "polmo-1978" / "pages" / "page-16.png"
    ).convert("RGB")
    archive_crop = polmo_page.crop((145, 95, 1215, 1015))
    archive_crop = ImageOps.fit(
        archive_crop, (1200, 820), method=Image.Resampling.LANCZOS
    )
    archive_crop = ImageOps.grayscale(archive_crop).convert("RGB")
    archive_crop = ImageEnhance.Contrast(archive_crop).enhance(1.16)
    archive_crop.save(
        OUT / "polmo-archive-hall.jpg",
        "JPEG",
        quality=91,
        optimize=True,
        progressive=True,
    )

    scheibler_source = OUT / "scheibler-archive-original.jpg"
    if scheibler_source.exists():
        scheibler = Image.open(scheibler_source).convert("RGB")
        scheibler = ImageOps.grayscale(scheibler).convert("RGB")
        scheibler = ImageEnhance.Contrast(scheibler).enhance(1.10)
        scheibler.save(
            OUT / "scheibler-archive.jpg",
            "JPEG",
            quality=92,
            optimize=True,
            progressive=True,
        )

    arrangement_sources = {
        "99hz-classroom-plan.jpg": ROOT / "work" / "1 (1).png",
        "99hz-horseshoe-plan.jpg": ROOT / "work" / "2 (1).png",
        "99hz-banquet-plan.jpg": ROOT / "work" / "3 (1).png",
    }
    for target_name, source_path in arrangement_sources.items():
        plan = Image.open(source_path).convert("RGB")
        plan = plan.crop((720, 170, 2240, 1580))
        plan = ImageOps.contain(plan, (900, 720), method=Image.Resampling.LANCZOS)
        background = Image.new("RGB", (900, 720), "white")
        background.paste(
            plan,
            ((background.width - plan.width) // 2, (background.height - plan.height) // 2),
        )
        background.save(
            OUT / target_name,
            "JPEG",
            quality=91,
            optimize=True,
            progressive=True,
        )


if __name__ == "__main__":
    main()
