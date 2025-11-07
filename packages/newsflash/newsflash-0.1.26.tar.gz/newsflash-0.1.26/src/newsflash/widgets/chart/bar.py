from django.http import HttpRequest
from django.contrib.humanize.templatetags.humanize import intcomma
from .base import Chart
from pydantic import BaseModel
from .utils import Point, Space
from fontTools.ttLib import TTFont
from pathlib import Path

from newsflash.fonts import get_text_height
from .element import Text, rect_from_bottom_center, ElementCollection
from .axes import build_x_axis, build_y_axis, build_y_grid_lines, build_y_ticks
from .title import build_title


def build_bars(
    xs: list[float],
    ys: list[float],
    multiplier: float,
    max_y: float,
    space: Space,
) -> ElementCollection:
    elements = ElementCollection()

    ys = [y / multiplier for y in ys]
    normalized_ys = [y / max_y for y in ys]

    for idx, x in enumerate(xs):
        rect = rect_from_bottom_center(
            bottom_center=Point(x=x / (len(xs) - 1), y=0),
            width=(1 / (len(xs) - 1)) * 0.9,
            height=normalized_ys[idx],
            space=space,
            rounded=True,
        )
        elements.append(rect)

    return elements


class BarChartContext(BaseModel):
    id: str
    width: float
    height: float
    elements: list[str]
    swap_oob: bool = False


class BarChart(Chart):
    xs: list[float] = []
    x_labels: list[str] = []
    ys: list[float] = []

    def set_points(self, xs: list[str], ys: list[float]) -> None:
        self.x_labels = xs
        self.xs = list(range(len(xs)))
        self.ys = ys

    def _build_chart(self, request: HttpRequest, id: str) -> BarChartContext:
        font = TTFont(
            Path(__file__).resolve().parent.parent.parent
            / "fonts"
            / "noto-serif"
            / "NotoSerif.ttf"
        )

        elements = ElementCollection()

        if self.title is not None:
            title = build_title(
                text=self.title,
                x_end=self.width_in_px,
                font=font,
            )

            elements.append(title)
            title_height = title.get_height()
        else:
            title_height = 10

        x_axis_font_size = 16
        x_axis_height = x_axis_font_size * 4

        y_label_width = 0
        if self.y_axis_label:
            y_min, y_max = get_text_height(
                font=font,
                text=self.y_axis_label,
                font_size=x_axis_font_size,
            )
            y_label_width = y_max - y_min

        y_ticks, y_labels, multiplier = build_y_ticks(
            number_of_ticks=4,
            min_y_value=0,
            max_y_value=max(self.ys),
        )

        if multiplier != 1:
            multiplier_text = Text(
                text=f"x {intcomma(multiplier)}",
                pos=Point(x=y_label_width * 2, y=title_height),
                y_align="bottom",
                font_size=x_axis_font_size,
                font=font,
            )
            elements.append(multiplier_text)

        y_axis_label_space = Space(
            top_left=Point(x=y_label_width, y=title_height * 2),
            bottom_right=Point(x=y_label_width, y=self.height_in_px - x_axis_height),
        )

        if self.y_axis_label is not None:
            y_axis_label = Text(
                text=self.y_axis_label,
                pos=Point(x=0, y=0.5),
                x_align="center",
                y_align="bottom",
                font_size=x_axis_font_size,
                font=font,
                rotate=90,
                space=y_axis_label_space,
            )
            elements.append(y_axis_label)

        y_axis = build_y_axis(
            y_start=title_height * 3,
            y_end=self.height_in_px - x_axis_height,
            x_start=y_label_width * 2,
            bottom_y_value=0.0,
            top_y_value=max(y_ticks),
            ticks=y_ticks,
            labels=y_labels,
            font=font,
        )

        bar_width = ((self.width_in_px - y_axis.get_width()) / len(self.ys)) / 2
        chart_start_x = y_label_width * 2 + y_axis.get_width() + x_axis_font_size
        chart_end_x = self.width_in_px - y_label_width * 2

        x_axis = build_x_axis(
            x_start=chart_start_x + bar_width,
            x_end=chart_end_x - bar_width,
            y_end=self.height_in_px,
            start_x_value=0.0,
            end_x_value=self.xs[-1],
            ticks=self.xs,
            labels=self.x_labels,
            font_size=x_axis_font_size,
            font=font,
            description=self.x_axis_label,
        )

        y_grid_lines = build_y_grid_lines(
            bottom_y_value=0.0,
            top_y_value=max(y_ticks),
            ticks=y_ticks,
            space=Space(
                top_left=Point(x=chart_start_x, y=title_height * 3),
                bottom_right=Point(x=chart_end_x, y=self.height_in_px - x_axis_height),
            ),
        )

        bars = build_bars(
            xs=self.xs,
            ys=self.ys,
            multiplier=multiplier,
            max_y=max(y_ticks),
            space=Space(
                top_left=Point(x=chart_start_x + bar_width, y=title_height * 3),
                bottom_right=Point(
                    x=chart_end_x - bar_width, y=self.height_in_px - x_axis_height
                ),
            ),
        )

        elements.extend(y_axis)
        elements.extend(x_axis)
        elements.extend(y_grid_lines)
        elements.extend(bars)

        assert self.id is not None
        return BarChartContext(
            id=self.id,
            width=self.width_in_px,
            height=self.height_in_px,
            elements=elements.render(),
            swap_oob=self.swap_oob,
        )
