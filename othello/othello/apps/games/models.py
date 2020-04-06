import os
from django.db import models
from django.conf import settings

from .storage import OverwriteStorage


class Submission(models.Model):

    def upload_path(self, name):
        return os.path.join(self.user.short_name, "strategy.py")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    submitted_time = models.DateTimeField(auto_now=True)
    code = models.FileField(upload_to=upload_path, storage=OverwriteStorage(), default=None)

    def __str__(self):
        return self.user.short_name


class Game(models.Model):
    black = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="black")
    white = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="white")
    time_limit = models.IntegerField(default=5,)
