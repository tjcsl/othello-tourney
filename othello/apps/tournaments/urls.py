from django.urls import path
from django.shortcuts import render

from . import views

app_name = "tournaments"


def default(request):
    return render(request, f"tournaments/{request.resolver_match.url_name}.html")


urlpatterns = [
    path("create/", views.create, name="create"),
    path("management/", views.create, name="management"),
    path("previous/", views.create, name="previous"),
    path("current/", views.create, name="current"),
]
