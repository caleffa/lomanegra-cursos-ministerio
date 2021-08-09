# Generated by Django 2.1 on 2018-08-15 15:35

import cursos.models
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0002_videotracking_parts_watched'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videotracking',
            name='parts_watched',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.BooleanField(default=False), default=cursos.models.emptyPartsWatched, size=100),
        ),
    ]
