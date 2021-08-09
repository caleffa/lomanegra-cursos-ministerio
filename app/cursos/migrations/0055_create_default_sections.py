from django.db import migrations, models
import django.db.models.deletion


def create_default_section(apps, schema_editor):
    Segment = apps.get_model('cursos', 'Segment')
    SegmentSection = apps.get_model('cursos', 'SegmentSection')
    Question = apps.get_model('cursos', 'Question')

    for s in Segment.objects.all():
        section = SegmentSection.objects.create(segment=s, questions_to_ask=s.questions_to_ask, order=1)

        for q in s.question_set.all():
            q.section = section
            q.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cursos', '0054_question_section'),
    ]

    operations = [
        migrations.RunPython(create_default_section),
    ]
