# Generated by Django 2.1.1 on 2018-09-20 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0032_videotracking_user_has_downloaded_all_documents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='videotracking',
            name='user_has_downloaded_document',
        ),
    ]