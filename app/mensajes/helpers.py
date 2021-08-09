from django.db.models import Q
from django.utils import timezone

from users.models import User
from .models import GeneradorConversaciones, Conversacion, Mensaje


def generar_conversacion(gc: GeneradorConversaciones):
    qf = None
    usuarios_cursos = set()
    if gc.areas_destino:
        qf = add_filter(Q(allowed_email__area__in=gc.areas_destino.all()), qf)
    if gc.dominios_destino:
        domains = gc.dominios_destino.all().values_list('domain', flat=True)
        qf = add_filter(Q(domain__in=domains), qf)
    if gc.cursos_destino:
        if gc.curso_solo_inscriptos:
            qf = add_filter(Q(enrollments__course__in=gc.cursos_destino.all()), qf)
        else:
            for curso in gc.cursos_destino.all():
                usuarios_cursos = usuarios_cursos.union(set(curso.allowed_users.all()))
    usuarios = set(User.objects.filter(qf))
    if gc.usuarios_destino:
        usuarios = usuarios.union(set(gc.usuarios_destino.all()))
    if len(usuarios_cursos) > 0:
        usuarios = usuarios.union(set(usuarios_cursos))
    if gc.iniciador in usuarios:
        usuarios.remove(gc.iniciador)
    for usr in usuarios:
        create_conversation(gc, usr)


def add_filter(new_qf, qf):
    if qf:
        qf = qf | new_qf
        return qf
    else:
        return new_qf

def create_conversation(gc, usr):
    new_conv = Conversacion()
    new_conv.iniciador = gc.iniciador
    new_conv.destinatario = usr
    new_conv.permite_responder = gc.permite_responder
    new_conv.curso = gc.curso
    new_conv.asunto = gc.asunto
    new_conv.generada_por = gc
    new_conv.fecha_ultimo_mensaje = timezone.now()
    new_conv.save()

    new_mensaje = Mensaje()
    new_mensaje.conversacion = new_conv
    new_mensaje.emisor = gc.iniciador
    new_mensaje.receptor = usr
    new_mensaje.leido = False
    new_mensaje.cuerpo = gc.cuerpo
    new_mensaje.save()
