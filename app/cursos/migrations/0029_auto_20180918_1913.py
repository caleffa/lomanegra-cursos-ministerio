# Generated by Django 2.1.1 on 2018-09-18 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cursos', '0028_remove_video_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='DownloadableDocumentTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_download_timestamp', models.DateTimeField(auto_now_add=True)),
                ('times_downloaded', models.PositiveIntegerField(default=1)),
                ('last_download_timestamp', models.DateTimeField(auto_now=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.DownloadableDocument')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='downloadabledocumenttracking',
            unique_together={('document', 'user')},
        ),
    ]