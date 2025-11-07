from typing import Callable, Literal, Type
from inspect import signature
import json
from urllib.parse import urlparse

from django.http import HttpRequest

from newsflash.base import Widget
from newsflash.widgets.control.select import Select
from newsflash.widgets.chart.base import Chart
from .utils import process_callback_arg
from .models import WidgetIO


# TODO: find better location (and deduplicate)
type ChartDimension = dict[Literal["width"] | Literal["height"], float]
type ChartDimensions = dict[str, ChartDimension]


def widget_type_to_instance(
    widget_type: Type[Widget],
    input_value: str | None,
    chart_dimension: ChartDimension | None,
):
    if issubclass(widget_type, Select):
        assert input_value is not None
        widget = widget_type(selected=input_value)
    elif issubclass(widget_type, Chart):
        assert chart_dimension is not None
        widget = widget_type(
            width_in_px=chart_dimension["width"],
            height_in_px=chart_dimension["height"],
            swap_oob=True,
        )
    else:
        widget = widget_type()

    return widget


def get_callback_in_and_outputs(
    callback_fn: Callable,
    additional_inputs: dict[str, str],
    chart_dimensions_dict: ChartDimensions,
) -> tuple[dict[str, Widget], dict[str, Widget]]:
    sig = signature(callback_fn)

    callback_inputs: dict[str, Widget] = {}
    callback_outputs: dict[str, Widget] = {}
    for param in sig.parameters:
        if param == "self" or param == "selected":
            continue

        widget_type, widget_id, widget_io = process_callback_arg(callback_fn, param)

        widget = widget_type_to_instance(
            widget_type=widget_type,
            input_value=additional_inputs.get(widget_id, None),
            chart_dimension=chart_dimensions_dict.get(widget_id, None),
        )

        callback_inputs[param] = widget
        if widget_io == WidgetIO.OUTPUT or widget_io == WidgetIO.BOTH:
            widget.swap_oob = True
            callback_outputs[param] = widget

    return callback_inputs, callback_outputs


def render_callback_outputs(
    callback_outputs: dict[str, Widget], request: HttpRequest
) -> bytes:
    result: str = ""

    for callback_output in callback_outputs.values():
        if callback_output._cancel_update:
            continue
        if isinstance(callback_output, Chart):
            result += "\n" + callback_output.render_chart(request)
        else:
            result += "\n" + callback_output.render(request)

    return result.encode()


def parse_chart_dimensions(request: HttpRequest) -> ChartDimensions:
    dimensions = json.loads(request.POST["dimensions"])

    chart_dimensions = [
        {k.removesuffix("-container"): v for k, v in chart.items()}
        for chart in dimensions
    ]

    chart_dimensions_dict: ChartDimensions = {}
    for chart in chart_dimensions:
        chart_dimensions_dict.update(chart)

    return chart_dimensions_dict


def parse_additional_inputs(request: HttpRequest, trigger: str) -> dict[str, str]:
    additional_inputs: dict[str, str] = {}

    for k in request.POST:
        if k.endswith("-value") and k.removesuffix("-value") != trigger:
            _value = request.POST[k]
            assert isinstance(_value, str)
            additional_inputs[k.removesuffix("-value")] = _value

    return additional_inputs


def parse_url_path(url: str) -> str:
    parsed = urlparse(url)
    path = str(parsed.path)
    return path


def parse_request_inputs(
    request: HttpRequest,
) -> tuple[str, str, dict[str, str], ChartDimensions]:
    trigger: str | None = request.headers.get("Hx-Trigger")
    url: str | None = request.headers.get("HX-Current-URL")
    assert trigger is not None and url is not None

    path = parse_url_path(url)
    additional_inputs = parse_additional_inputs(request, trigger)
    chart_dimensions_dict = parse_chart_dimensions(request)
    return path, trigger, additional_inputs, chart_dimensions_dict
