# Generated by Django 4.0.3 on 2022-05-21 20:08

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Patrols', '0007_alter_patrol_end_time_alter_patrol_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patrol',
            name='end_time',
            field=models.TimeField(default=datetime.datetime(2022, 5, 21, 23, 8, 47, 750695, tzinfo=utc), verbose_name='end time'),
        ),
    ]
