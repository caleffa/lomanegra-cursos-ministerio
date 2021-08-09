# Generated by Django 2.1.2 on 2020-01-23 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0079_auto_20191028_1335'),
        ('tareas', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarea',
            name='curso',
        ),
        migrations.AddField(
            model_name='tarea',
            name='segmento',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cursos.Segment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tareaalumno',
            name='timestamp_aprobacion',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='adjunto',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='devolucion',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='tareaalumno',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]