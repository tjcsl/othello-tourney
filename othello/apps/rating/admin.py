from django.contrib import admin

from .models import Gauntlet, RankedManager


class RankedManagerAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class GauntletAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(RankedManager, RankedManagerAdmin)
admin.site.register(Gauntlet, GauntletAdmin)
