# Generated by Django 5.1.2 on 2024-11-07 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TripTuner', '0006_remove_flight_departure_date_back_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportticket',
            name='resolved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата решения'),
        ),
    ]
