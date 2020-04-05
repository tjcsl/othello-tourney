import os
from django.db import models

from ..auth.models import User


class Submission(models.Model):

    def upload_path(self, name):
        return os.path.join(self.user.short_name, "strategy.py")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    code = models.FileField(upload_to=upload_path)
