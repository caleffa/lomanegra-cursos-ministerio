# Generated by Django 2.1.2 on 2019-06-04 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0058_segmenttracking_watched_full_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersEvolutionReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('finished', models.DateTimeField()),
                ('present', models.BooleanField(default=False)),
                ('file', models.FileField(upload_to='reports')),
            ],
        ),
    ]
