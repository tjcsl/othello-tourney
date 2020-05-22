import json

from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import FileResponse

from .models import Game
from .utils import serialize_game_info
from ..auth.decorators import login_required
from .forms import SubmissionForm, GameForm, DownloadSubmissionForm


@login_required
def upload(request):
    if request.method == "GET":
        return render(request, "games/upload.html", {'success': False, 'submission_form': SubmissionForm(),
                                                     'change_form': DownloadSubmissionForm(request.user)})
    action, success = request.POST.get("action", False), False
    if action == "new_submission":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                submission = form.save(commit=False)
                submission.user = request.user
                submission.save()
                success = True
            except BaseException as e:
                messages.error(request, "Unable to upload script at this time, try again later", extra_tags="danger")
                raise e
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    elif action == "download_submission":
        form = DownloadSubmissionForm(user=request.user, data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            submission = cd["script"]
            try:
                return FileResponse(submission.code.open('rb'), as_attachment=True,
                                    filename=f"{submission.get_submission_name()}.py")
            except BaseException as e:
                messages.error(request, "Unable to download script, try again later", extra_tags="danger")
                raise e
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    else:
        messages.error(request, "Received invalid request", extra_tags="danger")

    return render(request, "games/upload.html", {'success': success}) if success else redirect("games:upload")


def play(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            g = Game.objects.create(
                black=cd['black'],
                white=cd['white'],
                time_limit=cd['time_limit'],
                playing=True,
                ping=True,
            )
            cd['black'], cd['white'] = cd['black'].id, cd['white'].id
            request.session["form-data"] = json.dumps(cd)
            return render(request, "games/board.html",
                          {'game': serialize_game_info(g), 'is_watching': False})
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    initial = json.loads(request.session.get("form-data", "{}"))
    return render(request, "games/design.html", {'form': GameForm(initial=initial)})


def watch(request, game_id=False):
    if game_id:
        return render(
            request, "games/board.html", {
                'game': serialize_game_info(Game.objects.get(id=game_id)),
                'is_watching': True}
        )
    return render(request, "games/watch_list.html", {'games': Game.objects.running()})
