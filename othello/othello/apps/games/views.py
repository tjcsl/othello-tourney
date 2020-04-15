from django.contrib import messages
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.views.generic.edit import View, FormView

from ..auth.decorators import login_required

from .models import Game
from .forms import SubmissionForm, GameForm, WatchForm, ChangeSubmissionForm


class UploadView(FormView):
    template_name, form_class = "games/upload.html", SubmissionForm

    def form_valid(self, form):
        try:
            submission = form.save(commit=False)
            submission.user = self.request.user
            submission.save()
            success = True
        except:
            messages.error(self.request, "Unable to upload AI, try again later", extra_tags="danger")
            success = False
        return render(self.request, "games/upload.html", {'success': success})

    def form_invalid(self, form):
        for error in form.errors.get_json_data()["__all__"]:
            messages.error(self.request, error["message"], extra_tags="danger")
        return render(self.request, "games/upload.html", {'success': False})


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
