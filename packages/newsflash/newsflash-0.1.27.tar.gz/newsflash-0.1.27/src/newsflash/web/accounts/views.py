from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET

from django.contrib.auth import authenticate, login, logout


@require_GET
def login_page(request: HttpRequest) -> HttpResponse:
    return render(request, "accounts/login.html")


@require_POST
def auth_request(request: HttpRequest) -> HttpResponse:
    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return redirect("home")
    else:
        messages.error(request, "Login insuccessful, please try again.")
        return redirect("login-page")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("home")
