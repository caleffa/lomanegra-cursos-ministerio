# Generated by Django 2.1.2 on 2019-06-03 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0065_category_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='order',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
