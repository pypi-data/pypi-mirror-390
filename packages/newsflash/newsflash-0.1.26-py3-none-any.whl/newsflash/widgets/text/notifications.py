from django.http import HttpRequest

from pydantic import BaseModel
from newsflash.base import TextWidget


class Notification(BaseModel):
    text: str
    duration_in_ms: int


class NotificationsContext(BaseModel):
    notifications: list[Notification]


class Notifications(TextWidget):
    id: str = "notifications"
    template_name: str = "text/notification"
    notifications: list[Notification] = []

    def push(self, text: str, duration_in_ms: int = 5000) -> None:
        self.notifications.append(
            Notification(
                text=text,
                duration_in_ms=duration_in_ms,
            )
        )

    def _build(self, request: HttpRequest) -> NotificationsContext:
        return NotificationsContext(notifications=self.notifications)
