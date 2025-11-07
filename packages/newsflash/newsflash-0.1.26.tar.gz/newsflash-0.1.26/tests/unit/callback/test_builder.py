from newsflash_cli.main import setup_django
setup_django()

from typing import Any, Annotated
import unittest

from newsflash.callback.builder import construct_callback
from newsflash.callback.models import Callback
from newsflash.widgets.chart.bar import BarChart
from newsflash.widgets.control.button import Button


class TestCallback(unittest.TestCase):
    def test_construct_callback_with_button_and_chart(self):
        def dummy_callback_function(
            self: Any,
            bar_chart: Annotated[BarChart, "bar-chart-id"],
            button: Annotated[Button, "button-id"],
        ):
            pass

        result = construct_callback(
            callback_fn=dummy_callback_function,
            endpoint_name="ABC",
            trigger_event="click",
        )

        expected = Callback(
            endpoint_name="ABC",
            trigger_event="click",
            inputs=["button-id-input"],
            targets=["bar-chart-id"],
            target_wrapper_ids="#bar-chart-id-wrapper",
        )

        self.assertEqual(result, expected)
