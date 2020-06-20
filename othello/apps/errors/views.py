from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def handle_500_view(request: HttpRequest) -> HttpResponse:
    return render(request, "error/500.html", status=500)
