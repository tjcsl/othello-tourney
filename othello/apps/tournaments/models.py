from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now

from ..games.models import Game, Submission


class TournamentSet(models.QuerySet):
    def finished(self, **kwargs):
        return self.filter(finished=True, **kwargs)

    def in_progress(self, **kwargs):
        return self.filter(start_time__lte=now(), finished=False, **kwargs)

    def future(self, **kwargs):
        return self.filter(start_time__gt=now(), **kwargs)


class Tournament(models.Model):

    objects = TournamentSet().as_manager()

    created_at = models.DateTimeField(auto_now=True)

    start_time = models.DateTimeField()
    include_users = models.ManyToManyField(Submission, blank=True,)
    game_time_limit = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(settings.MAX_TIME_LIMIT)]
    )
    num_rounds = models.IntegerField(
        default=15, validators=[MinValueValidator(15), MaxValueValidator(settings.MAX_ROUND_NUM)]
    )
    played = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(settings.MAX_ROUND_NUM)]
    )
    bye_player = models.ForeignKey(
        Submission,
        blank=False,
        null=False,
        on_delete=models.PROTECT,
        related_name="bye",
        default=None,
    )

    finished = models.BooleanField(default=False,)
    terminated = models.BooleanField(default=False,)

    def __str__(self):
        return "Tournament at {}".format(self.start_time.strftime("%Y-%m-%d %H:%M:%S"))

    def __repr__(self):
        return "<Tournament @ {}, {}>".format(
            self.start_time.strftime("%Y-%m-%d %H:%M:%S"), self.finished
        )


class TournamentPlayer(models.Model):

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="players")
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    ranking = models.DecimalField(default=0, decimal_places=1, max_digits=15)

    def __str__(self):
        return self.submission.get_game_name()


class TournamentGame(models.Model):

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, null=False, blank=False, related_name="games"
    )

    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=False, blank=False)

    def __str__(self):
        return f"{str(self.tournament)} - {self.game.black.get_user_name()} v. {self.game.white.get_user_name()}"
