from django.contrib import admin

from .models import Game, Submission


class GameAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class SubmissionAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


admin.site.register(Game, GameAdmin)
admin.site.register(Submission, SubmissionAdmin)
