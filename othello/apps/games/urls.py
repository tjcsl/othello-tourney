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
    path("queue/", views.queue, name="queue"),
    path("queue/json/", views.queue_json, name="queue_json"),
    path("request_match/", views.request_match, name="request_match"),
    path("match_replay/<int:match_id>/", views.match_replay, name="match_replay"),
    path("help/", views.help_view, name="help"),
]
