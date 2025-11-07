from django.http import HttpRequest
from django.template.loader import render_to_string

from newsflash.base import ChartWidget
from .utils import Padding
from newsflash.callback.builder import construct_callback
from newsflash.callback.models import Callback

from pydantic import BaseModel


class ChartWrapperContext(BaseModel):
    id: str
    title: str | None
    description: str | None
    endpoint_name: str
    callback: Callback | None


class ChartContext(BaseModel):
    id: str
    width: float
    height: float
    width_half: float
    x_axis: str
    y_axis: str
    title: str | None
    swap_oob: bool


class Chart(ChartWidget):
    template_name: str = "chart/container"
    chart_template_name: str = "chart/chart"
    title: str | None = None
    description: str | None = None
    endpoint_name: str = "chart"
    padding: Padding = Padding(ps=50, pt=60, pe=20, pb=30)
    x_major_grid_lines: bool = False
    x_minor_grid_lines: bool = False
    y_major_grid_lines: bool = False
    y_minor_grid_lines: bool = False
    x_axis_label: str | None = None
    y_axis_label: str | None = None
    swap_oob: bool = False
    require_login: bool = False

    def on_load(self) -> None:
        pass

    def _build(self, request: HttpRequest) -> ChartWrapperContext:
        assert self.id is not None, "A chart must have an ID."
        assert self.endpoint_name is not None

        if "on_load" in self.__class__.__dict__:
            callback = construct_callback(
                self.__class__.on_load,
                "chart",
                "revealed delay:50ms, resizeChart delay:250ms",
            )
        else:
            callback = None

        return ChartWrapperContext(
            id=self.id,
            title=self.title,
            description=self.description,
            endpoint_name=self.endpoint_name,
            callback=callback,
        )

    def _build_chart(self, request: HttpRequest, id: str) -> ChartContext: ...

    def render_chart(self, request: HttpRequest) -> str:
        assert self.id is not None
        context = self._build_chart(request, id=self.id)
        return render_to_string(
            f"app/widgets/{self.chart_template_name}.html",
            context=context.model_dump(),
            request=request,
        )

    def render_unauthorized(self, request: HttpRequest) -> str:
        assert self.id is not None
        return render_to_string(
            "app/unauthorized.html",
            context={"id": self.id},
            request=request,
        )
