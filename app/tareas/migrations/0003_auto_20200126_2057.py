# Generated by Django 2.1.2 on 2020-01-26 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0002_auto_20200123_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tarea',
            name='adjuntos',
            field=models.ManyToManyField(blank=True, null=True, to='tareas.Adjunto'),
        ),
    ]