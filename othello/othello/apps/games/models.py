import os
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class Submission(models.Model):

    def upload_path(self, name):
        return os.path.join(self.user.short_name, "strategy.py")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    submitted_time = models.DateTimeField(auto_now=True)
    code = models.FileField(upload_to=upload_path, storage=OverwriteStorage())
