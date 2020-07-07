import json
import logging
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DownloadSubmissionForm, GameForm, SubmissionForm
from .models import Game
from .utils import serialize_game_info

logger = logging.getLogger("othello")


@login_required
def upload(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(
            request,
            "games/upload.html",
            {
                "success": False,
                "submission_form": SubmissionForm(),
                "download_form": DownloadSubmissionForm(request.user),
            },
        )
    success = False
    form = SubmissionForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            success = True
        except BaseException as e:
            messages.error(
                request,
                "Unable to upload script at this time, try again later",
                extra_tags="danger",
            )
            raise e
    else:
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(request, error["message"], extra_tags="danger")

    return (
        render(request, "games/upload.html", {"success": success})
        if success
        else redirect("games:upload")
    )


@login_required
def download(request: HttpRequest) -> HttpResponse:
    form = DownloadSubmissionForm(user=request.user, data=request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        submission = cd["script"]
        try:
            return FileResponse(
                submission.code.open("rb"),
                as_attachment=True,
                filename=f"{submission.get_submission_name()}.py",
            )
        except BaseException as e:
            messages.error(
                request, "Unable to download script, try again later", extra_tags="danger"
            )
            raise e
    else:
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(request, error["message"], extra_tags="danger")
    return redirect("games:upload")


def play(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            g = Game.objects.create(
                black=cd["black"],
                white=cd["white"],
                time_limit=cd["time_limit"],
                playing=True,
                last_heartbeat=timezone.now(),
            )
            logger.info(f"Created game with id: {g.id}")
            cd["black"], cd["white"] = cd["black"].id, cd["white"].id
            request.session["form-data"] = json.dumps(cd)
            return render(
                request,
                "games/board.html",
                {
                    "game": serialize_game_info(g),
                    "is_watching": False,
                },
            )
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    initial = json.loads(request.session.get("form-data", "{}"))
    return render(request, "games/design.html", {"form": GameForm(initial=initial)})


def watch(request: HttpRequest, game_id: Optional[int] = None) -> HttpResponse:
    if game_id is not None:
        return render(
            request,
            "games/board.html",
            {
                "game": serialize_game_info(get_object_or_404(Game, id=game_id)),
                "is_watching": True,
            },
        )
    return render(request, "games/watch_list.html", {"games": Game.objects.running()})


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "games/about.html")


def help_view(request: HttpRequest) -> HttpResponse:
    return render(request, "games/help.html")
