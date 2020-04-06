from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import FormView

from .forms import SubmissionForm, GameForm


def play(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            return HttpResponse("got form")
    return render(request, "games/design.html", {'form': GameForm()})


class UploadView(FormView):
    template_name, form_class = "games/upload.html", SubmissionForm

    def form_valid(self, form):
        try:
            submission = form.save(commit=False)
            submission.user = self.request.user
            submission.save()
            success = True
        except BaseException as e:
            print(e)
            success = False
        return render(self.request, 'games/upload_complete.html', {'success': success})
