# Generated by Django 2.1.2 on 2019-01-18 19:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0053_auto_20190118_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='section',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cursos.SegmentSection'),
        ),
    ]