# Generated by Django 2.1.2 on 2019-08-08 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0071_auto_20190807_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='certificate_template',
            field=models.ImageField(blank=True, null=True, upload_to='course_certificate', verbose_name='Plantilla del certificado'),
        ),
    ]
