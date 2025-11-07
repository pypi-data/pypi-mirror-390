from inspect import signature, getsourcefile
from runpy import run_path
from typing import Callable, Type, get_args, ForwardRef

from .models import WidgetIO
from newsflash.base import Widget, ChartWidget, ControlWidget, TextWidget


def resolve_forward_ref(
    widget_type: Type[Widget], callback_fn: Callable
) -> Type[Widget]:
    if isinstance(widget_type, ForwardRef):
        source_file = getsourcefile(callback_fn)
        assert source_file is not None
        file_globals = run_path(source_file)
        widget_type = file_globals[widget_type.__forward_arg__]

    return widget_type


def process_callback_arg(
    callback_fn: Callable, parameter: str
) -> tuple[Type[Widget], str, WidgetIO]:
    sig = signature(callback_fn)
    annotation = sig.parameters[parameter].annotation
    args = get_args(annotation)

    widget_type = args[0]
    widget_type = resolve_forward_ref(widget_type, callback_fn)
    widget_id = args[1]

    try:
        widget_io = args[2]
    except IndexError:
        if issubclass(widget_type, ControlWidget):
            widget_io = WidgetIO.INPUT
        if issubclass(widget_type, TextWidget):
            widget_io = WidgetIO.OUTPUT
        if issubclass(widget_type, ChartWidget):
            widget_io = WidgetIO.OUTPUT

    return widget_type, widget_id, widget_io
