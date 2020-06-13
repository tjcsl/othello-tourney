from celery import shared_task

from ..games.models import Submission
from ..games.tasks import Player, run_game
from .models import Tournament, TournamentGame, TournamentPlayer
from .utils import make_pairings


@shared_task
def run_tournament_game(tournament_game_id):
    try:
        t_game = TournamentGame.objects.get(id=tournament_game_id)
    except TournamentGame.DoesNotExist:
        return

    game = t_game.game
    run_game(game.id)


@shared_task
def run_tournament(tournament_id):
    try:
        t = Tournament.objects.get(id=tournament_id)
    except Tournament.DoesNotExist:
        return

    submissions = TournamentPlayer.objects.bulk_create(
        [
            TournamentPlayer(tournament=t, submission=s)
            for s in Submission.objects.latest(user_id__in=t.include_users.all())
        ]
    )

    matches = make_pairings(submissions, t.bye_player)

