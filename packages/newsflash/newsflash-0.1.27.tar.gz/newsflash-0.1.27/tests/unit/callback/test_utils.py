import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newsflash.web.settings")

from typing import Any, Annotated, get_args, Type, Callable
from inspect import signature
import unittest
from unittest.mock import patch

from newsflash.callback.utils import process_callback_arg
from newsflash.callback.models import WidgetIO
from newsflash.widgets import Button, Notifications, BarChart
from newsflash.base import Widget


def callback_fn(
    self: Any,
    # The widget type in this line is a "ForwardRef", indicated
    # by quotes around the type hint. This is necessary because
    # the actual widget class is only defined later in the file.
    # In the TestResolveForwardRef test we assert that the
    # ForwardRef is properly resolved to the actual type of the
    # widget.
    test_widget: Annotated["TestWidget", "test-widget"],
):
    pass


class TestWidget(Button):
    id: str = "test-widget"


class TestProcessCallbackArgs(unittest.TestCase):
    def setUp(self) -> None:
        def dummy_callback_function(
            self: Any,
            bar_chart: Annotated[BarChart, "bar-chart-id"],
            button: Annotated[Button, "button-id"],
            notifications: Annotated[Notifications, "notifications"],
        ):
            pass

        self.dummy_callback_function = dummy_callback_function

    def test_process_callback_arg_for_chart(self):
        result = process_callback_arg(self.dummy_callback_function, "bar_chart")

        expected = (BarChart, "bar-chart-id", WidgetIO.OUTPUT)

        self.assertEqual(result, expected)

    def test_process_callback_arg_for_button(self):
        result = process_callback_arg(self.dummy_callback_function, "button")

        expected = (Button, "button-id", WidgetIO.BOTH)

        self.assertEqual(result, expected)

    def test_process_callback_arg_for_notifications(self):
        result = process_callback_arg(self.dummy_callback_function, "notifications")

        expected = (Notifications, "notifications", WidgetIO.OUTPUT)

        self.assertEqual(result, expected)
