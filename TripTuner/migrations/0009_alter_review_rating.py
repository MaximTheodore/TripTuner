# Generated by Django 5.1.2 on 2024-11-14 17:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TripTuner', '0008_alter_city_country_id_alter_hotel_city_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1, message='Оценка не может быть меньше 1.'), django.core.validators.MaxValueValidator(5, message='Оценка не может быть больше 5.')], verbose_name='Оценка'),
        ),
    ]