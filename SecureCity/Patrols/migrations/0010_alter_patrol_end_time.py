<<<<<<< HEAD
# Generated by Django 4.0.3 on 2022-05-21 20:45
=======
# Generated by Django 4.0.3 on 2022-05-24 18:30
>>>>>>> e72f89392b4953f212253e21df6e554d34a4d407

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
<<<<<<< HEAD
        ('Patrols', '0009_alter_patrol_description_alter_patrol_end_time'),
=======
        ('Patrols', '0009_alter_patrol_end_time'),
>>>>>>> e72f89392b4953f212253e21df6e554d34a4d407
    ]

    operations = [
        migrations.AlterField(
            model_name='patrol',
            name='end_time',
<<<<<<< HEAD
            field=models.TimeField(default=datetime.datetime(2022, 5, 21, 23, 45, 24, 646200, tzinfo=utc), verbose_name='end time'),
=======
            field=models.TimeField(default=datetime.datetime(2022, 5, 24, 21, 30, 23, 262162, tzinfo=utc), verbose_name='end time'),
>>>>>>> e72f89392b4953f212253e21df6e554d34a4d407
        ),
    ]
