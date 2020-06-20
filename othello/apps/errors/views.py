from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def handle_500_view(request: HttpRequest) -> HttpResponse:
    return render(request, "error/500.html", status=500)
