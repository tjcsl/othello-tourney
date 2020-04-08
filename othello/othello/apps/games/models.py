import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from .storage import OverwriteStorage


class SubmissionManager(models.Manager):
    def safe_get(self, **kwargs):
        try:
            return Submission.objects.get(**kwargs)
        except ObjectDoesNotExist:
            return None

    def all_latest_submissions(self):
        return Submission.objects.order_by('user', '-submitted_time').distinct('user')


class Submission(models.Model):

    def upload_path(self, name):
        return os.path.join(self.user.short_name, "strategy.py")

    objects = SubmissionManager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    submitted_time = models.DateTimeField(auto_now=True)
    code = models.FileField(upload_to=upload_path,
                            storage=OverwriteStorage(), default=None)

    def __str__(self):
        return self.user.short_name


class GameManager(models.Manager):
    def safe_get(self, **kwargs):
        try:
            return Game.objects.get(**kwargs)
        except ObjectDoesNotExist:
            return None

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

    def __str__(self):
        return f"{self.black.user} v. {self.white.user} @ {self.time_limit}"
