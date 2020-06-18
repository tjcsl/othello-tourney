from django.contrib import admin

from .models import Tournament, TournamentGame, TournamentPlayer

admin.site.register(Tournament)
admin.site.register(TournamentPlayer)
admin.site.register(TournamentGame)
