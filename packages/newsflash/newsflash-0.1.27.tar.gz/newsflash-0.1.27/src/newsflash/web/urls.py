from django.urls import path, include


urlpatterns = [
    path("accounts/", include("newsflash.web.accounts.urls")),
    path("", include("newsflash.web.app.urls")),
]
