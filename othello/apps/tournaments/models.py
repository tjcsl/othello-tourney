from django.db import models
from django.utils.timezone import now
from django.contrib.auth import get_user_model


class TournamentSet(models.QuerySet):

    def finished(self):
        return self.filter(finished=True)

    def in_progress(self):
        return self.filter(start_time__lte=now(), finished=False)

    def future(self):
        return self.filter(start_time_gt=now())


class Tournament(models.Model):

    objects = TournamentSet().as_manager()

    created_at = models.DateTimeField(auto_now=True)

    start_time = models.DateTimeField()
    exclude_users = models.ManyToManyField(get_user_model(), blank=True,)

    finished = models.BooleanField(default=False,)

    def __str__(self):
        return "Tournament at {}".format(self.start_time.strftime("%Y-%m-%d %H:%M:%S"))

    def __repr__(self):
        return "<Tournament @ {}, {}>".format(self.start_time.strftime("%Y-%m-%d %H:%M:%S"), self.finished)
\