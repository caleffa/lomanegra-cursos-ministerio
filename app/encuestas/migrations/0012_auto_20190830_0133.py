# Generated by Django 2.1.2 on 2019-08-30 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0011_encuestatracking_iniciada'),
    ]

    operations = [
        migrations.AddField(
            model_name='encuestatracking',
            name='fecha_finalizacion',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='encuestatracking',
            name='fecha_inicio',
            field=models.DateTimeField(null=True),
        ),
    ]
