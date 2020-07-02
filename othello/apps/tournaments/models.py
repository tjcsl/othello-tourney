from typing import Any

from django.db import models
from django.utils.timezone import now

from ..games.models import Game, Submission
from ..games.validators import validate_game_time_limit
from .validators import validate_tournament_rounds


class TournamentSet(models.QuerySet):
    def filter_finished(self) -> "models.query.QuerySet[Tournament]":
        return self.filter(finished=True)

    def filter_in_progress(self) -> "models.query.QuerySet[Tournament]":
        return self.filter(start_time__lte=now(), finished=False)

    def filter_future(self) -> "models.query.QuerySet[Tournament]":
        return self.filter(start_time__gt=now())


class Tournament(models.Model):

    objects: Any = TournamentSet().as_manager()

    created_at = models.DateTimeField(auto_now=True)

    start_time = models.DateTimeField()
    include_users = models.ManyToManyField(Submission, blank=True)
    game_time_limit = models.IntegerField(default=1, validators=[validate_game_time_limit])
    num_rounds = models.IntegerField(default=15, validators=[validate_tournament_rounds])
    played = models.IntegerField(default=0)
    bye_player = models.ForeignKey(
        Submission,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="bye",
        default=None,
    )

    finished = models.BooleanField(default=False)
    terminated = models.BooleanField(default=False)
    celery_task_id = models.CharField(max_length=48, default="")

    def __str__(self) -> str:
        return "Tournament at {}".format(self.start_time.strftime("%Y-%m-%d %H:%M:%S"))

    def __repr__(self) -> str:
        return "<Tournament @ {}, {}>".format(
            self.start_time.strftime("%Y-%m-%d %H:%M:%S"), self.finished
        )


class TournamentPlayer(models.Model):

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="players")
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    ranking = models.DecimalField(default=0, decimal_places=1, max_digits=15)

    def __str__(self) -> str:
        return self.submission.get_game_name()


class TournamentGame(models.Model):

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, null=False, blank=False, related_name="games"
    )

    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return f"{str(self.tournament)} - {self.game.black.get_user_name()} v. {self.game.white.get_user_name()}"
