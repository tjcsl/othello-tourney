from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from .models import Game
from .utils import *


class GameConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None
        self.connected = False

    def connect(self):
        game_id = self.scope["url_route"]["kwargs"]["game_id"]

        try:
            self.game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            self.close()
            return

        if not self.game.playing:
            self.close()
            return

        self.connected = True
        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            self.game.channels_group_name(), self.channel_name
        )

    def disconnect(self, code):
        self.connected = False

    def game_update(self):
        self.update_game()

    def game_log(self):
        self.send_log()

    def game_error(self):
        self.send_error()

    def update_game(self):
        if self.connected:
            self.game.refresh_from_db()
            self.send(serialize_game_info(self.game))

    def send_log(self):
        if self.connected:
            self.game.logs.refresh_from_db()
            self.send(serialize_game_log(self.game.logs.latest()))

    def send_error(self):
        if self.connected:
            self.game.errors.refresh_from_db()
            self.send(serialize_game_error(self.game.errors.latest()))
