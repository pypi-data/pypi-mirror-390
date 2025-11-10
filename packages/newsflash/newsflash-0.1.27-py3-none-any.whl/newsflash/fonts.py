from fontTools.ttLib import TTFont


def get_text_width(font: TTFont, text: str, font_size: int) -> int:
    units_per_em = font["head"].unitsPerEm  # type: ignore
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    glyphs = [cmap[ord(x)] for x in text]
    advance = [hmtx[glyph][0] for glyph in glyphs]  # type: ignore
    total_advance = sum(advance)

    pixels_per_unit = font_size / units_per_em
    return total_advance * pixels_per_unit


def get_text_height(font: TTFont, text: str, font_size: int) -> tuple[float, float]:
    units_per_em = font["head"].unitsPerEm  # type: ignore
    cmap = font.getBestCmap()
    glyf = font["glyf"]

    y_min = 0
    y_max = 0
    glyphs = [cmap[ord(x)] for x in text]

    for glyph in glyphs:
        try:
            if (new_y_min := glyf[glyph].yMin) < y_min:  # type: ignore
                y_min = new_y_min
            if (new_y_max := glyf[glyph].yMax) > y_max:  # type: ignore
                y_max = new_y_max
        except AttributeError:
            continue

    pixels_per_unit = font_size / units_per_em
    return y_min * pixels_per_unit, y_max * pixels_per_unit
