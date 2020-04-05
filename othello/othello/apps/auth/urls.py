from django.urls import path

from . import views

app_name = "auth"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("upload/", views.upload, name="upload"),
    path("about_uploading/", views.about, name="about")
]
