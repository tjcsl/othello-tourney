# Generated by Django 3.0.7 on 2020-06-13 01:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tournaments', '0010_auto_20200612_1921'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='bye_player',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='bye', to=settings.AUTH_USER_MODEL),
        ),
    ]