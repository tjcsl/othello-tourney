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
    PAIRING_ALGORITHMS = (
        ("random", "Random"),
        ("swiss", "Swiss"),
        ("danish", "Danish"),
        ("round_robin", "Round Robin"),
    )

    objects: Any = TournamentSet().as_manager()

    created_at = models.DateTimeField(auto_now=True)

    start_time = models.DateTimeField()
    include_users = models.ManyToManyField(Submission, blank=True)
    game_time_limit = models.IntegerField(default=1, validators=[validate_game_time_limit])
    num_rounds = models.IntegerField(default=15, validators=[validate_tournament_rounds])
    played = models.IntegerField(default=0)
    runoff_enabled = models.BooleanField(default=False)
    bye_player = models.ForeignKey(
        Submission,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="bye",
        default=None,
    )
    pairing_algorithm = models.CharField(
        choices=PAIRING_ALGORITHMS,
        default="swiss",
        max_length=20,
    )
    round_robin_matches = models.IntegerField(
        default=2,
        help_text="How many matches to play between two players in a round robin tournament",
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
    ranking = models.FloatField(default=0)
    cumulative = models.FloatField(default=0)

    @property
    def user(self):
        return self.submission.user

    def __str__(self) -> str:
        return self.submission.get_game_name()


class TournamentGame(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, null=False, blank=False, related_name="games"
    )

    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.tournament!s} - {self.game.black.get_user_name()} v. {self.game.white.get_user_name()}"
