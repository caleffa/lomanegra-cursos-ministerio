# Generated by Django 2.1 on 2018-08-26 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0009_video_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('home_video_vimeo_id', models.PositiveIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
