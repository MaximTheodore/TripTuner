# Generated by Django 5.1.2 on 2024-11-04 11:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TripTuner', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='amenity',
            name='hotelRoom_id',
            field=models.ManyToManyField(to='TripTuner.hotelroom', verbose_name='Комната'),
        ),
        migrations.CreateModel(
            name='FlightHotelHotelRoom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TripTuner.flight', verbose_name='Рейс')),
                ('hotelRoom_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TripTuner.hotelroom', verbose_name='Номер в отеле')),
                ('hotel_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TripTuner.hotel', verbose_name='Отель')),
            ],
            options={
                'verbose_name': 'Рейс-Отель-Номер',
                'verbose_name_plural': 'Рейсы-Отели-Номера',
            },
        ),
    ]