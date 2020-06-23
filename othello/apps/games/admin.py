from django.contrib import admin

from .models import Game, GameError, Submission


class GameErrorAdmin(admin.TabularInline):
    model = GameError


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
    inlines = [
        GameErrorAdmin,
    ]


class SubmissionAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Game, GameAdmin)
admin.site.register(Submission, SubmissionAdmin)
