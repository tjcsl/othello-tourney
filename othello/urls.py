from django.contrib import admin
from django.urls import include, path

from .apps.errors.views import *

admin.site.site_header = "Othello Database Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("othello.apps.auth.urls", namespace="auth")),
    path("", include("othello.apps.games.urls", namespace="games")),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("tournaments/", include("othello.apps.tournaments.urls", namespace="tournaments")),
]

handler500 = handle_500_view
