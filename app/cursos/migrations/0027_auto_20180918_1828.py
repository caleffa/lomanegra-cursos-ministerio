# Generated by Django 2.1.1 on 2018-09-18 18:28

from django.db import migrations


## DATA MIGRATION

def copy_video_document(apps, schema_editor):
    Video = apps.get_model('cursos', 'Video')
    DownloadableDocument = apps.get_model('cursos', 'DownloadableDocument')
    for video in Video.objects.all():
    	if video.document:
        	DownloadableDocument.objects.create(video=video, document=video.document)
        
class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0026_downloadabledocument'),
    ]

    operations = [
    	migrations.RunPython(copy_video_document),
    ]
