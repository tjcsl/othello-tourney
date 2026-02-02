from django.contrib import admin

from .models import Game, GameError, Match, RatingHistory, Submission


class GameErrorAdmin(admin.TabularInline):
    model = GameError


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)
    inlines = [
        GameErrorAdmin,
    ]


class SubmissionAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class MatchAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class RatingHistoryAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Game, GameAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(RatingHistory, RatingHistoryAdmin)
