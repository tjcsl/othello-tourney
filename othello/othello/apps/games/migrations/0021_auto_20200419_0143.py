# Generated by Django 3.0.5 on 2020-04-19 05:43

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0020_auto_20200418_2305'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='gameerror',
            managers=[
                ('manager', django.db.models.manager.Manager()),
            ],
        ),
    ]
