from inspect import signature
from typing import Callable, Type, get_args, get_type_hints

from .models import WidgetIO
from newsflash.base import Widget, ChartWidget, ControlWidget, TextWidget


def process_callback_arg(
    callback_fn: Callable, parameter: str
) -> tuple[Type[Widget], str, WidgetIO]:
    sig = signature(callback_fn)

    widget_type = get_type_hints(callback_fn)[parameter]
    
    annotation = sig.parameters[parameter].annotation
    args = get_args(annotation)

    if len(args) == 0:
        widget_id = widget_type().id
    else:
        widget_id = args[1]

    if issubclass(widget_type, ControlWidget):
        widget_io = WidgetIO.BOTH
    if issubclass(widget_type, TextWidget):
        widget_io = WidgetIO.OUTPUT
    if issubclass(widget_type, ChartWidget):
        widget_io = WidgetIO.OUTPUT

    return widget_type, widget_id, widget_io
