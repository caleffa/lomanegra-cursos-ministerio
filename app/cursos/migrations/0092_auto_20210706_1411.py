# Generated by Django 2.2.17 on 2021-07-06 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0091_segment_embed_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='CareerTrack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='Título')),
                ('image', models.ImageField(blank=True, upload_to='career_track_thumbnails')),
                ('order', models.PositiveIntegerField(unique=True)),
            ],
            options={
                'verbose_name': 'Categoría',
                'verbose_name_plural': 'Categorías',
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Subcategoría', 'verbose_name_plural': 'Subcategorías'},
        ),
        migrations.AddField(
            model_name='category',
            name='career_tracks',
            field=models.ManyToManyField(blank=True, related_name='categories', to='cursos.CareerTrack'),
        ),
    ]
