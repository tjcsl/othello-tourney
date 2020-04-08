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

    @database_sync_to_async
    def get_game(self):
        return Game.objects.safe_get(id=self.game_id)


class GamePlayingConsumer(GameConsumer):
    async def connect(self):
        await super().connect()
        self.game = await self.get_game()


        if not self.game:
            await self.send_json({
                'type': "error",
                'error': f"Cannot find game with ID: {self.game_id}"
            })
            await self.close()
        elif not self.game.playing:
            await self.send_json({
                'type': "error",
                'error': f"Game {self.game_id} has already concluded"
            })


class GameWatchingConsumer(GameConsumer):
    pass
