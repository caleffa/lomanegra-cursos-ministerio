# Generated by Django 2.1.2 on 2020-05-01 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='broadcast',
            name='rtmp_url',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]
