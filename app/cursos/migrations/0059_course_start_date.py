# Generated by Django 2.1.2 on 2019-05-23 12:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0058_auto_20190521_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
