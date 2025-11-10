from typing import Callable
from inspect import signature

from .models import Callback, WidgetIO
from .utils import process_callback_arg


def construct_callback(
    callback_fn: Callable,
    endpoint_name: str,
    trigger_event: str,
) -> Callback:
    sig = signature(callback_fn)
    input_ids: list[str] = []
    target_ids: list[str] = []

    for param in sig.parameters:
        if param == "self" or param == "selected":
            continue

        _, widget_id, widget_io = process_callback_arg(
            callback_fn=callback_fn, parameter=param
        )

        if widget_io == WidgetIO.INPUT or widget_io == WidgetIO.BOTH:
            input_ids.append(widget_id + "-input")

        if widget_io == WidgetIO.OUTPUT or widget_io == WidgetIO.BOTH:
            target_ids.append(widget_id)

    return Callback(
        endpoint_name=endpoint_name,
        trigger_event=trigger_event,
        inputs=input_ids,
        targets=target_ids,
        target_wrapper_ids=", ".join([f"#{target}-wrapper" for target in target_ids]),
    )
