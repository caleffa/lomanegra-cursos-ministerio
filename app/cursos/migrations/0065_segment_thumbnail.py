# Generated by Django 2.1.2 on 2019-07-12 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0064_segment_enabled_since'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
