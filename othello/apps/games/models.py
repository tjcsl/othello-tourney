import os
import uuid
from typing import Any, AnyStr

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from ...moderator.constants import Player
from .validators import validate_game_time_limit

PLAYER_CHOICES = (
    (Player.BLACK.value, "Black"),
    (Player.WHITE.value, "White"),
)


def _save_path(instance, filename: str) -> AnyStr:
    return os.path.join(instance.user.username if instance.user else instance.name, f"{uuid.uuid4()}.py")


class SubmissionQuerySet(models.QuerySet):
    def latest(self, **kwargs: Any) -> "models.query.QuerySet[Submission]":
        """
        Returns a set of all the latest submissions for all users
        """
        return self.filter(**kwargs).distinct("user").order_by("user", "-tournament_win_year", "-created_at")


class Submission(models.Model):

    objects: Any = SubmissionQuerySet.as_manager()

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="submissions", null=True)
    name = models.CharField(max_length=500, null=True)
    created_at = models.DateTimeField(auto_now=True)
    code = models.FileField(upload_to=_save_path, default=None)

    is_legacy = models.BooleanField(default=False)
    tournament_win_year = models.IntegerField(default=-1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="user_or_name",
                check=models.Q(user__isnull=False) | models.Q(name__isnull=False),
            )
        ]

    def get_user_name(self) -> str:
        return self.user.short_name

    def get_user_username(self) -> str:
        return self.user.username

    def get_game_name(self) -> str:
        return (
            f"T-{self.tournament_win_year} {self.get_user_name()}"
            if self.tournament_win_year != -1
            else self.get_user_name() if self.user is not None else self.name
        )

    def get_submitted_time(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_submission_name(self) -> str:
        return f"{self.name}: <{self.get_submitted_time()}>"

    def __str__(self) -> str:
        return self.get_game_name()


class GameQuerySet(models.QuerySet):
    def running(self) -> "models.query.QuerySet[Game]":
        return self.filter(playing=True)

    def wins_for_user(self, submission: Submission) -> int:
        return (
            self.filter(playing=False, is_tournament=True)
            .filter(Q(white=submission, outcome=Player.WHITE.value) | Q(black=submission, outcome=Player.BLACK.value))
            .count()
        )


class Game(models.Model):

    OUTCOME_CHOICES = (
        (Player.BLACK.value, "black"),
        (Player.WHITE.value, "white"),
        ("T", "Tie"),
    )

    objects: Any = GameQuerySet.as_manager()
    created_at = models.DateTimeField(auto_now=True)

    black = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="black")
    white = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="white")
    time_limit = models.IntegerField(default=5, validators=[validate_game_time_limit])
    runoff = models.BooleanField(default=False)

    forfeit = models.BooleanField(default=False)
    outcome = models.CharField(max_length=1, choices=OUTCOME_CHOICES, default="T")
    score = models.IntegerField(default=0)

    is_tournament = models.BooleanField(default=False)
    playing = models.BooleanField(default=False)
    last_heartbeat = models.DateTimeField(default=timezone.now)

    @property
    def channels_group_name(self) -> str:
        return f"game-{self.id}"

    def __str__(self) -> str:
        return f"{self.black.user} (Black) vs {self.white.user} (White) [{self.time_limit}s]"

    def __repr__(self) -> str:
        return f"<Game: {self.black.user} vs {self.white.user}>"


class MoveSet(models.QuerySet):
    def latest(self) -> "models.query.QuerySet[Move]":
        return self.order_by("-created_at").first()


class Move(models.Model):

    objects: Any = MoveSet.as_manager()

    id = models.BigAutoField(primary_key=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.CharField(max_length=64, default="")
    player = models.CharField(max_length=1, choices=PLAYER_CHOICES)
    move = models.IntegerField(default=-10)

    possible = ArrayField(models.IntegerField(default=-1), default=list)

    def __str__(self) -> str:
        return f"{self.game}, {self.player}, {self.move}, {self.created_at}"


class GameObject(models.Model):

    id = models.BigAutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    player = models.CharField(max_length=1, choices=PLAYER_CHOICES)

    class Meta:
        abstract = True


class GameError(GameObject):

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="errors")
    error_code = models.IntegerField(default=0)
    error_msg = models.TextField(default="")


class GameLog(GameObject):

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="logs")
    message = models.TextField(default="")
