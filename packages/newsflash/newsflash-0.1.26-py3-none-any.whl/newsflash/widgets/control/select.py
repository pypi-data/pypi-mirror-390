from django.http import HttpRequest
from typing import (
    Type,
    Self,
)
from enum import StrEnum

from pydantic import BaseModel, model_validator

from newsflash.base import ControlWidget
from newsflash.callback.builder import construct_callback
from newsflash.callback.models import Callback


class SelectContext(BaseModel):
    id: str
    options: list[str]
    selected: str
    callback: Callback | None
    swap_oob: bool

    @model_validator(mode="after")
    def check_allowed_value(self) -> Self:
        if self.selected not in self.options:
            raise ValueError("value not allowed")
        return self


class Select(ControlWidget):
    template_name: str = "control/select"
    selected: str

    def _get_options(self) -> list[str]: ...

    def _build(self, request: HttpRequest) -> SelectContext:
        assert self.id is not None

        if "on_input" in self.__class__.__dict__:
            callback = construct_callback(self.__class__.on_input, "select", "input")
        else:
            callback = None

        return SelectContext(
            id=self.id,
            options=self._get_options(),
            selected=self.selected,
            callback=callback,
            swap_oob=self.swap_oob,
        )

    def on_input(self, *args, **kwargs) -> None: ...


class EnumSelect(Select):
    template_name: str = "control/select"
    options: Type[StrEnum]

    def _get_options(self) -> list[str]:
        return [str(o) for o in self.options]


class ListSelect(Select):
    template_name: str = "control/select"
    options: list[str]

    def _get_options(self) -> list[str]:
        return self.options
