from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

from .models import Tournament
from ..auth.decorators import *
from .forms import TournamentForm


class TournamentListView(ListView):
    model = Tournament
    template_name = 'tournaments/previous.html'
    paginate_by = 10
    ordering = ['-start_time']

    def get_queryset(self):
        return Tournament.objects.finished().order_by(*self.ordering)


def detail(request, tournament_id=None):
    if tournament_id:
        return HttpResponse(get_object_or_404(Tournament, id=tournament_id))
    return HttpResponse("current")


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
