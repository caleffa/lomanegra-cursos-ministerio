# Generated by Django 2.1.2 on 2020-05-07 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0083_auto_20200504_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segment',
            name='stream_key',
            field=models.UUIDField(blank=True, default=None, null=True),
        ),
    ]
