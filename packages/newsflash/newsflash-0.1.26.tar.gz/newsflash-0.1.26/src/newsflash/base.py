from typing import TypeVar

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.contrib.auth.models import User as UserModel
from pydantic import BaseModel


T = TypeVar("T", bound="Widget")


class User(BaseModel):
    username: str
    first_name: str
    last_name: str


def get_user_from_request(request: HttpRequest) -> "User | None":
    user = request.user
    if user.is_authenticated:
        assert isinstance(user, UserModel)

        return User(
            username=request.user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    return None


class Context(BaseModel):
    width: float
    height: float


class Widget(BaseModel):
    template_name: str = ""
    id: str | None = None
    width_in_px: float = 0.0
    height_in_px: float = 0.0
    span: int = 1
    swap_oob: bool = False

    _cancel_update: bool = False
    _request: HttpRequest | None = None
    _widget_type: str = "undefined"

    class Config:
        validate_assignment = True

    def cancel_update(self) -> None:
        self._cancel_update = True

    def _build(self, request: HttpRequest) -> Context: ...

    def render(self, request: HttpRequest) -> str:
        return render_to_string(
            f"app/widgets/{self.template_name}.html",
            context=self._build(request).model_dump(),
            request=request,
        )

    def update_dimensions(self, width_in_px: float, height_in_px: float) -> None:
        self.width_in_px = width_in_px
        self.height_in_px = height_in_px

    def get_user(self) -> User | None:
        if self._request is not None:
            return get_user_from_request(self._request)
        else:
            return None


class ChartWidget(Widget):
    _widget_type: str = "chart"


class ControlWidget(Widget):
    _widget_type: str = "control"


class TextWidget(Widget):
    _widget_type: str = "text"
