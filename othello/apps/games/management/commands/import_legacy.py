import os
import shutil

from uuid import uuid4
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from ....auth.models import User
from ....games.models import Submission


class Command(BaseCommand):
    help = 'Imports legacy user scripts'

    def add_arguments(self, parser):
        parser.add_argument('dir', help="directory to import submissions from")

    def handle(self, *args, **options):
        submissions_dir = os.path.join(settings.BASE_DIR, "submissions")
        import_dir = options['dir']
        for folder in os.listdir(import_dir):
            shutil.copytree(os.path.join(import_dir, folder), os.path.join(submissions_dir, folder))
            u, created = User.objects.get_or_create(username=folder)
            if created:
                u.is_imported = True
            u.save(update_fields=["is_imported"])
            name = u.short_name if u else folder
            s = Submission.objects.create(
                user=u,
                name=str(name),
                is_legacy=True,
            )
            s.code.save("", File(open(os.path.join(submissions_dir, folder, "strategy.py"))))
            s.save(update_fields=["code"])
            print(f"Imported {folder}")




