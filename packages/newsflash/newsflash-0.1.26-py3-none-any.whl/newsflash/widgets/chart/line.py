from math import floor
from django.http import HttpRequest
from django.contrib.humanize.templatetags.humanize import intcomma
from .base import Chart
from pydantic import BaseModel
from .utils import Point, Space
from fontTools.ttLib import TTFont
from pathlib import Path

from newsflash.fonts import get_text_height
from .element import Text, ElementCollection
from .element import Path as PathElement
from .axes import build_x_axis, build_y_axis, build_y_grid_lines, build_y_ticks
from .title import build_title


def build_lines(
    xs: list[float] | list[int],
    ys: list[float] | list[int],
    multiplier: float,
    min_y: float,
    max_y: float,
    space: Space,
) -> ElementCollection:
    elements = ElementCollection()

    ys = [y / multiplier for y in ys]
    normalized_ys = [(y - min_y) / (max_y - min_y) for y in ys]
    min_x, max_x = xs[0], xs[-1]
    normalized_xs = [(x - min_x) / (max_x - min_x) for x in xs]

    points: list[Point] = []
    for idx, x in enumerate(normalized_xs):
        points.append(Point(x=x, y=normalized_ys[idx]))

    elements.append(
        PathElement(
            points=points,
            space=space,
            classes=["stroke-line-light", "dark:stroke-line-dark", "line-path"],
            stroke_width=3.0,
        )
    )

    return elements


class LineChartContext(BaseModel):
    id: str
    width: float
    height: float
    elements: list[str]
    swap_oob: bool = False


class LineChart(Chart):
    xs: list[float] | list[int] = []
    ys: list[float] | list[int] = []

    x_ticks: list[float] | list[int] | None = None
    x_ticks_labels: list[str] | None = None

    def set_points(self, xs: list[float] | list[int], ys: list[float] | list[int]) -> None:
        self.xs = xs
        self.ys = ys

    def set_labels(self, x_ticks: list[float] | list[int], x_ticks_labels: list[str]) -> None:
        self.x_ticks = x_ticks
        self.x_ticks_labels = x_ticks_labels

    def _build_chart(self, request: HttpRequest, id: str) -> LineChartContext:
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
            min_y_value=min(self.ys),
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
            bottom_y_value=min(y_ticks),
            top_y_value=max(y_ticks),
            ticks=y_ticks,
            labels=y_labels,
            font=font,
        )

        chart_start_x = y_label_width * 2 + y_axis.get_width() + x_axis_font_size
        chart_end_x = self.width_in_px - y_label_width * 2

        if self.x_ticks is None:
            ticks_step = floor(len(self.xs) / 8)
            x_ticks = list(range(int(self.xs[0]), int(self.xs[-1]) + 1, ticks_step))
        else:
            x_ticks = self.x_ticks

        x_axis = build_x_axis(
            x_start=chart_start_x,
            x_end=chart_end_x,
            y_end=self.height_in_px,
            start_x_value=self.xs[0],
            end_x_value=self.xs[-1],
            ticks=x_ticks,
            labels=self.x_ticks_labels,
            font_size=x_axis_font_size,
            font=font,
            description=self.x_axis_label,
        )

        y_grid_lines = build_y_grid_lines(
            bottom_y_value=min(y_ticks),
            top_y_value=max(y_ticks),
            ticks=y_ticks,
            space=Space(
                top_left=Point(x=chart_start_x, y=title_height * 3),
                bottom_right=Point(x=chart_end_x, y=self.height_in_px - x_axis_height),
            ),
        )

        bars = build_lines(
            xs=self.xs,
            ys=self.ys,
            multiplier=multiplier,
            min_y=min(y_ticks),
            max_y=max(y_ticks),
            space=Space(
                top_left=Point(x=chart_start_x, y=title_height * 3),
                bottom_right=Point(x=chart_end_x, y=self.height_in_px - x_axis_height),
            ),
        )

        elements.extend(y_axis)
        elements.extend(x_axis)
        elements.extend(y_grid_lines)
        elements.extend(bars)

        assert self.id is not None
        return LineChartContext(
            id=self.id,
            width=self.width_in_px,
            height=self.height_in_px,
            elements=elements.render(),
            swap_oob=self.swap_oob,
        )
