import os
from django.conf import settings
from django.shortcuts import render
from django.views.generic.edit import FormView

from .forms import UploadFileForm


def about(request):
    return render(request, "games/about.html")


def help(request):
    return render(request, "games/help.html")


class UploadView(FormView):
    template_name = "games/upload.html"
    form_class = UploadFileForm

    def form_valid(self, form):
        if self.handle_form(form.cleaned_data.get('code', False)):
            return render(self.request, 'games/upload_complete.html', self.get_context_data())
        return render(self.request, 'games/upload_error.html', self.get_context_data())

    def handle_form(self, file):
        if not file:
            return False
        fdir = os.path.join(settings.MEDIA_ROOT, self.request.user.username)
        try:
            os.makedirs(fdir, mode=0o755, exist_ok=True)
            with open(os.path.join(fdir, 'strategy.py'), 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        except IOError:
            return False
