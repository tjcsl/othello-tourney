from django.urls import path

from . import views

app_name = "rating"

urlpatterns = [
    path("gauntlet", views.gauntlet, name="gauntlet"),
    path("help", views.help, name="help"),
    path("standings", views.standings, name="standings"),
    path("history", views.history, name="history"),
    path("manage", views.manage, name="manage"),
    path("deleteGauntlet", views.deleteGauntlet, name="deleteGauntlet"),
]
