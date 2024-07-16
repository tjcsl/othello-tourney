import json
import logging
import sys
from datetime import datetime, timedelta

import pytz
from celery.result import AsyncResult
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..auth.decorators import management_only
from ..auth.models import User
from ..games.models import Game, Submission
from .forms import MultipleChoiceForm
from .models import Gauntlet, RankedManager
from .tasks import deleteAllRankedGames, runGauntlet

logger = logging.getLogger("othello")


def formatGameInfo(side, game):
    if not game or not side:
        return ""
    if game.playing:
        return "running"
    payload = f"Won" if game.outcome == side else "Fail (tie or loss)"
    return f"{payload}, Score: {abs(game.score) if game.outcome == side else -abs(game.score)}"


@login_required
def gauntlet(request: HttpRequest) -> HttpResponse:
    # print(Gauntlet.objects.all())
    # request.user.is_gauntlet_running = False
    # request.user.save()
    # Gauntlet.objects.all().delete()
    # request.user.is_superuser = True
    # #request.user.is_
    # request.user.save()
    # print(request.user.last_gauntlet_run, datetime.now(pytz.timezone('EST')))
    # print((datetime.now(pytz.timezone('EST')) - request.user.last_gauntlet_run).total_seconds())

    gauntlets = Gauntlet.objects.all().filter(user=request.user)
    if request.method == "GET":
        if not request.user.is_gauntlet_running:  # we don't have a gauntlet submitted, just render the default
            choice = Submission.objects.filter(user=request.user).order_by("-created_at").first().get_submission_name()
            return render(
                request,
                "rating/gauntlet.html",
                {
                    "recent_submission": f"Submission: {str(choice)}",
                    "last_gauntlet": gauntlets.first() if gauntlets else None,
                    "g1": formatGameInfo(gauntlets.first().mySide1 if gauntlets else None, gauntlets.first().game1 if gauntlets else None),
                    "g2": formatGameInfo(gauntlets.first().mySide2 if gauntlets else None, gauntlets.first().game2 if gauntlets else None),
                    "g3": formatGameInfo(gauntlets.first().mySide3 if gauntlets else None, gauntlets.first().game3 if gauntlets else None),
                },
            )
        else:  # we have a gauntlet submitted
            myGauntlet = gauntlets.filter(finished=False, user=request.user).order_by("created_at")
            if myGauntlet:
                myGauntlet = myGauntlet.first()
            else:
                return redirect("/rating/deleteGauntlet")  # something weird happened, delete everything

            inQueue = True  # lets check if the gauntlet is running, or just in queue
            if myGauntlet.running:
                inQueue = False

            return render(
                request,
                "rating/gauntletrunning.html",
                {
                    "queue": inQueue,
                    "g1": formatGameInfo(myGauntlet.mySide1, myGauntlet.game1),
                    "g2": formatGameInfo(myGauntlet.mySide2, myGauntlet.game2),
                    "g3": formatGameInfo(myGauntlet.mySide3, myGauntlet.game3),
                },
            )
    else:  # post request to submit a gauntlet
        # see if we have already have an unfinished gauntlet active
        if request.user.last_gauntlet_run and (datetime.now(pytz.timezone("EST")) - request.user.last_gauntlet_run).total_seconds() < 60:
            return render(request, "rating/throttle.html")
        request.user.is_gauntlet_running = True
        request.user.last_gauntlet_run = datetime.now(pytz.timezone("EST"))
        request.user.save()

        myGauntlet = gauntlets.filter(finished=False).order_by("created_at")
        if myGauntlet:  # we have already submitted a gauntlet, stop here
            return redirect("/rating/gauntlet")
        else:  # we create a new gauntlet
            pastGauntlet = Gauntlet.objects.filter(user=request.user)
            pastRating = 400
            if pastGauntlet.count() > 0:
                pastGauntlet = pastGauntlet.first()
                pastRating = max(400, pastGauntlet.submission.rating)
                pastGauntlet.game1.delete()
                pastGauntlet.game2.delete()
                pastGauntlet.game3.delete()
                pastGauntlet.delete()
                Gauntlet.objects.filter(user=request.user).delete()
                # a lot of delete redudancy

            # keep one gauntlet run saved. since we're making a new one, delete the old one
            submission = Submission.objects.filter(user=request.user).order_by("-created_at").first()

            # INSERT THE CORRECT GAUNTLET BOT HERE
            gauntletUser = User.objects.filter(username="warden").first()
            gauntletBot = Submission.objects.filter(user=gauntletUser).first()
            # ------------------------------------

            game1 = Game.objects.create(
                black=gauntletBot,
                white=gauntletBot,
                time_limit=5,
                playing=False,
                last_heartbeat=timezone.now(),
                runoff=False,
                is_gauntlet=True,
            )
            game2 = Game.objects.create(
                black=gauntletBot,
                white=gauntletBot,
                time_limit=5,
                playing=False,
                last_heartbeat=timezone.now(),
                runoff=False,
                is_gauntlet=True,
            )
            game3 = Game.objects.create(
                black=gauntletBot,
                white=gauntletBot,
                time_limit=5,
                playing=False,
                last_heartbeat=timezone.now(),
                runoff=False,
                is_gauntlet=True,
            )
            myGauntlet = Gauntlet.objects.create(user=request.user, submission=submission, game1=game1, game2=game2, game3=game3, pastRating=pastRating)
            if myGauntlet.mySide1 == "x":
                myGauntlet.game1.black = submission
            else:
                myGauntlet.game1.white = submission
            if myGauntlet.mySide2 == "x":
                myGauntlet.game2.black = submission
            else:
                myGauntlet.game2.white = submission
            if myGauntlet.mySide3 == "x":
                myGauntlet.game3.black = submission
            else:
                myGauntlet.game3.white = submission

            myGauntlet.game1.save()
            myGauntlet.game2.save()
            myGauntlet.game3.save()
            myGauntlet.save()

        gauntlets = Gauntlet.objects.all().filter(finished=False).order_by("created_at")
        if myGauntlet == gauntlets.first() and not myGauntlet.running:  # check if this gauntlet is the first one submitted, then we need to start running
            myGauntlet.running = True
            myGauntlet.save()
            # runGauntlet(request.user.id) #.delay(request.user.id)
            runGauntlet.delay(request.user.id)
            return redirect("/rating/gauntlet")

        return redirect("/rating/gauntlet")  # its just in queue


@login_required
def deleteGauntlet(request: HttpRequest) -> HttpResponse:
    request.user.is_gauntlet_running = False
    request.user.save()
    gauntlets = Gauntlet.objects.all().filter(user=request.user).order_by("-created_at")
    if gauntlets:
        AsyncResult(gauntlets.first().celery_task_id).revoke(terminate=True)
        gauntlets.first().game1.delete()
        gauntlets.first().game2.delete()
        gauntlets.first().game3.delete()
    gauntlets.delete()

    return redirect("/rating/gauntlet")


def history(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        games = list(Game.objects.filter(is_ranked=True, playing=False).order_by("-created_at"))

        return render(
            request,
            "rating/history.html",
            {"games": games},
        )

    return redirect("/")


def help(request: HttpRequest) -> HttpResponse:
    return render(request, "rating/help.html")


def standings(request: HttpRequest) -> HttpResponse:
    # Game.objects.all().delete()
    players = Submission.objects.rated()

    page_obj = Paginator(players, 10).get_page(request.GET.get("page", "1"))
    offset = 10 * (page_obj.number - 1)

    return render(
        request,
        "rating/standings.html",
        {"next_time": RankedManager.objects.first().next_auto_run, "players": players, "page_obj": page_obj, "offset": offset},
    )


@management_only
def manage(request: HttpRequest) -> HttpResponse:
    manager = RankedManager.objects.first()

    if request.method == "POST":
        form = MultipleChoiceForm(request.POST)
        if form.is_valid():
            selected_choice = form.cleaned_data["choices"]
            if selected_choice == "deletegames":
                deleteAllRankedGames()
            elif selected_choice == "deletegauntlets":
                Gauntlet.objects.all().delete()
            elif selected_choice == "disableauto":
                manager.auto_run = False
                manager.save()
            elif selected_choice == "enableauto":
                manager.auto_run = True
                manager.next_auto_run = getNextScrimTime()
                manager.save()
            elif selected_choice == "initranked":
                # create 1 single ranked manager object
                RankedManager.objects.all().delete()
                manager = RankedManager.objects.create(
                    auto_run=False,
                    running=False,
                    next_auto_run=timezone.now(),
                )

                # create scheduler that runs once a minute
                interval, _ = IntervalSchedule.objects.get_or_create(
                    every=60,
                    period=IntervalSchedule.SECONDS,
                )

                PeriodicTask.objects.all().delete()
                PeriodicTask.objects.create(
                    interval=interval,
                    name="RankedScheduler",
                    task="othello.apps.rating.tasks.rankedSchedulerProcess",
                )
                # celery -A othello beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
    else:
        form = MultipleChoiceForm()
    return render(request, "rating/manage.html", {"form": form, "manager": manager})
