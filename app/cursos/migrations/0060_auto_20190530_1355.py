# Generated by Django 2.1.2 on 2019-05-30 13:55

from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0059_course_start_date'),
    ]

    operations = [
        UnaccentExtension()
    ]