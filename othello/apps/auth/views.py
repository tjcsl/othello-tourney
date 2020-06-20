from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/index.html")


def login(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/login.html")


def error(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/error.html")
