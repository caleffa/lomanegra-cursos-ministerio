from django.db import models
from django.conf import settings
import requests

from users.models import User
from cursos.models import Course, Area, AllowedDomain

class Conversacion(models.Model):
    iniciador = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='conv_iniciadas')
    destinatario = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultimo_mensaje = models.DateTimeField(null=False)
    fecha_ultima_interaccion_iniciador = models.DateTimeField(null=True)
    fecha_ultima_interaccion_destinatario = models.DateTimeField(null=True)
    permite_responder = models.BooleanField(default=True)
    curso = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)
    asunto = models.CharField(blank=False, max_length=50)
    generada_por = models.ForeignKey('GeneradorConversaciones', null=True, on_delete=models.CASCADE, related_name="conv_generadas")

    def last_message_readed(self, user):
        last_message = self.mensajes.filter(receptor=user).order_by('-fecha_creacion').first()
        if last_message:
            return last_message.leido
        return None

class Mensaje(models.Model):
    conversacion = models.ForeignKey(Conversacion, null=False, on_delete=models.CASCADE, related_name='mensajes')
    emisor = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    responde_a = models.ForeignKey('Mensaje', null=True, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False) 
    fecha_leido = models.DateTimeField(null=True)
    cuerpo = models.TextField(blank=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Mensaje, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                  update_fields=update_fields)
        # envío el mensaje via la API de ministerio
        if self.receptor.external_user:
            headers = {
                'ApiKey': f'{settings.API_NOTIFICACIONES_APIKEY}'
            }
            url = settings.API_NOTIFICACIONES_URL
            params = {
                'idPerfil': self.receptor.external_user.external_id,
                'titulo': self.conversacion.asunto,
                'contenido': self.cuerpo,
                'url': ''
            }
            r = requests.post(url, headers=headers, params=params)


class GeneradorConversaciones(models.Model):
    iniciador = models.ForeignKey(User, null=False, on_delete=models.CASCADE, related_name='generador_conv_iniciados')
    areas_destino = models.ManyToManyField(Area)
    dominios_destino = models.ManyToManyField(AllowedDomain)
    cursos_destino = models.ManyToManyField(Course, related_name='generador_conv_destino')
    usuarios_destino = models.ManyToManyField(User)
    permite_responder = models.BooleanField(default=True, null=False)
    curso_solo_inscriptos = models.BooleanField(default=True, null=False)
    curso = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)
    asunto = models.CharField(blank=False, max_length=50)
    cuerpo = models.TextField(blank=False, max_length=250)
