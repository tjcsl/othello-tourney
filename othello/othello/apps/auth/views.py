from django.shortcuts import render
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse

from .forms import UploadFileForm


def index(request):
    return render(request, "auth/index.html")


def login(request):
    return render(request, "auth/login.html")


def about(request):
    return render(request, "auth/about_uploading.html")


@login_required
def upload(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            return render(request, "auth/upload_complete.html")
    return render(request, "auth/upload.html", {'form': UploadFileForm()})


logout = LogoutView.as_view()
