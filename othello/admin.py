from django.contrib import admin


class OthelloAdmin(admin.AdminSite):
    site_header = "Othello Database Administration"
    site_title = "Othello Database Administration"
    enable_nav_sidebar = False
