from django.shortcuts import render
from django.urls import path

from . import views

app_name = "tournaments"


def default(request):
    return render(request, f"tournaments/{request.resolver_match.url_name}.html")


urlpatterns = [
    path("", views.detail, name="current"),
    path("<int:tournament_id>", views.detail, name="detail"),
    path("previous/", views.TournamentListView.as_view(), name="previous"),
    path("create/", views.create, name="create"),
    path("manage/<int:tournament_id>", views.management, name="manage"),
    path("help/", default, name="help"),
]
