from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/play/(?P<game_id>\d+)/$', consumers.GamePlayingConsumer),
    re_path(r'ws/watch/(?P<game_id>\d+)/$', consumers.GameWatchingConsumer)
]