# Generated by Django 2.1.2 on 2019-06-04 15:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mensajes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensaje',
            name='responde_a',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mensajes.Mensaje'),
        ),
    ]
