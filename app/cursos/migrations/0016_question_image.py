# Generated by Django 2.1 on 2018-08-28 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0015_questionnairequestion_answered_correctly'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(null=True, upload_to='question_images'),
        ),
    ]
