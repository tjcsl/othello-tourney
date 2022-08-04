from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("play/", views.play, name="play"),
    path("upload/", views.upload, name="upload"),
    path("download/", views.download, name="download"),
    path("watch/", views.watch, name="watch"),
    path("watch/<int:game_id>", views.watch, name="watch"),
    path("replay/", views.replay, name="replay"),
    path("help/", views.help_view, name="help"),
]
