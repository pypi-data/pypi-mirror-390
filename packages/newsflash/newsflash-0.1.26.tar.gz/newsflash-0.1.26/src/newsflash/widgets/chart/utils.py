from math import ceil, floor, log10
from pydantic import BaseModel


class Padding(BaseModel):
    ps: float
    pt: float
    pe: float
    pb: float


class Point(BaseModel):
    x: float
    y: float


class Space(BaseModel):
    top_left: Point
    bottom_right: Point


def chart_space_to_xy(
    max_width: float,
    max_height: float,
    padding: Padding,
    width_in_px: float,
    height_in_px: float,
    point: Point,
) -> Point:
    x_frac = point.x / max_width
    y_frac = 1 - (point.y / max_height)

    chart_width_px = width_in_px - padding.ps - padding.pe
    chart_height_px = height_in_px - padding.pt - padding.pb

    x_px = padding.ps + (x_frac * chart_width_px)
    y_px = padding.pt + (y_frac * chart_height_px)

    return Point(x=x_px, y=y_px)


def chart_to_svg_coordinates(
    space: Space,
    point: Point,
) -> Point:
    chart_width = space.bottom_right.x - space.top_left.x
    chart_height = space.bottom_right.y - space.top_left.y

    x = space.top_left.x + chart_width * point.x
    y = space.bottom_right.y - chart_height * point.y

    return Point(x=x, y=y)


def chart_to_svg_coordinates_many(
    space: Space,
    points: list[Point],
) -> list[Point]:
    return [chart_to_svg_coordinates(space, point) for point in points]


def calculate_ticks(x_end: float, x_start: float, n_ticks: int) -> tuple[float, float]:
    x_range = x_end - x_start
    return ceil(x_range / n_ticks), ceil(x_range / (n_ticks * 5))


def order_of_magnitude(x: float):
    if x == 0:
        return 0
    return floor(log10(abs(x)))
