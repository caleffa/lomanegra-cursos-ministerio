# Generated by Django 2.1.2 on 2020-05-01 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0081_auto_20200427_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segment',
            name='rtmp_url',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]
