# Generated by Django 2.1.2 on 2019-09-05 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('encuestas', '0012_auto_20190830_0133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encuesta',
            name='mensaje_gracias',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='encuesta',
            name='texto',
            field=models.TextField(max_length=200),
        ),
        migrations.AlterField(
            model_name='pregunta',
            name='texto',
            field=models.TextField(),
        ),
    ]
