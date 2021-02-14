from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(primary_key=True)

    is_teacher = models.BooleanField(default=False, null=False)
    is_student = models.BooleanField(default=True, null=False)
    is_imported = models.BooleanField(default=False, null=False)

    @property
    def has_management_permission(self) -> bool:
        return self.is_teacher or self.is_staff or self.is_superuser

    @property
    def short_name(self):
        return self.username

    def get_social_auth(self):
        return self.social_auth.get(provider="ion")

    def save(self, *args, **kwargs):
        existing_user = User.objects.filter(username=self.username, is_imported=True).first()
        if existing_user:
            from ..games.models import Submission

            Submission.objects.filter(user=existing_user).update(user=self)
            existing_user.delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_name
