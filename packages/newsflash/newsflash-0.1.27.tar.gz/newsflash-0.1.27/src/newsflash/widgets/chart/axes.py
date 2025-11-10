from math import floor, ceil
from .utils import Point, Space, order_of_magnitude
from fontTools.ttLib import TTFont
from .element import ElementCollection, Text, Line


def build_x_axis(
    x_start: float,
    x_end: float,
    y_end: float,
    start_x_value: float,
    end_x_value: float,
    ticks: list[float] | list[int],
    font_size: int,
    font: TTFont,
    labels: list[str] | None = None,
    description: str | None = None,
) -> ElementCollection:
    x_axis_height = font_size * 3

    x_axis_space = Space(
        top_left=Point(x=x_start, y=y_end - x_axis_height),
        bottom_right=Point(x=x_end, y=y_end),
    )

    if labels is None:
        labels = [str(tick) for tick in ticks]

    elements = ElementCollection()
    ticks = [(tick - start_x_value) / (end_x_value - start_x_value) for tick in ticks]

    for idx, tick in enumerate(ticks):
        elements.append(
            Text(
                text=labels[idx],
                font_size=font_size,
                pos=Point(x=tick, y=1),
                x_align="center",
                y_align="top",
                font=font,
                space=x_axis_space,
            )
        )

    if description is not None:
        elements.append(
            Text(
                text=description,
                font_size=font_size,
                pos=Point(x=0.5, y=0),
                x_align="center",
                y_align="bottom",
                font=font,
                space=x_axis_space,
            )
        )

    return elements


def build_y_axis(
    y_start: float,
    y_end: float,
    x_start: float,
    bottom_y_value: float,
    top_y_value: float,
    ticks: list[float],
    font: TTFont,
    labels: list[str] | None = None,
) -> ElementCollection:
    y_axis_space = Space(
        top_left=Point(x=x_start, y=y_start),
        bottom_right=Point(x=x_start, y=y_end),
    )

    if labels is None:
        labels = [str(tick) for tick in ticks]

    elements = ElementCollection()

    ticks = [(tick - bottom_y_value) / (top_y_value - bottom_y_value) for tick in ticks]

    for idx, tick in enumerate(ticks):
        if tick >= 0 and tick <= 1:
            elements.append(
                Text(
                    text=labels[idx],
                    font_size=16,
                    font=font,
                    pos=Point(x=0, y=tick),
                    space=y_axis_space,
                )
            )

    return elements


def build_y_ticks(
    number_of_ticks: int,
    min_y_value: float,
    max_y_value: float,
) -> tuple[list[float], list[str], int]:
    y_step = (max_y_value - min_y_value) / (number_of_ticks - 1)
    y_step_order_of_magnitude = order_of_magnitude(y_step)

    scale_factor = pow(10, y_step_order_of_magnitude)
    
    rounded_y_step = round(y_step / scale_factor) * scale_factor

    min_y_tick = floor(min_y_value / rounded_y_step)
    max_y_tick = ceil(max_y_value / rounded_y_step)
    
    y_steps = [
        rounded_y_step * i for i in range(min_y_tick, max_y_tick+1)
    ]

    multiplier = pow(1000, floor(y_step_order_of_magnitude / 3))
    # TODO: temporary solution:
    if multiplier < 1:
        multiplier = 1

    y_steps = [y_step / multiplier for y_step in y_steps]

    if y_step_order_of_magnitude < 0:
        labels = [f"{y:.{abs(y_step_order_of_magnitude)}f}" for y in y_steps]
    else:
        labels = [str(round(y)) for y in y_steps]

    return y_steps, labels, multiplier


def build_y_grid_lines(
    bottom_y_value: float,
    top_y_value: float,
    ticks: list[float],
    space: Space,
) -> ElementCollection:
    elements = ElementCollection()

    ticks = [(tick - bottom_y_value) / (top_y_value - bottom_y_value) for tick in ticks]

    for tick in ticks:
        if tick >= 0 and tick <= 1:
            elements.append(
                Line(
                    from_pos=Point(x=0, y=tick),
                    to_pos=Point(x=1, y=tick),
                    space=space,
                    stroke_width=2,
                    classes=["stroke-grid-lines-light", "dark:stroke-grid-lines-dark"],
                )
            )

    return elements
