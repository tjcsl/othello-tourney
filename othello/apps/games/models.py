import os
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from ...moderator.constants import Player

PLAYER_CHOICES = (
    (Player.BLACK.value, "Black"),
    (Player.WHITE.value, "White"),
)


def _save_path(instance, filename):
    return os.path.join(instance.user.short_name, f"{uuid.uuid4()}.py")


class SubmissionQuerySet(models.QuerySet):
    def latest(self, **kwargs):
        """
        Returns a set of all the latest submissions for all users
        """
        return self.filter(**kwargs).order_by("user", "-created_at").distinct("user")


class Submission(models.Model):

    objects = SubmissionQuerySet.as_manager()

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="user")
    name = models.CharField(max_length=500, default="")
    created_at = models.DateTimeField(auto_now=True)
    code = models.FileField(upload_to=_save_path, default=None)

    is_legacy = models.BooleanField(default=False)
    tournament_win_year = models.IntegerField(default=-1)

    def get_user_name(self):
        return self.user.short_name

    def get_game_name(self):
        return (
            f"T-{self.tournament_win_year} {self.get_user_name()}"
            if self.tournament_win_year != -1
            else self.get_user_name()
        )

    def get_submitted_time(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")

    def get_submission_name(self):
        return f"{self.name}: <{self.get_submitted_time()}>"

    def __str__(self):
        return self.get_game_name()


class GameQuerySet(models.QuerySet):
    def running(self):
        return self.filter(playing=True)

    def wins_for_user(self, submission):
        return (
            self.filter(playing=False, is_tournament=True)
            .filter(
                Q(white=submission, outcome=Player.WHITE.value)
                | Q(black=submission, outcome=Player.BLACK.value)
            )
            .count()
        )


class Game(models.Model):

    OUTCOME_CHOICES = (
        (Player.BLACK.value, "black"),
        (Player.WHITE.value, "white"),
        ("T", "Tie"),
    )

    objects = GameQuerySet.as_manager()
    created_at = models.DateTimeField(auto_now=True)

    black = models.ForeignKey(Submission, on_delete=models.PROTECT, related_name="black")
    white = models.ForeignKey(Submission, on_delete=models.PROTECT, related_name="white")
    time_limit = models.IntegerField(
        default=5, validators=[MaxValueValidator(settings.MAX_TIME_LIMIT), MinValueValidator(1)]
    )

    forfeit = models.BooleanField(default=False)
    outcome = models.CharField(max_length=1, choices=OUTCOME_CHOICES, default="T")
    score = models.IntegerField(default=0)

    is_tournament = models.BooleanField(default=False)
    playing = models.BooleanField(default=False)
    last_heartbeat = models.DateTimeField(default=timezone.now)

    @property
    def channels_group_name(self):
        return f"game-{self.id}"

    def __str__(self):
        return f"{self.black.user} (Black) vs {self.white.user} (White) [{self.time_limit}s]"


class MoveSet(models.QuerySet):
    def latest(self, **kwargs):
        return self.order_by("-created_at").first()


class Move(models.Model):

    objects = MoveSet.as_manager()

    id = models.BigAutoField(primary_key=True)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    created_at = models.DateTimeField(auto_now_add=True)
    board = models.CharField(max_length=64, default="")
    player = models.CharField(max_length=1, choices=PLAYER_CHOICES)
    move = models.IntegerField(default=-10)

    possible = ArrayField(models.IntegerField(default=-1), default=list)

    def __str__(self):
        return f"{self.game}, {self.player}, {self.move}, {self.created_at}"


class GameObject(models.Model):

    id = models.BigAutoField(primary_key=True)

    created_at = models.DateTimeField(auto_now_add=True)
    player = models.CharField(max_length=1, choices=PLAYER_CHOICES)

    class Meta:
        abstract = True


class GameError(GameObject):

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="errors")
    error_code = models.IntegerField(default=-1)
    error_msg = models.CharField(max_length=10 * 1024, default="")


class GameLog(GameObject):

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="logs")
    message = models.CharField(max_length=10 * 1024, default="")
