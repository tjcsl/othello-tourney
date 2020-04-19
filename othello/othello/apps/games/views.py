from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.views.generic.edit import View

from .tasks import run_game
from .models import Game, Submission
from .forms import SubmissionForm, GameForm, WatchForm, ChangeSubmissionForm


class UploadView(View):
    template_name = "games/upload.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                'success': False,
                'submission_form': SubmissionForm(),
                'change_form': ChangeSubmissionForm(request.user)
            }
        )

    def post(self, request):
        action, success = request.POST.get("action", False), False

        if action == "new_submission":
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    submission = form.save(commit=False)
                    submission.user = request.user
                    submission.save()
                    success = True
                except:
                    messages.error(request, "Unable to upload script at this time, try again later", extra_tags="danger")
            else:
                for error in form.errors.get_json_data()["__all__"]:
                    messages.error(request, error["message"], extra_tags="danger")

        elif action == "change_submission":
            form = ChangeSubmissionForm(user=request.user, data=request.POST)
            if form.is_valid():
                try:
                    form.cleaned_data.get("new_script", False).set_usable()
                    success = True
                except:
                    messages.error(request, "Unable to set script as running script, try again later", extra_tags="danger")
            else:
                messages.error(request, "Unable to set script as running script, try again later", extra_tags="danger")

        elif action == "download_submission":
            form = ChangeSubmissionForm(user=request.user, data=request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                submission = cd["new_script"]
                if submission in Submission.objects.get_all_submissions_for_user(request.user):
                    try:
                        return FileResponse(submission.code.open('rb'), as_attachment=True, filename=f"{submission.get_submission_name()}.py")
                    except BaseException as e:
                        messages.error(request, "Unable to download script, try again later", extra_tags="danger")
                        raise e
                else:
                    messages.error(request, "Cannot access specified submission", extra_tags="danger")
            else:
                for error in form.errors.get_json_data()["__all__"]:
                    messages.error(request, error["message"], extra_tags="danger")

        else:
            messages.error(request, "Received invalid request", extra_tags="danger")

        if not success:
            return redirect("games:upload")
        else:
            return render(request, self.template_name, {'success': success})


def play(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            g, created = Game.objects.get_or_create(
                black=cd['black'],
                white=cd['white'],
                time_limit=cd['time_limit'],
                playing=True
            )
            run_game.delay(g.id)
            return render(request, "games/play.html", {'game': model_to_dict(g), 'is_watching': False})
        else:
            messages.error(request, "Unable to start game, try again later", extra_tags="danger")
    return render(request, "games/design.html", {'form': GameForm()})


def watch(request):
    if request.method == "POST":
        return render(request, "games/watch.html")
    return render(request, "games/watch_list.html", {'form': WatchForm()})
