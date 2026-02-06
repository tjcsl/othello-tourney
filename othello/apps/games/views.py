import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import models
from django.http import FileResponse, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import formats, timezone

from .forms import DownloadSubmissionForm, GameForm, MatchForm, SubmissionForm
from .models import Game, Match, Submission
from .tasks import run_match
from .utils import serialize_game_info

logger = logging.getLogger("othello")


@login_required
def upload(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(
            request,
            "games/upload.html",
            {
                "success": False,
                "submission_form": SubmissionForm(user=request.user),
                "download_form": DownloadSubmissionForm(request.user),
            },
        )
    success = False
    form = SubmissionForm(user=request.user, data=request.POST, files=request.FILES)
    if form.is_valid():
        try:
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            success = True
        except BaseException as e:
            messages.error(
                request,
                "Unable to upload script at this time, try again later",
                extra_tags="danger",
            )
            raise e
    else:
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(request, error["message"], extra_tags="danger")

    return (
        render(request, "games/upload.html", {"success": success})
        if success
        else redirect("games:upload")
    )


@login_required
def download(request: HttpRequest) -> HttpResponse | FileResponse:
    form = DownloadSubmissionForm(user=request.user, data=request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        submission = cd["script"]
        try:
            return FileResponse(
                submission.code.open("rb"),
                as_attachment=True,
                filename=f"{submission.get_submission_name()}.py",
            )
        except BaseException as e:
            messages.error(
                request, "Unable to download script, try again later", extra_tags="danger"
            )
            raise e
    else:
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(request, error["message"], extra_tags="danger")
    return redirect("games:upload")


def play(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            g = Game.objects.create(
                black=cd["black"],
                white=cd["white"],
                time_limit=cd["time_limit"],
                playing=True,
                last_heartbeat=timezone.now(),
                runoff=cd["runoff"],
            )
            logger.info(f"Created game with id: {g.id}")
            cd["black"], cd["white"] = cd["black"].id, cd["white"].id
            request.session["form-data"] = json.dumps(cd)
            return render(
                request,
                "games/board.html",
                {
                    "game": serialize_game_info(g),
                    "is_watching": False,
                },
            )
        else:
            for errors in form.errors.get_json_data().values():
                for error in errors:
                    messages.error(request, error["message"], extra_tags="danger")
    initial = json.loads(request.session.get("form-data", "{}"))
    return render(request, "games/design.html", {"form": GameForm(initial=initial)})


@login_required
def request_match(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        messages.error(request, "Method not allowed")
        return redirect("games:queue")

    form = MatchForm(request.user, request.POST)
    if form.is_valid():
        cd = form.cleaned_data

        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        recent_games = (
            Match.objects.filter(
                models.Q(player1__user=request.user) | models.Q(player2__user=request.user),
                created_at__gte=one_hour_ago,
            ).aggregate(total_games=models.Sum("num_games"))["total_games"]
            or 0
        )
        if recent_games + cd["num_games"] > 100:
            messages.error(
                request,
                "You have exceeded the limit of 100 games per hour.",
                extra_tags="danger",
            )
            return redirect("games:queue")

        user_submission = Submission.objects.filter(user=request.user).latest(onesub=True)
        if not user_submission:
            messages.error(request, "Could not request match because you do not have a submission")
            return redirect("games:queue")

        opponent_user = cd["opponent"].user
        if cd["is_ranked"] and not opponent_user.accept_ranked_matches:
            messages.error(
                request, f"{opponent_user.username} does not accept ranked match requests."
            )
            return redirect("games:queue")
        elif not cd["is_ranked"] and not opponent_user.accept_unranked_matches:
            messages.error(
                request, f"{opponent_user.username} does not accept unranked match requests."
            )
            return redirect("games:queue")

        match = Match.objects.create(
            player1=user_submission,
            player2=cd["opponent"],
            num_games=cd["num_games"],
            is_ranked=cd["is_ranked"],
        )
        run_match.delay(match.id)
        messages.success(request, f"Match requested against {cd['opponent'].get_game_name()}.")
        return redirect("games:queue")
    else:
        for errors in form.errors.get_json_data().values():
            for error in errors:
                messages.error(request, error["message"], extra_tags="danger")

    return redirect("games:queue")


@login_required
def queue_json(request: HttpRequest) -> HttpResponse:
    matches = Match.objects.all().order_by("-created_at")
    my_matches_only = request.GET.get("my_matches") == "1"
    if my_matches_only:
        matches = matches.filter(
            models.Q(player1__user=request.user) | models.Q(player2__user=request.user)
        )
    paginator = Paginator(matches, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    matches_data = []
    for match in page_obj:
        matches_data.append(
            {
                "id": match.id,
                "player1_name": match.player1.user.username,
                "player2_name": match.player2.user.username,
                "score": f"{match.player1_wins} - {match.ties} - {match.player2_wins}"
                if match.status == "completed"
                else "-",
                "is_ranked": "Yes" if match.is_ranked else "No",
                "status": match.status,
                "status_display": match.get_status_display(),
                "created_at": formats.date_format(
                    timezone.localtime(match.created_at),
                    "DATETIME_FORMAT",
                ),
                "can_view_replay": request.user in [match.player1.user, match.player2.user],
                "player1_rating_delta": match.player1_rating_delta
                if match.player1_rating_delta
                else None,
                "player2_rating_delta": match.player2_rating_delta
                if match.player2_rating_delta
                else None,
            }
        )

    return JsonResponse(
        {
            "matches": matches_data,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "page_number": page_obj.number,
        }
    )


@login_required
def queue(request: HttpRequest) -> HttpResponse:
    matches = Match.objects.all().order_by("-created_at")
    my_matches_only = request.GET.get("my_matches") == "1"
    if my_matches_only and request.user.is_authenticated:
        matches = matches.filter(
            models.Q(player1__user=request.user) | models.Q(player2__user=request.user)
        )
    paginator = Paginator(matches, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "games/queue.html",
        {"page_obj": page_obj, "my_matches_only": my_matches_only, "request": request},
    )


def watch(request: HttpRequest, game_id: int | None = None) -> HttpResponse:
    if game_id is not None:
        return render(
            request,
            "games/board.html",
            {
                "game": serialize_game_info(get_object_or_404(Game, id=game_id)),
                "is_watching": True,
            },
        )
    return render(request, "games/watch_list.html", {"games": Game.objects.all()})


def replay(request: HttpRequest) -> HttpResponse:
    return render(request, "games/replay.html")


@login_required
def match_replay(request: HttpRequest, match_id: int) -> HttpResponse:
    match = get_object_or_404(Match, id=match_id)
    if request.user not in [match.player1.user, match.player2.user]:
        messages.error(
            request,
            "You can only view replays of matches you participated in.",
            extra_tags="danger",
        )
        return redirect("games:queue")
    games = list(match.games.order_by("created_at"))
    selected_game_id = request.GET.get("game_id")
    if selected_game_id:
        selected_game = get_object_or_404(Game, id=selected_game_id, match=match)
    elif games:
        selected_game = games[0]
    else:
        selected_game = None

    game_data = serialize_game_info(selected_game) if selected_game else None

    return render(
        request,
        "games/match_replay.html",
        {
            "match": match,
            "games": games,
            "selected_game": selected_game,
            "game_data": game_data,
        },
    )


def about(request: HttpRequest) -> HttpResponse:
    return render(request, "games/about.html")


def help_view(request: HttpRequest) -> HttpResponse:
    return render(request, "games/help.html")
