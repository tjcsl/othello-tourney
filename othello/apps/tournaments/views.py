from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView

from ..auth.decorators import management_only
from .forms import TournamentCreateForm, TournamentManagementForm
from .models import *


class TournamentListView(ListView):
    model = Tournament
    template_name = "tournaments/previous.html"
    paginate_by = 10
    ordering = ["-start_time"]

    def get_queryset(self):
        return Tournament.objects.finished().order_by(*self.ordering)


def detail(request, tournament_id=None):
    t = Tournament.objects.in_progress()
    t = t[0] if t.exists() else None

    if tournament_id is not None:
        t = get_object_or_404(Tournament, id=tournament_id)

    players = sorted(t.players.all(), key=lambda x: -x.ranking) if t is not None else None

    page_obj = None
    if players is not None:
        paginator = Paginator(players, 10)
        page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "tournaments/detail.html",
        {"tournament": t, "players": players, "page_obj": page_obj},
    )


@management_only
def create(request):
    if request.method == "POST":
        form = TournamentCreateForm(request.POST)
        if form.is_valid():
            t = form.save()
            TournamentPlayer.objects.bulk_create(
                [
                    TournamentPlayer(tournament=t, submission=s)
                    for s in Submission.objects.latest(user_id__in=t.include_users.all())
                ]
            )
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
    if request.method == "POST":
        form = TournamentManagementForm(tournament, request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            if cd.get("terminate", False):
                tid = tournament.id
                if tournament in Tournament.objects.in_progress():
                    tournament.terminated = False
                    tournament.save(update_fields=["terminated"])
                else:
                    tournament.delete()
                messages.success(
                    request,
                    f"Tournament #{tid} has successfully been terminated",
                    extra_tags="success",
                )
                return redirect("tournaments:create")

            if time := cd.get("reschedule", False):
                tournament.start_time = time
            if num_rounds := cd.get("num_rounds", False):
                tournament.num_rounds = num_rounds
            if tl := cd.get("game_time_limit", False):
                tournament.game_time_limit = tl
            if bye_user := cd.get("bye_user", False):
                tournament.bye_player = bye_user
            if added_users := cd.get("add_users", False):
                tournament.include_users.set(tournament.include_users.all().union(added_users))
            if removed_users := cd.get("remove_users", False):
                tournament.include_users.set(
                    tournament.include_users.all().exclude(id__in=removed_users)
                )
            tournament.save()
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")

    if tournament in Tournament.objects.future():
        page_obj = Paginator(tournament.include_users.all(), 10).get_page(request.GET.get("page"))
    else:
        page_obj = Paginator(
            sorted(tournament.players.all(), key=lambda x: -x.ranking), 10
        ).get_page(request.GET.get("page"))
    return render(
        request,
        "tournaments/manage.html",
        {
            "tournament": tournament,
            "players": page_obj,
            "form": TournamentManagementForm(tournament),
            "future": tournament in Tournament.objects.future(),
        },
    )
