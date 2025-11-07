from django.urls import path
from newsflash.app import App
from . import views


urlpatterns = []


def set_urlpatterns(app: App) -> None:
    global urlpatterns

    urlpatterns = [
        path("_click", views.build_button_view(app), name="click"),
        path("_select", views.build_select_view(app), name="select"),
        path("_chart", views.build_chart_view(app), name="chart"),
        path("", views.build_main_view(app), name="home"),
        path("<path:page_path>", views.build_main_view(app), name="home"),
    ]
