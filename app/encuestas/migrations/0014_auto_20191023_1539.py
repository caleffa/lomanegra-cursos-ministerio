# Generated by Django 2.1.2 on 2019-10-23 15:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0013_auto_20190905_2048'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pregunta',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='opcionpregunta',
            unique_together={('pregunta', 'texto')},
        ),
        migrations.AlterOrderWithRespectTo(
            name='pregunta',
            order_with_respect_to='encuesta',
        ),
    ]
