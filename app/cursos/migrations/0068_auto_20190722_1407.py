# Generated by Django 2.1.2 on 2019-07-22 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0067_auto_20190717_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='segment',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to='segment_thumbnails'),
        ),
    ]
