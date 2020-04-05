import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic.edit import FormView

from .forms import SubmissionForm


def about(request):
    return render(request, "games/about.html")


def help(request):
    return render(request, "games/help.html")


class UploadView(FormView):
    template_name, form_class = "games/upload.html", SubmissionForm

    def form_valid(self, form):
        try:
            submission = form.save(commit=False)
            submission.user = self.request.user
            submission.save()
        except BaseException as e:
            print(e)
            return render(self.request, 'games/upload_error.html', self.get_context_data())
        return render(self.request, 'games/upload_complete.html', self.get_context_data())
