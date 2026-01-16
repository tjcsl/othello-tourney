from typing import Optional

from celery.result import AsyncResult

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.list import ListView

from ..auth.decorators import management_only
from .forms import TournamentCreateForm, TournamentManagementForm
from .models import Tournament
from .tasks import run_tournament, tournament_notify_email


class TournamentListView(ListView):
    model = Tournament
    template_name = "tournaments/previous.html"
    paginate_by = 10
    ordering = ["-start_time"]

    def get_queryset(self):
        return Tournament.objects.filter_finished().order_by(*self.ordering)


def detail(request: HttpRequest, tournament_id: Optional[int] = None) -> HttpResponse:
    if tournament_id is not None:
        t = get_object_or_404(Tournament, id=tournament_id)
    else:
        t = Tournament.objects.filter_in_progress().last()

    if t is not None:
        players = t.players.exclude(submission=t.bye_player).order_by("-ranking", "-cumulative")
        page_obj = Paginator(players, 10).get_page(request.GET.get("page", "1"))
        offset = 10 * (page_obj.number - 1)
    else:
        players = None
        page_obj = None
        offset = 0

    return render(
        request,
        "tournaments/detail.html",
        {"tournament": t, "players": players, "page_obj": page_obj, "offset": offset},
    )


@management_only
def create(request: HttpRequest) -> HttpResponse:
    form = TournamentCreateForm()
    if request.method == "POST":
        form = TournamentCreateForm(request.POST)
        if form.is_valid():
            try:
                t = form.save()
                cd = form.cleaned_data
                task = run_tournament.apply_async([t.id], eta=t.start_time)
                t.celery_task_id = task.id
                t.save(update_fields=["celery_task_id"])
                messages.success(
                    request,
                    f"Successfully created tournament! Tournament is scheduled to run at {t.start_time}",
                    extra_tags="success",
                )
                if cd.get("using_legacy", False):
                    messages.warning(
                        request,
                        "Warning: One of more participating users is using legacy code! "
                        "If this was a mistake, you can delete the Tournament and recreate it.",
                        extra_tags="warning",
                    )
                tournament_notify_email.delay(t.id)
            except Exception as e:
                messages.error(
                    request,
                    "An unexpected error occurred when trying to create a tournament, try again later",
                    extra_tags="danger",
                )
                raise e
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    return render(
        request,
        "tournaments/create.html",
        {
            "form": form,
            "in_progress": Tournament.objects.filter_in_progress().filter(terminated=False),
            "future": Tournament.objects.filter_future(),
        },
    )


@management_only
def management(request: HttpRequest, tournament_id: Optional[int] = None) -> HttpResponse:
    tournament = get_object_or_404(Tournament, id=tournament_id)
    if request.method == "POST":
        form = TournamentManagementForm(tournament, request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd.get("terminate", False):
                tid = tournament.id
                if tournament in Tournament.objects.filter_in_progress():
                    tournament.terminated = True
                    tournament.save(update_fields=["terminated"])
                else:
                    tournament.delete()
                messages.success(
                    request,
                    f"Tournament #{tid} has successfully been terminated",
                    extra_tags="success",
                )
                return redirect("tournaments:create")

            if time := cd.get("reschedule", None):
                AsyncResult(tournament.celery_task_id).revoke()
                tournament.start_time = time
                task = run_tournament.apply_async([tournament.id], eta=time)
                tournament_notify_email.delay(tournament.id)
                tournament.celery_task_id = task.id
            if num_rounds := cd.get("num_rounds", None):
                tournament.num_rounds = num_rounds
            if tl := cd.get("game_time_limit", None):
                tournament.game_time_limit = tl
            if bye_user := cd.get("bye_user", None):
                tournament.bye_player = bye_user
            if added_users := cd.get("add_users", None):
                tournament.include_users.set(tournament.include_users.all().union(added_users))
            if removed_users := cd.get("remove_users", None):
                if tournament in Tournament.objects.filter_in_progress():
                    tournament.players.filter(id__in=removed_users).delete()
                else:
                    tournament.include_users.set(tournament.include_users.all().exclude(id__in=removed_users))
            tournament.save()
            if cd.get("reschedule", None):
                tournament_notify_email(tournament.id)
            messages.success(
                request,
                "Successfully made changes to tournament!",
                extra_tags="success",
            )
            if cd.get("using_legacy", False):
                messages.warning(
                    request,
                    "Warning: One of more participating users is using legacy code!" " If this was a mistake, you can delete the Tournament and recreate it.",
                    extra_tags="warning",
                )
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")

    if tournament in Tournament.objects.filter_future():
        page_obj = Paginator(tournament.include_users.all(), 10).get_page(request.GET.get("page", 1))
    else:
        page_obj = Paginator(tournament.players.all().order_by("-ranking"), 10).get_page(request.GET.get("page", 1))

    return render(
        request,
        "tournaments/manage.html",
        {
            "tournament": tournament,
            "num_players": tournament.include_users.count(),
            "players": page_obj,
            "form": TournamentManagementForm(tournament),
            "future": tournament in Tournament.objects.filter_future(),
            "bye_player": tournament.bye_player,
            "offset": 10 * (page_obj.number - 1),
        },
    )


def help_view(request: HttpRequest) -> HttpResponse:
    return render(request, "tournaments/help.html")
