# Generated by Django 2.1.2 on 2019-01-18 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0051_segment_questions_to_ask'),
    ]

    operations = [
        migrations.AddField(
            model_name='segmenttracking',
            name='last_part_watched',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
