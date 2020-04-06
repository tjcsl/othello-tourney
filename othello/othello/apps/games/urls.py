from django.urls import path

from . import views
from ..auth.decorators import login_required

app_name = "games"

urlpatterns = [
    # path("play/", views.play, name="login"),
    # path("watch/", views.watch, name="logout"),
    path("about/", views.about, name="about"),
    path("upload/", login_required(views.UploadView.as_view()), name="upload"),
    path("help/", views.help, name="help")
]
