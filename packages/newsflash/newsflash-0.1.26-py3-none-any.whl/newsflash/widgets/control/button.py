from django.http import HttpRequest

from pydantic import BaseModel

from newsflash.base import ControlWidget
from newsflash.callback.builder import construct_callback
from newsflash.callback.models import Callback


class ButtonContext(BaseModel):
    id: str
    text: str
    callback: Callback | None


class Button(ControlWidget):
    template_name: str = "control/button"
    text: str

    def _build(self, request: HttpRequest) -> ButtonContext:
        assert self.id is not None

        callback = construct_callback(self.__class__.on_click, "click", "click")

        return ButtonContext(
            id=self.id,
            text=self.text,
            callback=callback,
        )

    def on_click(self, *args, **kwargs) -> None: ...
