from celery import shared_task
from django.utils import timezone
from cursos.models import Segment
from streaming.models import Broadcast


@shared_task(name='broadcasts_set_live')
def broadcasts_set_live():
    to_set_live = Broadcast.objects.filter(
        started__isnull=True,  # Los BC que nunca empezaron a transmitir
        is_live=False,  # y que no están en vivo
        date__lte=timezone.now()  # y cuya fecha es anterior a ya mismo
    )

    for bc in to_set_live:
        bc.set_live()


