# Generated by Django 2.1.2 on 2019-01-18 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0055_create_default_sections'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='video',
        ),
    ]
