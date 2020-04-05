from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    # path("play/", views.play, name="login"),
    # path("watch/", views.watch, name="logout"),
    path("about/", views.about, name="about"),
]
