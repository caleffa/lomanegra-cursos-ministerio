# Generated by Django 2.1 on 2018-08-23 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0005_video_max_retries'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaireoption',
            name='selected_by_user',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
