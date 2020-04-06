import logging
import requests

from django.db import models
from django.contrib.auth.models import AbstractUser

from social_django.utils import load_strategy


logger = logging.getLogger(__name__)


class User(AbstractUser):
    ACCESS_TYPES = (("none", "None"), ("view", "View"), ("edit", "Edit"))

    id = models.AutoField(primary_key=True)

    access_type = models.CharField(max_length=10, choices=ACCESS_TYPES, default="none")

    @property
    def has_management_permission(self) -> bool:
        return self.access_type == "edit" or self.is_staff or self.is_superuser

    @property
    def short_name(self):
        return self.username

    def api_request(self, url, params=dict, refresh=True):
        s = self.get_social_auth()
        params.update({"format": "json"})
        params.update({"access_token": s.access_token})
        r = requests.get("https://ion.tjhsst.edu/api/{}".format(url), params=params)
        if r.status_code == 401:
            if refresh:
                try:
                    self.get_social_auth().refresh_token(load_strategy())
                except BaseException as e:
                    logger.exception(str(e))
                return self.api_request(url, params, False)
            else:
                logger.error("Ion API Request Failure: {} {}".format(r.status_code, r.json()))
        return r.json()

    def get_social_auth(self):
        return self.social_auth.get(provider="ion")

    def __str__(self):
        return self.short_name
