from enum import StrEnum
from pydantic import BaseModel


class Callback(BaseModel):
    endpoint_name: str
    trigger_event: str
    inputs: list[str]
    targets: list[str]
    target_wrapper_ids: str


class WidgetIO(StrEnum):
    INPUT = "input"
    OUTPUT = "output"
    BOTH = "input+output"
