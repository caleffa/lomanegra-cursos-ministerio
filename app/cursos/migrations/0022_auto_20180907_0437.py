# Generated by Django 2.1.1 on 2018-09-07 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0021_videotracking_user_has_downloaded_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='min_correct_questions',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
