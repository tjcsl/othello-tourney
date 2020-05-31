from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

from ..auth.decorators import management_only
from .forms import TournamentCreateForm
from .models import Tournament


class TournamentListView(ListView):
    model = Tournament
    template_name = "tournaments/previous.html"
    paginate_by = 10
    ordering = ["-start_time"]

    def get_queryset(self):
        return Tournament.objects.finished().order_by(*self.ordering)


def detail(request, tournament_id=None):
    if tournament_id:
        return HttpResponse(get_object_or_404(Tournament, id=tournament_id))
    return HttpResponse("current")


@management_only
def create(request):
    if request.method == "POST":
        form = TournamentCreateForm(request.POST)
        if form.is_valid():
            t = form.save()
            messages.success(
                request,
                f"Successfully created tournament! Tournament is scheduled to run at {t.start_time}",
                extra_tags="success",
            )
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    return render(
        request,
        "tournaments/create.html",
        {
            "form": TournamentCreateForm(),
            "in_progress": Tournament.objects.in_progress(),
            "future": Tournament.objects.future(),
        },
    )


@management_only
def management(request, tournament_id=None):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return HttpResponse(tournament)
