from django.urls import path
from django.shortcuts import render

from . import views

app_name = "games"


def default(request):
    return render(request, f"games/{request.resolver_match.url_name}.html")


urlpatterns = [
    path("play/", views.play, name="play"),
    path("upload/", views.upload, name="upload"),
    path("watch/", views.watch, name="watch"),
    path("watch/<int:game_id>", views.watch, name="watch"),

    path("about/", default, name="about"),
    path("help/", default, name="help")
]
