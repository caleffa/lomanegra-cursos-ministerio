# Generated by Django 2.1.2 on 2020-05-06 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0083_auto_20200504_1449'),
        ('streaming', '0003_auto_20200501_1425'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='broadcast',
            unique_together={('segment', 'is_live')},
        ),
    ]