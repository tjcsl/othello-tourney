from typing import Any

from django.db import models
from django.utils.timezone import now

from ..games.models import Game, Submission
from ..games.validators import validate_game_time_limit
from ..auth.models import User
#from .validators import validate_tournament_rounds

from django.contrib.auth import get_user_model

import random

class Gauntlet(models.Model):
    # objects: Any = TournamentSet().as_manager()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now=True)
    game_time_limit = models.IntegerField(default=5, validators=[validate_game_time_limit])

    running = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    terminated = models.BooleanField(default=False)

    celery_task_id = models.CharField(max_length=48, default="")

    #asdf = models.ForeignKey(Submission, on_delete=models.PROTECT, null = False)
    submission = models.ForeignKey(
        Submission,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="gauntletsubmission",
        default=None,
    )
    pastRating = models.IntegerField(default=400)
    
    # celery_task_id = models.CharField(max_length=48, default="")
    game1 = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="g1", null=False, blank=False, default=None)
    game2 = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="g2", null=False, blank=False, default=None)
    game3 = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="g3", null=False, blank=False, default=None)

    mySide1 = models.CharField(default=random.choice(['x', 'o']), max_length=1)
    mySide2 = models.CharField(default=random.choice(['x', 'o']), max_length=1)
    mySide3 = models.CharField(default=random.choice(['x', 'o']), max_length=1)

    def __str__(self) -> str:
        return "gauntlet object"

    def __repr__(self) -> str:
        return f"gauntlet object {self.user} {self.created_at}"

class RankedManager(models.Model):
    auto_run = models.BooleanField(default=False, null=False)
    next_auto_run = models.DateTimeField()
    running = models.BooleanField(default=False, null=False)
    game = models.ForeignKey(Game, on_delete=models.PROTECT, related_name="g", null=True, blank=True, default=None)

    def __str__(self) -> str:
        return f"Auto Run {self.auto_run}, Next Auto {self.next_auto_run}, Running {self.running}"

    def __repr__(self) -> str:
        return f"Auto Run {self.auto_run}, Next Auto {self.next_auto_run}, Running {self.running}"

# class RankedGame(models.Model):

#     batch = models.DateField()

#     game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False)

#     def __str__(self) -> str:
#         return f"Ranked game @ {str(self.batch)} - {self.game.black.get_user_name()} v. {self.game.white.get_user_name()}"