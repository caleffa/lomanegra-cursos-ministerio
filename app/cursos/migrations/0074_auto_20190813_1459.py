# Generated by Django 2.1.2 on 2019-08-13 14:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0072_auto_20190808_1432'),
    ]

    operations = [
        migrations.AlterField(
            model_name='allowedemail',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='allowed_email', to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
    ]
