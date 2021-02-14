from django.test import RequestFactory

from ...test.othello_test import OthelloTestCase
from .views import handle_500_view


class ErrorsTestCase(OthelloTestCase):
    def test_500_view(self):
        factory = RequestFactory()
        request = factory.get("/")
        response = handle_500_view(request)

        self.assertEqual(500, response.status_code)
