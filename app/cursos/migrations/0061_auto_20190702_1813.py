# Generated by Django 2.1.2 on 2019-07-02 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0060_auto_20190604_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='enabled_courses',
            field=models.ManyToManyField(blank=True, help_text='Son los cursos que podrán realizar los usuarios que pertenezcan a esta área', related_name='enabled_areas', to='cursos.Course', verbose_name='Cursos habilitados'),
        ),
    ]
