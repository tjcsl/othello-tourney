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
            success = True
        except BaseException as e:
            print(e)
            success = False
        return render(self.request, 'games/upload_complete.html', {'success': success})
