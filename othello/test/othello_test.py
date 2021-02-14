from django.contrib.auth import get_user_model
from django.test import TestCase


class OthelloTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def login(self, username="awilliam"):
        # We need to add the user to the db before trying to login as them.
        user = get_user_model().objects.get_or_create(username=username)[0]
        self.client.force_login(user)
        return user

    def make_admin(self, username="awilliam"):
        user = self.login(username=username)
        # Make user an admin
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
