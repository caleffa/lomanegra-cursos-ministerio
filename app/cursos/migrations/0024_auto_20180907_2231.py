# Generated by Django 2.1.1 on 2018-09-07 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0023_auto_20180907_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(),
        ),
    ]
