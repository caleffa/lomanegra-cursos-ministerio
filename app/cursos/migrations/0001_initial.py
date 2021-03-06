# Generated by Django 2.0.8 on 2018-08-12 23:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_complete', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=256)),
                ('is_correct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=256)),
                ('has_only_one_correct_answer', models.BooleanField(default=True)),
                ('show_correct_options', models.PositiveIntegerField(default=1)),
                ('show_incorrect_options', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_complete', models.BooleanField(default=False)),
                ('score', models.IntegerField(null=True)),
                ('creation_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('option', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Option')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('answered', models.BooleanField(default=False)),
                ('answer_timestamp', models.DateTimeField(auto_now=True)),
                ('options', models.ManyToManyField(through='cursos.QuestionnaireOption', to='cursos.Option')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Question')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Questionnaire')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('order', models.PositiveIntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Course')),
            ],
        ),
        migrations.CreateModel(
            name='VideoTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('started_timestamp', models.DateTimeField(auto_now_add=True)),
                ('last_watch', models.DateTimeField(auto_now=True)),
                ('watched_full', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Video')),
            ],
        ),
        migrations.AddField(
            model_name='questionnaireoption',
            name='questionnaire_question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.QuestionnaireQuestion'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='questions',
            field=models.ManyToManyField(through='cursos.QuestionnaireQuestion', to='cursos.Question'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Video'),
        ),
        migrations.AddField(
            model_name='question',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Video'),
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cursos.Question'),
        ),
        migrations.AlterUniqueTogether(
            name='videotracking',
            unique_together={('video', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='video',
            unique_together={('course', 'order')},
        ),
    ]
