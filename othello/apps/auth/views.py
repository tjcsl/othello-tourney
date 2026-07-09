import json
import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..games.forms import MatchForm
from ..games.models import RatingHistory, Submission

logger = logging.getLogger("othello")


def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        user = request.user
        history = RatingHistory.objects.filter(user=user).order_by("changed_at")
        ratings = [float(i) for i in history.values_list("rating", flat=True)]
        dates = [h.changed_at.strftime("%Y-%m-%d %H:%M") for h in history]
        return render(
            request,
            "auth/index.html",
            {
                "current_rating": user.rating,
                "ratings_json": json.dumps(ratings),
                "dates_json": json.dumps(dates),
                "accept_ranked_matches": user.accept_ranked_matches,
                "accept_unranked_matches": user.accept_unranked_matches,
            },
        )
    return render(request, "auth/index.html")


def login(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/login.html")


def error(request: HttpRequest) -> HttpResponse:
    return render(request, "auth/error.html")


@login_required
def rating(request: HttpRequest) -> HttpResponse:
    user = request.user
    history = RatingHistory.objects.filter(user=user).order_by("changed_at")
    ratings = list(history.values_list("rating", flat=True))
    dates = list(history.values_list("changed_at", flat=True))
    return render(
        request,
        "auth/rating.html",
        {
            "current_rating": user.rating,
            "ratings": ratings,
            "dates": [d.isoformat() for d in dates],
        },
    )


@login_required
def profile(request: HttpRequest, username: str) -> HttpResponse:
    profile_user = get_object_or_404(get_user_model(), username=username)

    history = RatingHistory.objects.filter(user=profile_user).order_by("changed_at")

    ratings = [float(i) for i in history.values_list("rating", flat=True)]
    dates = [h.changed_at.strftime("%Y-%m-%d %H:%M") for h in history]

    return render(
        request,
        "auth/profile.html",
        {
            "profile_user": profile_user,
            "current_rating": profile_user.rating,
            "ratings_json": json.dumps(ratings),
            "dates_json": json.dumps(dates),
        },
    )


@login_required
def rankings(request: HttpRequest) -> HttpResponse:
    users = get_user_model().objects.order_by("-rating").exclude(username="Yourself")
    paginator = Paginator(users, 25)  # Show 25 users per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    form = MatchForm(request.user)
    users_with_submissions = set(
        Submission.objects.values_list("user__username", flat=True).distinct()
    ) - {request.user.username, "Yourself"}
    return render(
        request,
        "auth/rankings.html",
        {
            "page_obj": page_obj,
            "form": form,
            "users_with_submissions": users_with_submissions,
        },
    )


@login_required
def update_preferences(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        accept_ranked = request.POST.get("accept_ranked_matches") == "true"
        accept_unranked = request.POST.get("accept_unranked_matches") == "true"
        request.user.accept_ranked_matches = accept_ranked
        request.user.accept_unranked_matches = accept_unranked
        request.user.save(update_fields=["accept_ranked_matches", "accept_unranked_matches"])
        messages.success(request, "Preferences updated successfully.")
    return redirect("auth:index")
