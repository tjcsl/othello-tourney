from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("play/", views.play, name="play"),
    path("upload/", views.upload, name="upload"),
    path("watch/", views.watch, name="watch"),
    path("watch/<int:game_id>", views.watch, name="watch"),
    path("about/", views.about, name="about"),
    path("help/", views.help, name="help"),
]
