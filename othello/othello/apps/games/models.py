import os
from django.db import models
from django.conf import settings


class Submission(models.Model):

    def upload_path(self, name):
        return os.path.join(self.user.short_name, "strategy.py")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    code = models.FileField(upload_to=upload_path)
