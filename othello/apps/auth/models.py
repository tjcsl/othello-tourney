from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_teacher = models.BooleanField(default=False, null=False)
    is_student = models.BooleanField(default=True, null=False)
    is_imported = models.BooleanField(default=False, null=False)
    rating = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    @property
    def has_management_permission(self) -> bool:
        return self.is_teacher or self.is_staff or self.is_superuser

    @property
    def short_name(self):
        return (
            f"{self.first_name} {self.last_name} ({self.username})"
            if self.first_name or self.last_name
            else self.username
        )

    def get_social_auth(self):
        return self.social_auth.get(provider="ion")

    def save(self, *args, **kwargs):
        existing_user = User.objects.filter(username=self.username, is_imported=True).first()
        if existing_user:
            from ..games.models import (
                Submission,  # cannot import at top of file b/c Submission references User (circular import)
            )

            Submission.objects.filter(user=existing_user).update(user=self)
            existing_user.delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class RatingHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rating_history")
    rating = models.DecimalField(max_digits=6, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    match = models.ForeignKey("games.Match", null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ["changed_at"]
