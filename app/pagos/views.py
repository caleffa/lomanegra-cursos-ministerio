from django.shortcuts import render
from django.db import transaction
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from payments import RedirectNeeded
from payments.models import PaymentStatus
from cursos.models import Course, CourseEnrollment
from .models import Pago, Orden


class AlreadyPayed(RedirectNeeded):
    pass


class PaymentIsProcessing(Exception):
    pass


class RequestUserQuerySetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(orden__usuario=self.request.user)


class PagoExitosoView(LoginRequiredMixin, RequestUserQuerySetMixin, DetailView):
    model = Pago
    template_name = 'pagos/exito.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.pagado:
            enrollment, created = CourseEnrollment.objects.get_or_create(user=obj.orden.usuario, course=obj.orden.curso)
        return obj

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return_page = request.session.pop('return_page', None)
        course_page = reverse('course', kwargs={'course': self.object.orden.curso.slug})
        return redirect(return_page or course_page)

pago_exitoso = PagoExitosoView.as_view()


class PagoFallidoView(LoginRequiredMixin, RequestUserQuerySetMixin, DetailView):
    model = Pago
    template_name = 'pagos/error.html'
pago_fallido = PagoFallidoView.as_view()


class PagarCursoView(LoginRequiredMixin, FormMixin, DetailView):
    model = Course

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except RedirectNeeded as redirect_to:
            return redirect(str(redirect_to))

    def get_form(self, form_class=None):
        pago = self.object.ordenes_de_compra.get(usuario=self.request.user).pago_vigente
        return pago.get_form()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        oc, created = Orden.objects.get_or_create(usuario=self.request.user, curso=obj)

        pago = oc.pago_vigente
        if pago:
            if pago.pagado:
                raise AlreadyPayed(reverse_lazy('pago-exitoso', kwargs={'pk': pago.id}))
            # if pago.en_proceso:
            #     raise PaymentIsProcessing
            if pago.fallido:
                # Si el último pago falló, creo uno nuevo
                pago = Pago.nuevo_pago_para_orden(oc)
        else:
            pago = Pago.nuevo_pago_para_orden(oc)

        return obj
pagar_curso = PagarCursoView.as_view()
