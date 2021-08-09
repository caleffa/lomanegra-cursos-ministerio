# Generated by Django 2.1.2 on 2020-10-23 13:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0086_auto_20200828_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='requires_full_watch',
            field=models.BooleanField(db_index=True, default=True, help_text='Indica si se requiere que el alumno mire todo el video antes de poder continuar.'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='default_area',
            field=models.ForeignKey(blank=True, help_text='Es el área que se asignará a los usuarios que se registren sin que previamente exista un "Email habilitado" para ellos', null=True, on_delete=django.db.models.deletion.PROTECT, to='cursos.Area', verbose_name='Área por defecto'),
        ),
    ]
