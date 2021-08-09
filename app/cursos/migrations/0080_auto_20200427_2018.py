# Generated by Django 2.1.2 on 2020-04-27 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0079_auto_20191028_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='announcement_type',
            field=models.CharField(choices=[('O', 'Open'), ('F', 'Fixed dates')], default='O', max_length=1),
        ),
        migrations.AddField(
            model_name='segment',
            name='is_live_stream',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='segment',
            name='rtmp_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='segment',
            name='stream_key',
            field=models.UUIDField(blank=True, default=None, null=True, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='segment',
            unique_together={('course', 'order', 'is_live_stream')},
        ),
    ]