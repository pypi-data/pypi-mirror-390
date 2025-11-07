from fontTools.ttLib import TTFont
from .element import Text, Space
from .utils import Point


def build_title(
    text: str,
    x_end: float,
    font: TTFont,
) -> Text:
    space = Space(
        top_left=Point(x=0, y=0),
        bottom_right=Point(x=x_end, y=0),
    )

    title = Text(
        text=text,
        font_size=26,
        pos=Point(x=0.5, y=1),
        space=space,
        x_align="center",
        y_align="top",
        font=font,
    )

    return title
