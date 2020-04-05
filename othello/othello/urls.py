from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("social_django.urls", namespace="social")),
    path("", include("othello.apps.auth.urls", namespace="auth")),
    path("admin/", admin.site.urls),
]
