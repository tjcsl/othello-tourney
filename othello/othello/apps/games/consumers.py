from typing import Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Game


class GameConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs'].get('game_id', -1)
        self.game_group_name = f"game_{self.game_id}"


        # Init Moderator here

        await self.channel_layer.group_add(
            self.game_group_name,
            self.game_id
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.game_id
        )
