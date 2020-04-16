import os
import uuid

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.exceptions import ObjectDoesNotExist
from .storage import OverwriteStorage


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

    def __str__(self):
        return f"{self.black.user} v. {self.white.user} @ {self.time_limit}"
