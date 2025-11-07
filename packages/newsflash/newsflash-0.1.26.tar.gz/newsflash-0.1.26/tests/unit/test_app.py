import unittest
from unittest.mock import patch
from typing import Type

from django.http import HttpRequest
from django.test import TestCase, RequestFactory
from pydantic import BaseModel

from newsflash.app import App, Page
from newsflash.base import Widget
from newsflash.widgets import Notifications


class DummyContext(BaseModel):
    key: str = "value"


class DummyWidget(Widget):
    id: str = "dummy-widget"

    def _build(self, request: HttpRequest) -> DummyContext:
        return DummyContext()


def build_dummy_page() -> Page:
    widgets: list[Type[Widget]] = [DummyWidget]

    return Page(
        path="/path/to/page",
        name="test-page",
        layout="test_layout.html",
        widgets=widgets,
    )


class TestApp(unittest.TestCase):
    def setUp(self) -> None:
        self.page = build_dummy_page()

    def test_init_app(self):
        app = App(pages=[self.page])

    def test_has_path(self):
        app = App(pages=[self.page])

        has_path = app.has_path("/path/to/page")
        self.assertTrue(has_path)

        has_path = app.has_path("/path/to/nonexisting/page")
        self.assertFalse(has_path)

    def test_get_page(self):
        app = App(pages=[self.page])

        page = app.get_page("/path/to/page")
        self.assertEqual(page, self.page)

        with self.assertRaises(ValueError):
            app.get_page("/path/to/nonexisting/page")

    def test_get_widget(self):
        app = App(pages=[self.page])

        widget = app.get_widget(
            page_path="/path/to/page",
            id="dummy-widget",
            type=DummyWidget,
        )

        self.assertIsNotNone(widget)
        self.assertIsInstance(widget, DummyWidget)

        # so that the linter also knows that the widget is not None
        assert widget is not None
        self.assertIsNotNone(widget.id)

        self.assertEqual(widget.id, "dummy-widget")

    def test_get_notification_widget(self):
        app = App(pages=[self.page])

        widget = app.get_widget(
            page_path="/path/to/page",
            id="notifications",
            type=Notifications,
        )

        self.assertIsNotNone(widget)
        self.assertIsInstance(widget, Notifications)

        # so that the linter also knows that the widget is not None,
        # before accessing its properties
        assert widget is not None
        self.assertIsNotNone(widget.id)

        self.assertEqual(widget.id, "notifications")

    def test_get_nonexisting_widget(self):
        app = App(pages=[self.page])

        widget = app.get_widget(
            page_path="/path/to/page",
            id="nonexisting-widget",
            type=DummyWidget,
        )

        self.assertIsNone(widget)


class TestAppDjango(TestCase):
    def setUp(self) -> None:
        self.page = build_dummy_page()

    @patch("newsflash.app.render_to_string")
    @patch("newsflash.base.render_to_string")
    def test_render(self, mock_render_widget_to_string, mock_render_app_to_string):
        mock_render_widget_to_string.return_value = "rendered widget"
        mock_render_app_to_string.return_value = "rendered app"

        factory = RequestFactory()
        request = factory.post("path/to/endpoint")

        app = App(pages=[self.page])
        result = app.render(request=request, page_path="/path/to/page")

        self.assertEqual(result, "rendered app")
