from typing import Annotated
import json
from django.test import TestCase, RequestFactory
import unittest
from unittest.mock import patch, MagicMock

from newsflash.callback.caller import (
    widget_type_to_instance,
    get_callback_in_and_outputs,
    render_callback_outputs,
    parse_additional_inputs,
    parse_chart_dimensions,
    parse_request_inputs,
    ChartDimension,
)
from newsflash.callback.models import WidgetIO
from newsflash.widgets import (
    Button,
    BarChart,
    ListSelect,
)
from newsflash.base import Widget


class TestWidgetTypeToInstance(unittest.TestCase):
    def test_button(self):
        class TestButton(Button):
            id: str = "test-button"
            text: str = "Test Button"

        widget_type = TestButton
        input_value = None
        chart_dimension = None

        result = widget_type_to_instance(
            widget_type=widget_type,
            input_value=input_value,
            chart_dimension=chart_dimension,
        )

        expected = TestButton()
        self.assertEqual(result, expected)

    def test_select(self):
        class TestSelect(ListSelect):
            id: str = "test-select"
            options: list[str] = ["a", "b", "c"]
            selected: str = "a"

        widget_type = TestSelect
        input_value = "b"
        chart_dimension = None

        result = widget_type_to_instance(
            widget_type=widget_type,
            input_value=input_value,
            chart_dimension=chart_dimension,
        )

        expected = TestSelect(selected="b")
        self.assertEqual(result, expected)

    def test_chart(self):
        class TestChart(BarChart):
            id: str = "test-bar-chart"

        widget_type = TestChart
        input_value = None
        chart_dimension: ChartDimension = {"width": 400.5, "height": 200}

        result = widget_type_to_instance(
            widget_type=widget_type,
            input_value=input_value,
            chart_dimension=chart_dimension,
        )

        expected = TestChart(
            width_in_px=400.5,
            height_in_px=200,
            swap_oob=True,
        )
        self.assertEqual(result, expected)


class TestGetCallbackInAndOutputs(unittest.TestCase):
    def test_get_callback_in_and_outputs_button(
        self,
    ):
        class TestButton(Button):
            id: str = "test-button"
            text: str = "Test Button"

            def on_click(
                self,
                widget_a: Annotated[str, "a"],
                widget_b: Annotated[str, "b"],
                widget_c: Annotated[str, "c"],
            ) -> None:
                pass

        callback_args_side_effect = [
            ("TypeA", "a", WidgetIO.INPUT),
            ("TypeB", "b", WidgetIO.OUTPUT),
            ("TypeC", "c", WidgetIO.BOTH),
        ]

        mock_widget_a = MagicMock()
        mock_widget_b = MagicMock()
        mock_widget_c = MagicMock()
        mock_widget_types = [mock_widget_a, mock_widget_b, mock_widget_c]

        with (
            patch(
                "newsflash.callback.caller.widget_type_to_instance",
                side_effect=mock_widget_types,
            ),
            patch(
                "newsflash.callback.caller.process_callback_arg",
                side_effect=callback_args_side_effect,
            ),
        ):
            inputs, outputs = get_callback_in_and_outputs(
                callback_fn=TestButton.on_click,
                additional_inputs={},
                chart_dimensions_dict={},
            )

        self.assertEqual(
            inputs,
            {
                "widget_a": mock_widget_a,
                "widget_b": mock_widget_b,
                "widget_c": mock_widget_c,
            },
        )
        self.assertEqual(
            outputs, {"widget_b": mock_widget_b, "widget_c": mock_widget_c}
        )


def mock_render_to_string(self, request) -> str:
    return f"<dummy widget: {self.id}>"


class TestRenderCallbackOutputs(TestCase):
    def setUp(self) -> None:
        self.button = Button(id="test-button", text="Test Button")
        self.select = ListSelect(
            id="test-select", options=["a", "b", "c"], selected="a"
        )
        self.chart = BarChart(id="test-bar", xs=[1, 2], x_labels=["1", "2"], ys=[2, 3])

    @patch("newsflash.base.Widget.render", new=mock_render_to_string)
    @patch("newsflash.widgets.chart.base.Chart.render_chart", new=mock_render_to_string)
    def test_render_callback_outputs(self):
        factory = RequestFactory()
        request = factory.post("path/to/endpoint")

        callback_outputs: dict[str, Widget] = {
            "test-button": self.button,
            "test-select": self.select,
            "test-bar": self.chart,
        }
        result = render_callback_outputs(callback_outputs, request=request)

        expected = "\n<dummy widget: test-button>\n<dummy widget: test-select>\n<dummy widget: test-bar>"
        self.assertEqual(result, expected.encode())

    @patch("newsflash.base.Widget.render", new=mock_render_to_string)
    @patch("newsflash.widgets.chart.base.Chart.render_chart", new=mock_render_to_string)
    def test_cancel_update(self):
        self.button.cancel_update()
        self.chart.cancel_update()

        factory = RequestFactory()
        request = factory.post("path/to/endpoint")

        callback_outputs: dict[str, Widget] = {
            "test-button": self.button,
            "test-select": self.select,
            "test-bar": self.chart,
        }
        result = render_callback_outputs(callback_outputs, request=request)

        expected = "\n<dummy widget: test-select>"
        self.assertEqual(result, expected.encode())


class TestParseAdditionalInputs(TestCase):
    def setUp(self) -> None:
        factory = RequestFactory()
        request = factory.post(
            "path/to/endpoint",
            {
                "trigger-input-value": "hi!",
                "some-additional-input-value": "abc",
                "another-additional-input-value": "def",
            },
        )

        self.request = request

    def test_parse_additional_inputs(self):
        result = parse_additional_inputs(
            self.request,
            trigger="trigger-input",
        )

        expected = {
            "some-additional-input": "abc",
            "another-additional-input": "def",
        }

        self.assertEqual(result, expected)

    def test_parse_additional_inputs_different_trigger(self):
        result = parse_additional_inputs(
            self.request,
            trigger="some-additional-input",
        )

        expected = {
            "trigger-input": "hi!",
            "another-additional-input": "def",
        }

        self.assertEqual(result, expected)


class TestParseChartDimensions(TestCase):
    def test_parse_chart_dimensions(self) -> None:
        dimensions = [
            {
                "chart-a-container": {
                    "width": 200,
                    "height": 100.50,
                },
                "chart-b-container": {
                    "width": 123.45,
                    "height": 234.56,
                },
            }
        ]

        factory = RequestFactory()
        request = factory.post(
            "path/to/endpoint", {"dimensions": json.dumps(dimensions)}
        )

        result = parse_chart_dimensions(request)

        expected = {
            "chart-a": {
                "width": 200,
                "height": 100.50,
            },
            "chart-b": {
                "width": 123.45,
                "height": 234.56,
            },
        }

        self.assertEqual(result, expected)


class TestParseRequestInputs(TestCase):
    @patch("newsflash.callback.caller.parse_chart_dimensions")
    @patch("newsflash.callback.caller.parse_additional_inputs")
    def test_parse_request_inputs(
        self, mock_parse_additional_inputs, mock_parse_chart_dimensions
    ):
        mock_parse_additional_inputs.return_value = "additional-inputs"
        mock_parse_chart_dimensions.return_value = "chart-dimensions"

        factory = RequestFactory()
        request = factory.post(
            "http://localhost:8000/path/to/endpoint",
            headers={
                "HX-Current-URL": "http://localhost:8000/path",
                "Hx-Trigger": "trigger-element-id",
            },
        )

        result = parse_request_inputs(request)
        self.assertEqual(result[0], "/path")
        self.assertEqual(result[1], "trigger-element-id")
        self.assertEqual(result[2], "additional-inputs")
        self.assertEqual(result[3], "chart-dimensions")
