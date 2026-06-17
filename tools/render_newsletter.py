from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables" / "cfi_mice_newsletter"
ASSETS = OUT / "assets"

W = 1440
S = 2

INK = "#171612"
CHARCOAL = "#24211d"
CHOCOLATE = "#301d0d"
WOOD = "#6d543b"
PAPER = "#f1eadf"
PAPER_DEEP = "#e5d7c4"
COPPER = "#ad6f45"
COPPER_LIGHT = "#d4a47f"
WHITE = "#fffdf8"
MUTED_WHITE = "#d8d3ca"

FONT_DIR = Path(r"C:\Windows\Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_DIR / name, size)


F = {
    "sans_20": font("arial.ttf", 20),
    "sans_22": font("arial.ttf", 22),
    "sans_24": font("arial.ttf", 24),
    "sans_28": font("arial.ttf", 28),
    "sans_bold_13": font("arialbd.ttf", 13),
    "sans_bold_20": font("arialbd.ttf", 20),
    "sans_bold_24": font("arialbd.ttf", 24),
    "sans_bold_28": font("arialbd.ttf", 28),
    "serif_28": font("georgia.ttf", 28),
    "serif_38": font("georgia.ttf", 38),
    "serif_44": font("georgia.ttf", 44),
    "serif_52": font("georgia.ttf", 52),
    "serif_62": font("georgia.ttf", 62),
    "serif_82": font("georgia.ttf", 82),
    "serif_124": font("georgia.ttf", 124),
    "serif_italic_38": font("georgiai.ttf", 38),
    "serif_italic_44": font("georgiai.ttf", 44),
    "serif_italic_112": font("georgiai.ttf", 112),
}


def text_width(draw: ImageDraw.ImageDraw, text: str, text_font) -> float:
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0]


def wrap(draw: ImageDraw.ImageDraw, text: str, text_font, max_width: int) -> list[str]:
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if text_width(draw, candidate, text_font) <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    xy: tuple[int, int],
    text_font,
    max_width: int,
    fill: str,
    line_height: int,
    spacing_after: int = 0,
) -> int:
    x, y = xy
    for line in wrap(draw, text, text_font, max_width):
        draw.text((x, y), line, font=text_font, fill=fill)
        y += line_height
    return y + spacing_after


def cover(path: Path, size: tuple[int, int], position=(0.5, 0.5)) -> Image.Image:
    image = Image.open(path).convert("RGB")
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=position)


def letterspaced(draw, xy, text, text_font, fill, spacing=5):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=text_font, fill=fill)
        x += text_width(draw, char, text_font) + spacing


def wood_gradient(width: int, height: int) -> Image.Image:
    image = Image.new("RGB", (width, height), CHOCOLATE)
    gradient_draw = ImageDraw.Draw(image)
    start = (27, 16, 8)
    middle = (48, 29, 13)
    end = (109, 84, 59)
    for x in range(width):
        t = x / max(1, width - 1)
        if t <= 0.52:
            local = t / 0.52
            color = tuple(round(a + (b - a) * local) for a, b in zip(start, middle))
        else:
            local = (t - 0.52) / 0.48
            color = tuple(round(a + (b - a) * local) for a, b in zip(middle, end))
        gradient_draw.line((x, 0, x, height), fill=color)
    return image


def build_tektura_collage() -> None:
    base = Image.open(ASSETS / "tektura-collage-base.jpg").convert("RGB")
    top_right_source = Image.open(ASSETS / "tektura-collage-top-right.png").convert("RGB")
    bottom_right_source = Image.open(ASSETS / "tektura-collage-new.png").convert("RGB")

    top_right = ImageOps.fit(
        top_right_source,
        (800, 450),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )

    # Remove the small mark in the source image's lower-left corner before fitting.
    source_w, source_h = bottom_right_source.size
    bottom_right_source = bottom_right_source.crop(
        (round(source_w * 0.043), 0, source_w, round(source_h * 0.945))
    )
    bottom_right = ImageOps.fit(
        bottom_right_source,
        (800, 450),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )

    # Replace both right-hand images while preserving the central logo tile.
    logo_tile = base.crop((766, 414, 840, 488))
    base.paste(top_right, (800, 0))
    base.paste(bottom_right, (800, 450))
    base.paste(logo_tile, (766, 414))
    base.save(ASSETS / "tektura-collage.jpg", quality=94, optimize=True)


def build_tektura_footer_collage() -> None:
    gap = 10
    collage_w = W
    collage_h = 540
    canvas = Image.new("RGB", (collage_w, collage_h), CHOCOLATE)

    paths = [
        "tektura-footer-bar.jpg",
        "tektura-footer-table.jpg",
        "tektura-footer-patio.jpg",
    ]
    images = [Image.open(ASSETS / path).convert("RGB") for path in paths]
    available_w = collage_w - gap * (len(images) - 1)
    aspects = [image.width / image.height for image in images]
    widths = [round(available_w * aspect / sum(aspects)) for aspect in aspects]
    widths[-1] += available_w - sum(widths)

    x = 0
    for image, width in zip(images, widths):
        resized = image.resize((width, collage_h), Image.Resampling.LANCZOS)
        canvas.paste(resized, (x, 0))
        x += width + gap

    canvas.save(ASSETS / "tektura-footer-collage.jpg", quality=94, optimize=True)


def render() -> Image.Image:
    canvas = Image.new("RGB", (W, 11000), PAPER)
    draw = ImageDraw.Draw(canvas)
    y = 0

    # Top bar
    canvas.paste(wood_gradient(W, 144), (0, y))
    letterspaced(draw, (84, y + 52), "CFI HOTELS GROUP", F["sans_bold_24"], WHITE, 5)
    badge_x, badge_y, badge_w, badge_h = 840, y + 42, 165, 56
    draw.rounded_rectangle(
        (badge_x, badge_y, badge_x + badge_w, badge_y + badge_h),
        radius=28,
        fill=COPPER_LIGHT,
    )
    badge_text = "NOWOŚĆ"
    badge_text_w = sum(text_width(draw, c, F["sans_bold_20"]) + 3 for c in badge_text)
    letterspaced(
        draw,
        (badge_x + (badge_w - badge_text_w) / 2, badge_y + 16),
        badge_text,
        F["sans_bold_20"],
        INK,
        3,
    )
    letterspaced(draw, (1050, y + 55), "ŁÓDŹ / MICE", F["sans_bold_20"], COPPER_LIGHT, 7)
    y += 144

    # Hero
    hero_h = 1160
    left = cover(ASSETS / "tektura-hero-window.jpg", (W // 2, hero_h), (0.50, 0.50))
    right = cover(ASSETS / "99hz-hero-banquet-crop.jpg", (W // 2, hero_h), (0.50, 0.52))
    canvas.paste(left, (0, y))
    canvas.paste(right, (W // 2, y))
    overlay = Image.new("RGBA", (W, hero_h), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for row in range(hero_h):
        t = row / hero_h
        alpha = int(20 + 225 * max(0, (t - 0.38) / 0.62) ** 1.45)
        overlay_draw.line((0, row, W, row), fill=(17, 15, 12, alpha))
    canvas.paste(overlay, (0, y), overlay)
    draw = ImageDraw.Draw(canvas)
    draw.line((W // 2, y, W // 2, y + hero_h), fill="#b8aea2", width=2)
    title_y = y + 840
    draw.text((70, title_y), "Od Scheiblera", font=F["serif_82"], fill=WHITE)
    draw.text((770, title_y), "do", font=F["serif_82"], fill=WHITE)
    draw.text((866, title_y + 2), "POLMO", font=F["serif_italic_112"], fill=COPPER_LIGHT)
    hero_eyebrow = "DWIE NOWE PRZESTRZENIE EVENTOWE W ŁODZI"
    hero_spacing = 6
    hero_font = F["sans_bold_28"]
    hero_text_w = sum(text_width(draw, c, hero_font) + hero_spacing for c in hero_eyebrow)
    hero_box = (76, y + 1014, 76 + hero_text_w + 64, y + 1090)
    hero_label_bg = Image.new("RGBA", (W, hero_h), (0, 0, 0, 0))
    hero_label_draw = ImageDraw.Draw(hero_label_bg)
    hero_label_draw.rounded_rectangle(
        (hero_box[0], hero_box[1] - y, hero_box[2], hero_box[3] - y),
        radius=5,
        fill=(31, 18, 9, 215),
        outline=(212, 164, 127, 122),
        width=2,
    )
    canvas.paste(hero_label_bg, (0, y), hero_label_bg)
    draw = ImageDraw.Draw(canvas)
    letterspaced(draw, (108, y + 1038), hero_eyebrow, hero_font, COPPER_LIGHT, hero_spacing)
    y += hero_h

    # Intro
    intro_top = y
    intro_h = 610
    draw.rectangle((0, intro_top, W, intro_top + intro_h), fill=PAPER)
    draw.text((96, y + 100), "Łódź.", font=F["serif_52"], fill=COPPER)
    draw.text((96, y + 160), "Miasto, które", font=F["serif_44"], fill=COPPER)
    draw.text((96, y + 214), "od zawsze", font=F["serif_44"], fill=COPPER)
    draw.text((96, y + 268), "tworzyło historię.", font=F["serif_44"], fill=COPPER)
    intro_1 = "W sercu miasta, które przez dziesięciolecia wyznaczało kierunki rozwoju polskiego przemysłu, CFI Hotels Group tworzy dziś miejsca spotkań łączące historię, architekturę i nowoczesną gościnność."
    intro_2 = "Do portfolio grupy dołączyły dwie nowe przestrzenie eventowe, których charakter wyrasta bezpośrednio z dziedzictwa Łodzi."
    ty = draw_wrapped(draw, intro_1, (520, y + 104), F["sans_28"], 810, INK, 46, 28)
    draw_wrapped(draw, intro_2, (520, ty), F["sans_28"], 810, INK, 46)
    y += intro_h

    # Timeline
    y -= 48
    timeline_h = 650
    canvas.paste(wood_gradient(W, timeline_h), (0, y))
    half = W // 2
    draw.line((half, y + 40, half, y + timeline_h - 40), fill="#987657", width=2)
    draw.text((52, y + 134), "1855", font=F["serif_62"], fill="#d5ad82")
    timeline_1855 = "W 1855 roku „król bawełny” Karol Scheibler przy Wodnym Rynku w Łodzi (dzisiejszy plac Zwycięstwa 2) uruchomił własną fabrykę — przędzalnię, która stanowiła początek włókienniczego imperium."
    draw_wrapped(draw, timeline_1855, (218, y + 48), F["serif_28"], 445, "#d5ad82", 38)
    left_content_center = (218 + half) / 2
    draw.text((52, y + 394), "2026", font=F["serif_52"], fill="#d5ad82")
    timeline_tektura = Image.open(ASSETS / "tektura-logo-white.png").convert("RGBA")
    timeline_tektura_w = 190
    timeline_tektura_h = round(timeline_tektura.height * timeline_tektura_w / timeline_tektura.width)
    timeline_tektura = timeline_tektura.resize((timeline_tektura_w, timeline_tektura_h), Image.Resampling.LANCZOS)
    timeline_tektura_x = round(left_content_center - timeline_tektura_w / 2)
    canvas.paste(timeline_tektura, (timeline_tektura_x, y + 438), timeline_tektura)
    draw.text((half + 52, y + 134), "1908", font=F["serif_62"], fill="#d5ad82")
    draw.text((half + 52, y + 394), "2026", font=F["serif_52"], fill="#d5ad82")
    timeline_1908 = "Historia łódzkiej Fabryki Osprzętu Samochodowego (FOS) „Polmo” przy ul. Przybyszewskiego 99 sięga 1908 roku. Zakład rozpoczął od produkcji odlewniczej, w 1929 roku wszedł w branżę motoryzacyjną, od 1945 roku działał jako samodzielne przedsiębiorstwo."
    draw_wrapped(draw, timeline_1908, (half + 218, y + 48), F["serif_28"], 445, "#d5ad82", 38)
    timeline_99 = Image.open(ASSETS / "99hz-logo-white.png").convert("RGBA")
    timeline_99_w = 195
    timeline_99_h = round(timeline_99.height * timeline_99_w / timeline_99.width)
    timeline_99 = timeline_99.resize((timeline_99_w, timeline_99_h), Image.Resampling.LANCZOS)
    right_content_center = (half + 218 + W) / 2
    timeline_99_x = round(right_content_center - timeline_99_w / 2)
    canvas.paste(timeline_99, (timeline_99_x, y + 438), timeline_99)
    y += timeline_h

    # 99Hz
    section_top = y
    draw.rectangle((0, section_top, W, section_top + 3450), fill=PAPER)
    letterspaced(draw, (96, y + 105), "01 / POLMO / PRZYBYSZEWSKIEGO 99", F["sans_bold_20"], COPPER, 5)
    draw.text((96, y + 160), "99Hz", font=F["serif_82"], fill=INK)
    draw_wrapped(draw, "Nowoczesny event w miejscu z motoryzacyjną historią", (96, y + 262), F["serif_italic_38"], 930, COPPER, 52)
    draw.ellipse((1180, y + 105, 1340, y + 265), outline=COPPER, width=2)
    draw.text((1215, y + 150), "01", font=F["serif_52"], fill=COPPER)
    y += 405
    image_h = 720
    image = cover(ASSETS / "99hz-conference.jpg", (W, image_h), (0.5, 0.45))
    canvas.paste(image, (0, y))
    y += image_h + 80
    col_w = 570
    x1, x2 = 96, 774
    lead = "99Hz to elegancka przestrzeń konferencyjno-eventowa zlokalizowana w budynku Citi Hotel's Łódź, przy ul. Przybyszewskiego 99."
    p1 = "Miejsce powstało na terenie dawnych zakładów motoryzacyjnych POLMO, będących przez lata ważnym elementem przemysłowej historii miasta."
    p2 = "Inspirację tym dziedzictwem odnaleźć można we wnętrzu obiektu, gdzie charakterystyczne metalowe elementy dekoracyjne nawiązują do motoryzacyjnej przeszłości tej lokalizacji."
    p3 = "Nowoczesna architektura, profesjonalne wyposażenie multimedialne oraz bezpośredni dostęp do 114 pokoi Citi Hotel's Łódź tworzą kompleksowe rozwiązanie dla organizatorów konferencji, szkoleń, gal, bankietów\ni wydarzeń firmowych."
    p4 = "To przestrzeń stworzona dla tych, którzy oczekują czegoś więcej niż standardowej sali konferencyjnej."
    left_y = draw_wrapped(draw, lead, (x1, y), F["serif_38"], col_w, INK, 55, 30)
    left_end = draw_wrapped(draw, p1, (x1, left_y), F["sans_24"], col_w, INK, 39)
    right_y = draw_wrapped(draw, p2, (x2, y), F["sans_24"], col_w, INK, 39, 30)
    right_y = draw_wrapped(draw, p3, (x2, right_y), F["sans_24"], col_w, INK, 39, 30)
    right_end = draw_wrapped(draw, p4, (x2, right_y), F["sans_24"], col_w, INK, 39)
    y = max(left_end, right_end) + 90

    # 99Hz key capacity information
    draw.line((96, y, W - 96, y), fill="#a99e90", width=2)
    hz_capacities = [
        ("145 m²", "POWIERZCHNIA SALI"),
        ("DO 120", "OSÓB PRZY STOŁACH PROSTOKĄTNYCH"),
        ("DO 80", "OSÓB PRZY STOŁACH OKRĄGŁYCH"),
        ("DO 150", "OSÓB W FORMULE KOKTAJLOWEJ (STANDING PARTY)"),
    ]
    capacity_w = (W - 192) // 4
    for idx, (value, caption) in enumerate(hz_capacities):
        cx = 96 + idx * capacity_w
        if idx:
            draw.line((cx, y + 30, cx, y + 230), fill="#b9afa1", width=2)
        value_w = text_width(draw, value, F["serif_44"])
        draw.text((cx + (capacity_w - value_w) / 2, y + 42), value, font=F["serif_44"], fill=COPPER)
        caption_lines = wrap(draw, caption, F["sans_bold_20"], capacity_w - 52)
        cy = y + 112
        for line in caption_lines:
            line_w = text_width(draw, line, F["sans_bold_20"])
            draw.text((cx + (capacity_w - line_w) / 2, cy), line, font=F["sans_bold_20"], fill=INK)
            cy += 29
    draw.line((96, y + 260, W - 96, y + 260), fill="#a99e90", width=2)
    y += 330

    # Historical POLMO card
    history_h = 670
    history_x = 76
    history_w = W - 152
    image_w = 500
    canvas.paste(wood_gradient(history_w, history_h), (history_x, y))
    archive = cover(ASSETS / "polmo-archive-hall.jpg", (image_w, history_h), (0.5, 0.5))
    canvas.paste(archive, (history_x, y))
    hx = history_x + image_w + 42
    letterspaced(draw, (hx, y + 42), "RYS HISTORYCZNY / POLMO", F["sans_bold_20"], COPPER_LIGHT, 4)
    draw.text((hx, y + 91), "Od odlewni do", font=F["serif_38"], fill=WHITE)
    draw.text((hx, y + 138), "motoryzacyjnej specjalizacji", font=F["serif_38"], fill=WHITE)
    history_intro = "FOS „POLMO” powstało na bazie ośmiu łódzkich zakładów, łącząc odlewnictwo, konstrukcję silników i produkcję osprzętu dla polskiej motoryzacji."
    draw_wrapped(draw, history_intro, (hx, y + 202), F["sans_20"], 645, MUTED_WHITE, 31)
    history_items = [
        ("1908", "Odlewnia Żelaza „Ferrum” — od tej daty zakład liczył swoją historię."),
        ("1929", "Roman Klinger zakłada Fabrykę Akcesoriów Samochodowych."),
        ("1952", "Start produkcji gaźników — jednej z głównych specjalizacji zakładu."),
        ("1968", "Przyjęcie nazwy Fabryka Osprzętu Samochodowego „POLMO”."),
    ]
    for idx, (date, label) in enumerate(history_items):
        col = idx % 2
        row = idx // 2
        ix = hx + col * 335
        iy = y + 335 + row * 145
        draw.line((ix, iy, ix + 294, iy), fill="#69635c", width=2)
        draw.text((ix, iy + 15), date, font=F["serif_38"], fill=COPPER_LIGHT)
        draw_wrapped(draw, label, (ix, iy + 64), F["sans_20"], 294, MUTED_WHITE, 28)
    letterspaced(draw, (hx, y + 632), "ARCHIWALNA HALA MONTAŻU · INFORMATOR FOS „POLMO”, 1978", F["sans_bold_13"], "#77716a", 1)
    y += history_h + 90

    draw.line((96, y, W - 96, y), fill="#a99e90", width=2)
    facts = [("114", "POKOI W CITI HOTEL'S ŁÓDŹ"), ("MICE", "KONFERENCJE, SZKOLENIA I GALE"), ("AV", "PROFESJONALNE MULTIMEDIA\nKLIMATYZACJA")]
    fact_w = (W - 192) // 3
    for i, (big, small) in enumerate(facts):
        fx = 96 + i * fact_w
        if i:
            draw.line((fx, y + 32, fx, y + 240), fill="#b9afa1", width=2)
        big_x = fx + (20 if i else 0)
        draw.text((big_x, y + 48), big, font=F["serif_52"], fill=COPPER)
        if big == "AV":
            icon_x = big_x + text_width(draw, big, F["serif_52"]) + 34
            icon_y = y + 76
            icon_r = 22
            draw.line((icon_x - icon_r, icon_y, icon_x + icon_r, icon_y), fill=COPPER, width=4)
            draw.line((icon_x - 11, icon_y - 19, icon_x + 11, icon_y + 19), fill=COPPER, width=4)
            draw.line((icon_x - 11, icon_y + 19, icon_x + 11, icon_y - 19), fill=COPPER, width=4)
        draw_wrapped(draw, small, (fx + (20 if i else 0), y + 120), F["sans_bold_20"], fact_w - 45, INK, 30)
    draw.line((96, y + 270, W - 96, y + 270), fill="#a99e90", width=2)
    y += 350

    # Tektura
    tektura_top = y
    canvas.paste(wood_gradient(W, 3490), (0, tektura_top))
    letterspaced(draw, (96, y + 105), "02 / CENTRALA SCHEIBLERA / PLAC ZWYCIĘSTWA 2", F["sans_bold_20"], COPPER_LIGHT, 5)
    draw.text((96, y + 160), "Tektura", font=F["serif_82"], fill=WHITE)
    draw.text((390, y + 255), "by Farina Bianco", font=F["serif_italic_38"], fill=COPPER_LIGHT)
    draw_wrapped(draw, "Industrialna elegancja w historycznej Centrali Scheiblera", (96, y + 334), F["serif_italic_38"], 930, COPPER_LIGHT, 52)
    draw.ellipse((1180, y + 105, 1340, y + 265), outline=COPPER_LIGHT, width=2)
    draw.text((1215, y + 150), "02", font=F["serif_52"], fill=COPPER_LIGHT)
    y += 485
    image_h = 810
    image = cover(ASSETS / "tektura-collage.jpg", (W, image_h), (0.5, 0.50))
    canvas.paste(image, (0, y))
    y += image_h + 84
    lead2 = "Przy Placu Zwycięstwa 2 znajduje się jedno z najbardziej wyjątkowych miejsc na mapie Łodzi."
    t1 = "Tektura by Farina Bianco mieści się w zabytkowym kompleksie dawnej fabryki Karola Scheiblera, znanym jako „Centrala”."
    t2 = "Powstały w latach 1855-1870 obiekt należy do najważniejszych zabytków przemysłowych miasta\ni jest symbolem łódzkiej przedsiębiorczości oraz przemysłowego rozwoju."
    t3 = "Dziś odrestaurowane wnętrza zachwycają autentyczną cegłą, monumentalnymi przeszkleniami\ni niepowtarzalnym klimatem, tworząc idealne tło dla gal, premier produktów, konferencji, bankietów\ni wydarzeń prywatnych."
    left_y = draw_wrapped(draw, lead2, (x1, y), F["serif_38"], col_w, WHITE, 55, 32)
    left_end = draw_wrapped(draw, t1, (x1, left_y), F["sans_24"], col_w, MUTED_WHITE, 39)
    right_y = draw_wrapped(draw, t2, (x2, y), F["sans_24"], col_w, MUTED_WHITE, 39, 32)
    right_end = draw_wrapped(draw, t3, (x2, right_y), F["sans_24"], col_w, MUTED_WHITE, 39)
    y = max(left_end, right_end) + 95

    # Tektura key information and amenities
    key_h = 400
    key_x = 76
    key_w = W - 152
    key_panel = Image.new("RGB", (key_w, key_h), PAPER)
    canvas.paste(key_panel, (key_x, y))
    key_label = "KLUCZOWE INFORMACJE I ATUTY"
    key_label_w = sum(text_width(draw, c, F["sans_bold_20"]) + 4 for c in key_label)
    letterspaced(draw, (key_x + (key_w - key_label_w) / 2, y + 30), key_label, F["sans_bold_20"], COPPER, 4)
    key_values = [
        ("600 m²", "POWIERZCHNIA PRZESTRZENI"),
        ("OD 40", "OSÓB · IMPREZY ZAMKNIĘTE"),
        ("DO 180", "OSÓB PRZY STOŁACH OKRĄGŁYCH LUB PODŁUŻNYCH"),
        ("DO 300", "OSÓB W FORMULE KOKTAJLOWEJ (STANDING PARTY)"),
    ]
    key_col_w = key_w // 4
    key_values_y = y + 78
    draw.line((key_x + 38, key_values_y, key_x + key_w - 38, key_values_y), fill="#a99e90", width=2)
    for idx, (value, caption) in enumerate(key_values):
        kx = key_x + idx * key_col_w
        if idx:
            draw.line((kx, key_values_y + 22, kx, key_values_y + 170), fill="#c4b6a3", width=2)
        value_w = text_width(draw, value, F["serif_44"])
        draw.text((kx + (key_col_w - value_w) / 2, key_values_y + 28), value, font=F["serif_44"], fill=COPPER)
        lines = wrap(draw, caption, F["sans_bold_20"], key_col_w - 48)
        ky = key_values_y + 100
        for line in lines:
            line_w = text_width(draw, line, F["sans_bold_20"])
            draw.text((kx + (key_col_w - line_w) / 2, ky), line, font=F["sans_bold_20"], fill=INK)
            ky += 29
    amenities_y = y + 258
    draw.line((key_x + 38, amenities_y, key_x + key_w - 38, amenities_y), fill="#a99e90", width=2)
    key_amenities = ["Sąsiedztwo parku", "Dyskretne wejście VIP", "Wewnętrzne patio", "Przestrzeń na parkiet"]
    for idx, item in enumerate(key_amenities):
        item_w = text_width(draw, item, F["sans_20"])
        group_w = 12 + 14 + item_w
        ax = key_x + idx * key_col_w + (key_col_w - group_w) / 2
        draw.ellipse((ax, amenities_y + 55, ax + 10, amenities_y + 65), fill=COPPER)
        draw.text((ax + 24, amenities_y + 43), item, font=F["sans_20"], fill=INK)
    y += key_h + 90

    # Historical Scheibler card
    scheibler_h = 720
    history_x = 76
    history_w = W - 152
    image_w = 500
    panel = Image.new("RGB", (history_w, scheibler_h), "#ead7bd")
    panel_draw = ImageDraw.Draw(panel)
    panel_start = (234, 215, 189)
    panel_end = (244, 234, 220)
    for px in range(history_w):
        t = px / max(1, history_w - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(panel_start, panel_end))
        panel_draw.line((px, 0, px, scheibler_h), fill=color)
    canvas.paste(panel, (history_x, y))
    archive = cover(ASSETS / "scheibler-archive.jpg", (image_w, scheibler_h), (0.5, 0.52))
    archive_sepia = ImageOps.colorize(ImageOps.grayscale(archive), black="#2d2119", white="#d9ba91")
    archive = Image.blend(archive, archive_sepia, 0.72)
    canvas.paste(archive, (history_x, y))
    draw.rectangle((history_x + image_w - 3, y, history_x + image_w + 5, y + scheibler_h), fill=COPPER)
    hx = history_x + image_w + 42
    letterspaced(draw, (hx, y + 38), "RYS HISTORYCZNY / CENTRALA SCHEIBLERA", F["sans_bold_20"], COPPER, 3)
    draw.text((hx, y + 88), "Miejsce, od którego zaczęło się", font=F["serif_38"], fill=INK)
    draw.text((hx, y + 135), "przemysłowe imperium", font=F["serif_38"], fill=INK)
    scheibler_intro = "Centrala Scheiblera przy Placu Zwycięstwa 2 to najstarszy kompleks dawnej fabryki bawełny Karola Scheiblera. Dała początek jednemu z największych imperiów przemysłowych XIX-wiecznej Europy i pozostaje kluczowym zabytkiem Łodzi."
    draw_wrapped(draw, scheibler_intro, (hx, y + 198), F["sans_20"], 645, "#514b44", 30)
    scheibler_items = [
        ("1855", "Karol Scheibler rozpoczyna działalność przemysłową w Łodzi."),
        ("1858", "Powstaje najstarsza część kompleksu „Centrala”."),
        ("XIX w.", "Początek jednego z największych imperiów przemysłowych Europy."),
        ("DZIŚ", "Tektura by Farina Bianco · Plac Zwycięstwa 2."),
    ]
    for idx, (date, label) in enumerate(scheibler_items):
        col = idx % 2
        row = idx // 2
        ix = hx + col * 335
        iy = y + 360 + row * 162
        draw.rounded_rectangle((ix, iy, ix + 294, iy + 148), radius=8, fill="#f4eadc", outline="#d7b996", width=2)
        draw.rectangle((ix, iy, ix + 7, iy + 148), fill=COPPER)
        draw.text((ix + 20, iy + 12), date, font=F["serif_38"], fill=COPPER)
        draw_wrapped(draw, label, (ix + 20, iy + 58), F["sans_20"], 254, "#514b44", 28)
    letterspaced(draw, (hx, y + 690), "BRAMA ZAKŁADÓW · 1936-1938 · AP ŁÓDŹ / FOTOPOLSKA.EU", F["sans_bold_20"], "#8b7f70", 1)
    y += scheibler_h + 90

    footer_collage = Image.open(ASSETS / "tektura-footer-collage.jpg").convert("RGB")
    canvas.paste(footer_collage, (0, y))
    y += footer_collage.height + 90

    # Footer
    footer_h = 270
    canvas.paste(wood_gradient(W, footer_h), (0, y))
    letterspaced(draw, (96, y + 78), "CFI HOTELS GROUP", F["sans_bold_28"], WHITE, 6)
    draw.text((96, y + 132), "Historia nie stanowi dekoracji.", font=F["serif_italic_38"], fill=COPPER_LIGHT)
    draw.text((96, y + 180), "Jest częścią każdego wydarzenia.", font=F["serif_italic_38"], fill=COPPER_LIGHT)
    letterspaced(draw, (1030, y + 85), "ŁÓDŹ", F["sans_bold_20"], MUTED_WHITE, 6)
    letterspaced(draw, (914, y + 132), "NOWE PRZESTRZENIE", F["sans_bold_20"], MUTED_WHITE, 4)
    letterspaced(draw, (1032, y + 175), "EVENTOWE", F["sans_bold_20"], MUTED_WHITE, 4)
    y += footer_h

    return canvas.crop((0, 0, W, y))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_tektura_collage()
    build_tektura_footer_collage()
    preview = render()
    preview.save(OUT / "project-preview.png", optimize=True)

    mobile_width = 390
    mobile = preview.resize(
        (mobile_width, round(preview.height * mobile_width / preview.width)),
        Image.Resampling.LANCZOS,
    )
    mobile.save(OUT / "mobile-preview.png", optimize=True)

    pdf = fitz.open()
    page_width = 720
    page_height = page_width * preview.height / preview.width
    page = pdf.new_page(width=page_width, height=page_height)
    page.insert_image(page.rect, filename=str(OUT / "project-preview.png"))
    try:
        pdf.save(OUT / "project-preview.pdf", deflate=True)
    except Exception:
        pdf.save(OUT / "project-preview-updated.pdf", deflate=True)


if __name__ == "__main__":
    main()
