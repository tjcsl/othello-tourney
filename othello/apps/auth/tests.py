from django.urls import reverse

from ...test.othello_test import OthelloTestCase


class AuthTestCase(OthelloTestCase):
    def test_index(self):
        response = self.client.get(reverse("auth:index"))
        self.assertEqual(200, response.status_code)

    def test_login(self):
        response = self.client.get(reverse("auth:login"))
        self.assertEqual(200, response.status_code)

    def test_error(self):
        response = self.client.get(reverse("auth:error"))
        self.assertEqual(200, response.status_code)
