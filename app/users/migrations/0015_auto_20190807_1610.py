# Generated by Django 2.1.2 on 2019-08-07 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_user_is_stakeholder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_stakeholder',
            field=models.BooleanField(default=False, verbose_name='Es Stakeholder'),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_tutor',
            field=models.BooleanField(default=False, verbose_name='Es Tutor'),
        ),
    ]
