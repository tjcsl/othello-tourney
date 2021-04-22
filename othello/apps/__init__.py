from django.contrib.admin.apps import AdminConfig


class OthelloAdminConfig(AdminConfig):
    default_site = "othello.admin.OthelloAdmin"
