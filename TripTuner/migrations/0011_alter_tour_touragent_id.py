# Generated by Django 5.1.2 on 2024-11-17 16:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TripTuner', '0010_delete_landmark'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tour',
            name='tourAgent_id',
            field=models.ManyToManyField(default=None, null=True, to=settings.AUTH_USER_MODEL, verbose_name='Турагент'),
        ),
    ]
