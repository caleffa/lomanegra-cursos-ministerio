# Generated by Django 2.1.2 on 2019-10-29 13:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0014_auto_20191023_1539'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pregunta',
            options={'ordering': ('order',)},
        ),
        migrations.AlterOrderWithRespectTo(
            name='pregunta',
            order_with_respect_to=None,
        ),
    ]