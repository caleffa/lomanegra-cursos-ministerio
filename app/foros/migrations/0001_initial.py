# Generated by Django 2.1.2 on 2019-07-22 17:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cursos', '0068_auto_20190722_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('order', models.PositiveIntegerField()),
                ('segment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cursos.Segment')),
            ],
        ),
        migrations.CreateModel(
            name='ForumMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited', models.DateTimeField(null=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('delete_date', models.DateTimeField(null=True)),
                ('delete_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('forum', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foros.Forum')),
                ('segment_tracking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cursos.SegmentTracking')),
            ],
        ),
        migrations.CreateModel(
            name='ForumMessageHistoryRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('edited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('forum_message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='foros.ForumMessage')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='forum',
            unique_together={('segment', 'title'), ('segment', 'order')},
        ),
    ]
