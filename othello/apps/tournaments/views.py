from django.contrib import messages
from django.shortcuts import render

from ..auth.decorators import *
from .forms import TournamentForm


@management_only
def management(request):
    if request.method == "POST":
        form = TournamentForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(
                request,
                f"Successfully created tournament! Tournament is scheduled to run at {t.start_time}",
                extra_tags="success"
            )
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    return render(request, "tournaments/create.html", {'form': TournamentForm()})


