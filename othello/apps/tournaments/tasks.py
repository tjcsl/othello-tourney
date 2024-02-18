import logging
from typing import List, Tuple

from celery import shared_task

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse_lazy

from ..games.models import Game
from ..games.tasks import Player, run_game
from .emails import email_send
from .models import Tournament, TournamentGame, TournamentPlayer
from .utils import chunks, get_updated_ranking
from .pairings import pair

logger = logging.getLogger("othello")


@shared_task
def tournament_notify_email(tournament_id: int):
    try:
        t = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist as e:
        logger.error(f"Trying to access tournament that does not exist {tournament_id}")
        raise e

    email_send(
        "emails/tournament_notify.txt",
        "emails/tournament_notify.html",
        {
            "start_time": t.start_time,
            "base_url": "https://othello.tjhsst.edu",
            "ranking_url": reverse_lazy("tournaments:current"),
            "dev_email": settings.DEVELOPER_EMAIL,
        },
        " Tournament is scheduled!",
        [x.user.email for x in t.include_users.all()],
        bcc=True,
    )


def tournament_start_email(tournament_id: int):
    try:
        t = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist as e:
        logger.error(f"Trying to access tournament that does not exist {tournament_id}")
        raise e
    admins = get_user_model().objects.filter(Q(is_teacher=True) | Q(is_staff=True) | Q(is_superuser=True))
    email_send(
        "emails/tournament_started.txt",
        "emails/tournament_started.html",
        {
            "base_url": "https://othello.tjhsst.edu",
            "ranking_url": reverse_lazy("tournaments:current"),
            "dev_email": settings.DEVELOPER_EMAIL,
        },
        " Tournament has started!",
        [x.user.email for x in t.include_users.all()] + [admin.email for admin in admins],
        bcc=True,
    )


@shared_task
def run_tournament_game(tournament_game_id: int) -> str:
    try:
        t_game = TournamentGame.objects.get(id=tournament_game_id)
    except TournamentGame.DoesNotExist as e:
        logger.error(f"Trying to run a tournament game that does not exist {tournament_game_id}")
        raise e

    game = t_game.game
    run_game(game.id)
    game.refresh_from_db()
    return game.outcome


@shared_task
def run_tournament(tournament_id: int) -> None:
    tournament_start_email(tournament_id)
    try:
        t = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist as e:
        logger.error(f"Trying to run tournament that does not exist {tournament_id}")
        raise e

    submissions: List[TournamentPlayer] = TournamentPlayer.objects.bulk_create([TournamentPlayer(tournament=t, submission=s) for s in t.include_users.all()])
    bye_player = TournamentPlayer.objects.create(tournament=t, submission=t.bye_player)

    for round_num in range(t.num_rounds):
        matches: List[Tuple[TournamentPlayer, ...]] = pair(submissions, bye_player)
        t.refresh_from_db()
        if t.terminated:
            t.delete()
            logger.info(f"Tournament {tournament_id} has been terminated")
            return
        t.played = round_num + 1
        t.save(update_fields=["played"])
        logger.warning(f"Tournament {tournament_id} Round {round_num+1} start")
        for match in matches:
            logger.warning(f"{match[0]}({match[0].ranking}) v. {match[1]}({match[1].ranking})")
        logger.info("\n")
        for round_matches in chunks(matches, settings.CONCURRENT_GAME_LIMIT):
            games = [
                t.games.create(
                    game=Game.objects.create(
                        black=game[0].submission,
                        white=game[1].submission,
                        time_limit=t.game_time_limit,
                        playing=True,
                        is_tournament=True,
                        runoff=t.runoff_enabled,
                    )
                )
                for game in round_matches
            ]
            tasks = {game: run_tournament_game.delay(game.id) for game in games}
            while len(tasks):
                finished_games = []
                for game, task in tasks.items():
                    if task.ready():
                        if task.result == Player.BLACK.value:
                            p = t.players.get(submission=game.game.black)
                            p.ranking += 1
                            p.save(update_fields=["ranking"])
                            tmp = "BLACK"
                        elif task.result == Player.WHITE.value:
                            p = t.players.get(submission=game.game.white)
                            p.ranking += 1
                            p.save(update_fields=["ranking"])
                            tmp = "WHITE"
                        else:
                            b, w = (
                                t.players.get(submission=game.game.black),
                                t.players.get(submission=game.game.white),
                            )
                            b.ranking += 0.5
                            w.ranking += 0.5
                            b.save(update_fields=["ranking"])
                            w.save(update_fields=["ranking"])
                            tmp = "TIE"
                        b, w = (
                            t.players.get(submission=game.game.black),
                            t.players.get(submission=game.game.white),
                        )
                        b.cumulative += get_updated_ranking(b)
                        w.cumulative += get_updated_ranking(w)
                        b.save(update_fields=["cumulative"])
                        w.save(update_fields=["cumulative"])
                        logger.warning(f"Tournament {tournament_id}, Round {round_num + 1}, {tmp}: {game.game.black} v. {game.game.white}")
                        finished_games.append(game)  # keep track of all finished games in auxiliary list

                for game in finished_games:  # need to use list to delete after iterating through dictionary
                    del tasks[game]  # cannot delete during dictionary iteration (edit while access error)
        logger.warning(f"Tournament {tournament_id}, Round {round_num+1} complete")

    t.finished = True
    t.save(update_fields=["finished"])
    logger.info(f"Tournament {tournament_id} has now finished, sending emails")

    winners: List[TournamentPlayer] = t.players.all().order_by("-ranking", "-cumulative")[:3]
    tournament_winner: TournamentPlayer = winners[0]
    for pos, winner in enumerate(winners):
        email_send(
            "emails/winner.txt",
            "emails/winner.html",
            {
                "name": winner.user.short_name,
                "rank": pos + 1,
                "base_url": "https://othello.tjhsst.edu",
                "ranking_url": reverse_lazy("tournaments:detail", kwargs={"tournament_id": tournament_id}),
                "dev_email": settings.DEVELOPER_EMAIL,
            },
            " Congratulations!",
            [winner.user.email],
        )
    email_send(
        "emails/tournament_finished.txt",
        "emails/tournament_finished.html",
        {
            "tournament_id": tournament_id,
            "start_time": t.start_time,
            "winners": [f"{x.user.get_full_name()} ({x.user.short_name})" for x in winners],
            "base_url": "https://othello.tjhsst.edu",
            "ranking_url": reverse_lazy("tournaments:detail", kwargs={"tournament_id": tournament_id}),
            "dev_email": settings.DEVELOPER_EMAIL,
        },
        " Tournament Completed",
        [x.email for x in get_user_model().objects.filter(Q(is_teacher=True) | Q(is_staff=True) | Q(is_superuser=True))],
    )
    tournament_winner.submission.tournament_win_year = t.start_time.year
    tournament_winner.submission.save(update_fields=["tournament_win_year"])
