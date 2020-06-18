from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("error/", views.error, name="error"),
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
