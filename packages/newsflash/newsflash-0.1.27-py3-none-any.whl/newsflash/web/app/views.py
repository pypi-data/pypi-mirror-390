from typing import Callable, Literal

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render

from newsflash.app import App
from newsflash.widgets.chart.base import Chart
from newsflash.widgets.control.select import Select
from newsflash.widgets import Button
from newsflash.callback.caller import (
    get_callback_in_and_outputs,
    render_callback_outputs,
    parse_request_inputs,
)


type ChartDimension = dict[Literal["width"] | Literal["height"], float]
type ChartDimensions = dict[str, ChartDimension]


def build_main_view(app: App) -> Callable:
    def main(request: HttpRequest, page_path: str = "/") -> HttpResponse:
        if app.has_path(page_path):
            return render(
                request,
                "app/page.html",
                context={
                    "content": app.render(request, page_path),
                },
            )
        else:
            return HttpResponseNotFound()

    return main


def build_button_view(app: App) -> Callable:
    def click(request: HttpRequest) -> HttpResponse:
        path, trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )

        button_element = app.get_widget(path, trigger, Button)
        assert button_element is not None

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            button_element.on_click, additional_inputs, chart_dimensions_dict
        )

        button_element._request = request
        button_element.on_click(**callback_inputs)
        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return click


def build_select_view(app: App) -> Callable:
    def select(request: HttpRequest) -> HttpResponse:
        path, trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )
        trigger = trigger.removesuffix("-input")
        value = request.POST[f"{trigger}-value"]

        select_element = app.get_widget(path, trigger, Select)
        assert select_element is not None

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            select_element.on_input, additional_inputs, chart_dimensions_dict
        )

        value_type = type(select_element.selected)
        select_element.selected = value_type(value)
        select_element._request = request
        select_element.on_input(**callback_inputs)

        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return select


def build_chart_view(app: App) -> Callable:
    def chart(request: HttpRequest) -> HttpResponse:
        path, trigger, additional_inputs, chart_dimensions_dict = parse_request_inputs(
            request
        )
        trigger = trigger.removesuffix("-wrapper")

        chart_element = app.get_widget(path, trigger, Chart)
        assert chart_element is not None

        chart_element.width_in_px = chart_dimensions_dict[trigger]["width"]
        chart_element.height_in_px = chart_dimensions_dict[trigger]["height"]

        callback_inputs, callback_outputs = get_callback_in_and_outputs(
            chart_element.on_load, additional_inputs, chart_dimensions_dict
        )

        callback_outputs[trigger] = chart_element
        chart_element._request = request
        chart_element.on_load(**callback_inputs)

        return HttpResponse(render_callback_outputs(callback_outputs, request))

    return chart
