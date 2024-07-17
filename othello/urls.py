from django.contrib import admin
from django.urls import include, path

from .apps.errors.views import handle_500_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("othello.apps.auth.urls", namespace="auth")),
    path("", include("othello.apps.games.urls", namespace="games")),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("tournaments/", include("othello.apps.tournaments.urls", namespace="tournaments")),
    path("rating/", include("othello.apps.rating.urls", namespace="rating")),
]

handler500 = handle_500_view
