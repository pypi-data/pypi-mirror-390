from typing import Literal, Self
from copy import deepcopy
from pydantic import BaseModel, ConfigDict
from newsflash.fonts import get_text_width, get_text_height
from .utils import chart_to_svg_coordinates, Point, Space
from fontTools.ttLib import TTFont
from django.template.loader import render_to_string


class Element(BaseModel):
    template_name: str = ""
    space: Space | None = None
    classes: list[str] = []

    def prerender(self) -> None:
        pass

    def render(self) -> str:
        if self.space is not None:
            self.transform_to_space(self.space)
        self.prerender()
        return render_to_string(
            f"app/widgets/chart/elements/{self.template_name}.html",
            context=self.model_dump(),
        )

    def get_width(self) -> float: ...

    def transform_to_space(self, space: Space) -> Self: ...


class Rectangle(Element):
    template_name: str = "rect"
    top_left: Point
    bottom_right: Point
    shape: Point | None = None
    fill_color: str = "lightblue"
    rounded: bool = False
    rx: float = 0
    ry: float = 0

    def transform_to_space(self, space: Space) -> Self:
        self.top_left = chart_to_svg_coordinates(space, self.top_left)
        self.bottom_right = chart_to_svg_coordinates(space, self.bottom_right)
        self.shape = Point(
            x=self.bottom_right.x - self.top_left.x,
            y=self.bottom_right.y - self.top_left.y,
        )
        width = self.bottom_right.x - self.top_left.x
        if self.rounded:
            self.rx = min(width * 0.05, 5)
            self.ry = min(width * 0.05, 5)
        return self

    def get_width(self) -> float:
        return self.bottom_right.x - self.top_left.x


def rect_from_bottom_center(
    bottom_center: Point,
    width: float,
    height: float,
    space: Space | None = None,
    rounded: bool = False,
) -> Rectangle:
    return Rectangle(
        top_left=Point(x=bottom_center.x - (width / 2), y=bottom_center.y + height),
        bottom_right=Point(x=bottom_center.x + (width / 2), y=bottom_center.y),
        space=space,
        rounded=rounded,
        classes=["fill-bar-light", "dark:fill-bar-dark", "bar"],
    )


class Line(Element):
    template_name: str = "line"
    from_pos: Point
    to_pos: Point
    path_length: float = 100
    stroke_color: str = "black"
    stroke_width: float = 5.0
    stroke_linecap: str = "round"

    def transform_to_space(self, space: Space) -> Self:
        self.from_pos = chart_to_svg_coordinates(space, self.from_pos)
        self.to_pos = chart_to_svg_coordinates(space, self.to_pos)
        return self

    def get_width(self) -> float:
        return abs(self.to_pos.x - self.from_pos.x)


class Path(Element):
    template_name: str = "path"
    points: list[Point]
    path_length: float = 100
    stroke_color: str = "black"
    stroke_width: float = 5.0
    stroke_linecap: str = "round"
    fill_color: str = "transparent"

    def transform_to_space(self, space: Space) -> Self:
        transformed_points: list[Point] = []
        for point in self.points:
            point = chart_to_svg_coordinates(space, point)
            transformed_points.append(point)

        self.points = transformed_points
        return self

    def get_width(self) -> float: ...


type YAlign = Literal["top"] | Literal["center"] | Literal["bottom"]
type XAlign = Literal["left"] | Literal["center"] | Literal["right"]


class Text(Element):
    template_name: str = "text"
    text: str
    font_size: int
    pos: Point
    x_align: XAlign = "left"
    y_align: YAlign = "center"
    font: TTFont
    classes: list[str] = ["fill-text-light", "dark:fill-text-dark"]
    rotate: float = 0.0
    original_pos: Point | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def prerender(self) -> None:
        self.original_pos = deepcopy(self.pos)

        y_min, y_max = get_text_height(self.font, self.text, self.font_size)
        height = y_max - y_min

        if self.y_align == "top":
            self.pos.y += y_max
        elif self.y_align == "center":
            self.pos.y += y_max - height / 2
        elif self.y_align == "bottom":
            self.pos.y += y_min

        width = self.get_width()

        if self.x_align == "center":
            self.pos.x -= width / 2
        elif self.x_align == "right":
            self.pos.x -= width

    def transform_to_space(self, space: Space) -> Self:
        self.pos = chart_to_svg_coordinates(space, self.pos)
        return self

    def get_width(self) -> float:
        return get_text_width(self.font, self.text, self.font_size)

    def get_height(self) -> float:
        y_min, y_max = get_text_height(self.font, self.text, self.font_size)
        return y_max - y_min


class ElementCollection(BaseModel):
    elements: list[Element] = []

    def render(self) -> list[str]:
        return [element.render() for element in self.elements]

    def append(self, element: Element) -> None:
        self.elements.append(element)

    def extend(self, other: "ElementCollection") -> None:
        self.elements.extend(other.elements)

    def get_width(self) -> float:
        widths = [element.get_width() for element in self.elements]
        return max(widths)
