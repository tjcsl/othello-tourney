from django.contrib import admin

from .models import *

admin.site.register(Tournament)
admin.site.register(TournamentPlayer)
admin.site.register(TournamentGame)
