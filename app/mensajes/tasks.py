from celery import shared_task

from mensajes.helpers import generar_conversacion
from mensajes.models import GeneradorConversaciones


@shared_task
def task_generar_conversacion(generador_id):
    print('####### Corriendo tarea')
    gc = GeneradorConversaciones.objects.get(id=generador_id)
    generar_conversacion(gc)
