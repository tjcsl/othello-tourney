from channels.auth import AuthMiddlewareStack
from channels.generic.websocket import WebsocketConsumer
from channels.routing import ProtocolTypeRouter, URLRouter

from django.urls import path


class WebsocketCloseConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.close()

    def receive(self, text_data=None, bytes_data=None):
        pass

    def disconnect(self, code):
        pass


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/play/<int:game_id>', consumers.GameConsumer),
                path('ws/watch/<int:game_id>', consumers.GameConsumer),
                path('<path:path>', WebsocketCloseConsumer)
            ]
        )
    ),
})
