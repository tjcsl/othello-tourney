from django.urls import path

from . import views

app_name = "tournaments"

urlpatterns = [
    path("", views.detail, name="current"),
    path("<int:tournament_id>", views.detail, name="detail"),
    path("previous/", views.TournamentListView.as_view(), name="previous"),
    path("create/", views.create, name="create"),
    path("manage/<int:tournament_id>", views.management, name="manage"),
    path("help/", views.help_view, name="help"),
]
