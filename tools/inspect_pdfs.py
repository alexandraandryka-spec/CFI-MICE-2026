from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work" / "pdf_inspection"
SOURCES = {
    "99hz": Path(r"C:\Users\Rafal\AppData\Local\Temp\99hz PREZENTACJA (1).pdf"),
    "tektura": Path(r"C:\Users\Rafal\AppData\Local\Temp\TEKTURA PREZENTACJA 2026 (1).pdf"),
    "polmo-1978": Path(r"C:\Users\Rafal\Downloads\Informator-POLMO-Lodz-1978.pdf"),
}


def render_pdf(name: str, source: Path) -> None:
    target = OUT / name
    pages_dir = target / "pages"
    images_dir = target / "images"
    pages_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(source)
    report = [f"SOURCE: {source}", f"PAGES: {doc.page_count}", ""]
    thumbs = []

    for page_index, page in enumerate(doc):
        page_no = page_index + 1
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        page_path = pages_dir / f"page-{page_no:02d}.png"
        pix.save(page_path)

        thumb = Image.open(page_path).convert("RGB")
        thumb.thumbnail((420, 280))
        thumbs.append((page_no, thumb.copy()))

        report.extend([f"--- PAGE {page_no} ---", page.get_text("text").strip(), ""])

        for image_index, image_info in enumerate(page.get_images(full=True), start=1):
            xref = image_info[0]
            image_data = doc.extract_image(xref)
            ext = image_data["ext"]
            image_path = images_dir / f"page-{page_no:02d}-img-{image_index:02d}-xref-{xref}.{ext}"
            if not image_path.exists():
                image_path.write_bytes(image_data["image"])

    (target / "text.txt").write_text("\n".join(report), encoding="utf-8")

    cell_w, cell_h = 460, 330
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for idx, (page_no, thumb) in enumerate(thumbs):
        x = (idx % cols) * cell_w
        y = (idx // cols) * cell_h
        sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + 28))
        draw.text((x + 12, y + 8), f"{name} / page {page_no}", fill="black", font=font)
    sheet.save(target / "contact-sheet.jpg", quality=90)

    image_paths = sorted(images_dir.iterdir())
    image_thumbs = []
    for image_path in image_paths:
        try:
            source_image = Image.open(image_path).convert("RGB")
        except Exception:
            continue
        source_image.thumbnail((300, 210))
        image_thumbs.append((image_path.name, source_image.copy()))

    image_cell_w, image_cell_h = 340, 265
    image_cols = 4
    image_rows = (len(image_thumbs) + image_cols - 1) // image_cols
    image_sheet = Image.new(
        "RGB", (image_cols * image_cell_w, image_rows * image_cell_h), "white"
    )
    image_draw = ImageDraw.Draw(image_sheet)
    for idx, (filename, thumb) in enumerate(image_thumbs):
        x = (idx % image_cols) * image_cell_w
        y = (idx // image_cols) * image_cell_h
        image_sheet.paste(thumb, (x + (image_cell_w - thumb.width) // 2, y + 35))
        image_draw.text((x + 8, y + 8), filename, fill="black", font=font)
    image_sheet.save(target / "image-catalog.jpg", quality=90)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        render_pdf(name, source)


if __name__ == "__main__":
    main()
