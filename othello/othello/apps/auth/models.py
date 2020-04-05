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
    def has_view_permission(self) -> bool:
        """Whether the user can view workstation information."""
        return self.access_type == "view" or self.has_edit_permission

    @property
    def has_edit_permission(self) -> bool:
        """Whether the user can perform basic workstation management (such as resetting the healthy
        flag and scheduling/cancelling maintenance periods).

        Note: Editors can only cancel maintenance periods they have scheduled."""
        return self.access_type == "edit" or self.has_management_permission

    @property
    def has_management_permission(self) -> bool:
        """Whether the user can perform advanced workstation management (such as creating and
        deleting workstations, cancelling maintenance periods scheduled by other users, or sending
        Wake-on-LAN packets)."""
        return self.is_staff and self.is_superuser

    @property
    def short_name(self):
        return self.username

    def api_request(self, url, params={}, refresh=True):
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
