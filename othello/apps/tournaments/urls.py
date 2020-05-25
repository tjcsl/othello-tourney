from django.urls import path
from django.shortcuts import render

from . import views

app_name = "tournaments"


def default(request):
    return render(request, f"tournaments/{request.resolver_match.url_name}.html")


urlpatterns = [
    path("", views.detail, name="current"),
    path("<int:tournament_id>", views.detail, name="detail"),
    path("previous/", views.TournamentListView.as_view(), name="previous"),
    path("management/", views.management, name="management"),

    path("help/", default, name="help"),
]
