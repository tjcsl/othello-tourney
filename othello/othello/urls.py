from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("othello.apps.auth.urls", namespace="auth")),
    path("oauth/", include("social_django.urls", namespace="social")),
]
