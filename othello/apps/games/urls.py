from django.urls import path, re_path
from django.shortcuts import render


from . import views
from ..auth.decorators import login_required

app_name = "games"


def default(request):
    return render(request, f"games/{request.resolver_match.url_name}.html")


urlpatterns = [
    path("play/", views.play, name="play"),
    path("watch/<int:game_id>", views.watch, name="watch"),
    path("watch/", views.watch, name="watch"),
    path("upload/", login_required(views.UploadView.as_view()), name="upload"),
    path("about/", default, name="about"),
    path("help/", default, name="help")
]
