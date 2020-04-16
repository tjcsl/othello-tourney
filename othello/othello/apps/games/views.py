from django.contrib import messages
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.views.generic.edit import View

from .models import Game
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
                messages.error(request, "Unable to upload script at this time, try again later", extra_tags="danger")

        elif action == "change_submission":
            form = ChangeSubmissionForm(request.user, request.POST)
            if form.is_valid():
                try:
                    form.cleaned_data.get("new_script", False).set_usable()
                    success = True
                except BaseException as e:
                    messages.error(request, "Unable to set script as running script, try again later", extra_tags="danger")
                    raise e
            else:
                messages.error(request, "Unable to set script as running script, try again later", extra_tags="danger")

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
            return render(request, "games/play.html", {'game': model_to_dict(g), 'is_watching': False})
        else:
            messages.error(request, "Unable to start game, try again later", extra_tags="danger")
    return render(request, "games/design.html", {'form': GameForm()})


def watch(request):
    if request.method == "POST":
        return render(request, "games/watch.html")
    return render(request, "games/watch_list.html", {'form': WatchForm()})
