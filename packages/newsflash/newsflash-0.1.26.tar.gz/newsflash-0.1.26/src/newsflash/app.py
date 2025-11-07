from typing import Type, TypeVar

import uvicorn
from pydantic import BaseModel
from django.http import HttpRequest
from django.template.loader import render_to_string

from newsflash.widgets import Notifications
from newsflash.base import Widget


W = TypeVar("W", bound=Widget)


class Page(BaseModel):
    path: str
    name: str
    layout: str
    widgets: list[Type[Widget]]


class App:
    navbar: bool = False
    pages: list[Page]

    def __init__(self, pages: list[Page]) -> None:
        self.pages = pages

    def has_path(self, path: str) -> bool:
        for page in self.pages:
            if page.path.removeprefix("/") == path.removeprefix("/"):
                return True
        return False

    def get_page(self, path: str) -> Page:
        for page in self.pages:
            if page.path.removeprefix("/") == path.removeprefix("/"):
                return page
        raise ValueError()

    def get_widget(self, page_path: str, id: str, type: Type[W]) -> W | None:
        notifications = Notifications()
        if id == "notifications" and isinstance(notifications, type):
            return notifications

        page = self.get_page(page_path)

        for widget in page.widgets:
            _widget = widget()
            if _widget.id == id and isinstance(_widget, type):
                return _widget

        return None

    def render(self, request: HttpRequest, page_path: str) -> str:
        page = self.get_page(page_path)

        rendered_widgets = {}
        for widget in page.widgets:
            _widget = widget()
            assert _widget.id is not None
            rendered_widgets[_widget.id] = _widget.render(request)

        return render_to_string(
            template_name=page.layout,
            context=rendered_widgets,
            request=request,
        )

    def run(self):
        from newsflash.web.app.urls import set_urlpatterns
        from django.core.asgi import get_asgi_application
        from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler  # type: ignore

        set_urlpatterns(self)

        asgi = get_asgi_application()
        asgi = ASGIStaticFilesHandler(asgi)

        uvicorn.run(
            app=asgi,
        )
