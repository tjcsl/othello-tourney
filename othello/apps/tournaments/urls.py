from django.urls import path
from django.shortcuts import render

from . import views

app_name = "tournaments"


def default(request):
    return render(request, f"tournaments/{request.resolver_match.url_name}.html")


urlpatterns = [
    path("management/", views.management, name="management"),
    path("previous/", views.management, name="previous"),
    path("current/", views.management, name="current"),
    path("help/", default, name="help"),
]
