# Generated by Django 2.1.1 on 2018-10-09 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0035_auto_20181009_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='slides')),
                ('next_slide', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous_slide', to='cursos.Slide')),
            ],
        ),
        migrations.AddField(
            model_name='segment',
            name='type_of_segment',
            field=models.CharField(choices=[('V', 'Video'), ('S', 'Slides')], default='V', max_length=1),
        ),
        migrations.AlterField(
            model_name='segment',
            name='vimeo_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='segment',
            name='first_slide',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='cursos.Slide'),
        ),
    ]
