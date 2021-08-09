from urllib.parse import urlparse, urlunparse

from django.db import transaction
from django.views.generic import TemplateView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, resolve_url, redirect
from django.http import Http404, QueryDict, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.utils.translation import gettext_lazy as _

from .models import Encuesta, Pregunta, EncuestaTracking, Respuesta, OpcionPregunta




class EncuestaView(LoginRequiredMixin, TemplateView):
    template_name = 'encuestas/encuesta_view.html'

    def get_context_data(self, **kwargs):
        encuesta_id = self.kwargs.get('encuesta')
        encuesta = get_object_or_404(Encuesta, pk=encuesta_id)
        if not encuesta.user_can_answer_now(self.request.user):
            raise Http404()
        context = super().get_context_data(**kwargs)

        context['encuesta'] = encuesta
        tracking = EncuestaTracking.objects.filter(encuesta=encuesta, usuario=self.request.user).first()
        if tracking and tracking.iniciada:
            context['pregunta'] = tracking.get_next_question()
        else:
            context['sin_iniciar'] = True
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        action = request.POST.get('action')
        tracking, created = EncuestaTracking.objects.get_or_create(encuesta=context.get('encuesta'), usuario=request.user)
        if action == 'INICIAR':
            tracking.iniciar()
            context = self.get_context_data(**kwargs)
        elif action == 'RESPONDER':
            self.save_respuesta(context, tracking)
        elif action == 'SNOOZE':
            tracking.snooze()
            if self.request.GET.get('next'):
                return redirect(self.request.GET.get('next'))
            return redirect('home')
        else:
            return HttpResponseBadRequest()
        if not context.get('pregunta'):
            tracking.finalizar()
        return super().render_to_response(context)

    @transaction.atomic()
    def save_respuesta(self, context, tracking):
        pregunta = context['pregunta']
        respuesta = Respuesta()
        respuesta.tracking = tracking
        respuesta.pregunta = pregunta
        respuesta.save()
        if pregunta.tipo == Pregunta.ADITIVA:
            for op in pregunta.opciones.all():
                if self.request.POST.get('opcion-'+str(op.id), None):
                    respuesta.opciones.add(op)
            if pregunta.aditiva_debe_contestar_al_menos_una and not respuesta.opciones.all():
                context['error'] = _('Debe seleccionar al menos una opción.')
        elif pregunta.tipo == Pregunta.EXCLUYENTE:
            op_id = self.request.POST.get('excluyente-input')
            opcion = OpcionPregunta.objects.get(pk=op_id)
            if opcion:
                respuesta.opciones.add(opcion)
            else:
                context['error'] = _('Debe seleccionar una de las opciones.')
        elif pregunta.tipo == Pregunta.TEXTO:
            texto = self.request.POST.get('texto-input')
            if texto:
                respuesta.texto = texto
            else:
                context['error'] = _('Debe ingresar una respuesta.')
        elif pregunta.tipo == Pregunta.ESTRELLAS:
            value = self.request.POST.get('estrellas-input')
            if value:
                respuesta.estrellas = value
            else:
                context['error'] = _('Debe seleccionar una de las opciones.')
        elif pregunta.tipo == Pregunta.PULGARES:
            if self.request.POST.get('pulgar-input') == '1':
                respuesta.pulgar = True
            elif self.request.POST.get('pulgar-input') == '2':
                respuesta.pulgar = False
            else:
                context['error'] = _('Debe seleccionar una de las opciones.')
        if not context.get('error'):
            respuesta.save()
            context['pregunta'] = tracking.get_next_question()
        else:
            respuesta.delete()


def redirect_to_encuesta(next, encuesta, redirect_field_name='next'):
    """
    Redirigir al usuario a la encuesta
    """
    encuesta_url = resolve_url('encuestas:encuesta', encuesta=encuesta.pk)

    url_parts = list(urlparse(encuesta_url))
    if redirect_field_name:
        querystring = QueryDict(url_parts[4], mutable=True)
        querystring[redirect_field_name] = next
        url_parts[4] = querystring.urlencode(safe='/')

    return HttpResponseRedirect(urlunparse(url_parts))
