import os
import uuid

from enum import Enum
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxLengthValidator, MinValueValidator
from .storage import OverwriteStorage


class Player(Enum):
    BLACK = "X"
    WHITE = "O"


def save_path(instance, filename):
    return os.path.join(instance.user.short_name, f"{uuid.uuid4()}.py")


class SubmissionManager(models.Manager):
    def safe_get(self, **kwargs):
        try:
            return Submission.objects.filter(**kwargs)
        except ObjectDoesNotExist:
            return Submission.objects.none()

    def all_usable_submissions(self, user=None):
        return Submission.objects.safe_get(user=user, usable=True) if user else Submission.objects.safe_get(usable=True)

    def get_all_submissions_for_user(self, user):
        return Submission.objects.safe_get(user=user)


class Submission(models.Model):

    objects = SubmissionManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    name = models.CharField(max_length=500, default="")
    submitted_time = models.DateTimeField(auto_now=True)
    code = models.FileField(
        upload_to=save_path,
        storage=OverwriteStorage(),
        default=None,
    )
    usable = models.BooleanField(default=True)

    def get_name(self):
        return self.name

    def get_user_name(self):
        return self.user.short_name

    def get_submitted_time(self):
        return self.submitted_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_submission_name(self):
        return f'{self.get_name()}: <{self.get_submitted_time()}>'

    def get_code_filepath(self):
        return self.code.path

    def get_code_filename(self):
        return self.code.name

    @property
    def is_usable(self):
        return self.usable

    def set_usable(self):
        for x in Submission.objects.get_all_submissions_for_user(self.user):
            if x != self:
                x.usable = False
            else:
                x.usable = True
            x.save()

    def save(self, *args, **kwargs):
        if self.usable:
            for x in Submission.objects.get_all_submissions_for_user(self.user):
                if x != self:
                    x.usable = False
                    x.save()
        super(Submission, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.code.storage.delete(self.code.name)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.get_user_name()}: {self.get_submission_name()}"


@receiver(post_delete, sender=Submission)
def delete_submission_file(sender, instance, using, **kwargs):
    instance.code.delete()


class GameManager(models.Manager):
    def safe_get(self, **kwargs):
        try:
            return Game.objects.filter(**kwargs)
        except ObjectDoesNotExist:
            return Game.objects.none()

    def get_all_running(self):
        return Game.objects.all().filter(playing=True)


class Game(models.Model):
    objects = GameManager()

    black = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="black")
    white = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="white")
    time_limit = models.IntegerField(default=5,)
    playing = models.BooleanField(default=False)

    class Meta:
        unique_together = ["black", "white", "time_limit",]

    def get_code_filepath(self, player: Player):
        return self.black.get_code_filepath() if player == Player.BLACK else self.white.get_code_filepath()

    def __str__(self):
        return f"{self.black.user} (Black) vs {self.white.user} (Yourself) [{self.time_limit}s]"


class MoveManager(models.Manager):

    def get_latest_move(self):
        return qs.order_by('-created_at')[0] if len(qs := self.get_queryset()) > 0 else None


class Move(models.Model):

    manager = MoveManager()

    PLAYER_CHOICES = (
        ('B', 'Black'),
        ('W', "White"),
    )

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="moves")
    created_at = models.DateTimeField(auto_now_add=True)
    player = models.CharField(max_length=1, choices=PLAYER_CHOICES)
    board = models.CharField(max_length=64, default="")
    move = models.IntegerField(default=-1, validators=[MaxLengthValidator(64), MinValueValidator(-1)])
    valid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.game}, {self.player}, {self.board}, {self.move}, {self.valid}, {self.created_at}"


class GameLogManager(models.Manager):

    def get_latest_log(self):
        return qs.order_by('-created_at')[0] if len(qs := self.get_queryset()) > 0 else None


class GameLog(models.Model):

    manager = GameLogManager()

    log = models.CharField(max_length=10 * 1024, default="")
    created_at = models.DateTimeField(auto_now_add=True)


class BlackGameLog(GameLog):

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="black_logs")


class WhiteGameLog(GameLog):

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="white_logs")
