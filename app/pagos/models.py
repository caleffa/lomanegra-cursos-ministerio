from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from payments import PurchasedItem
from payments.models import BasePayment, PaymentStatus


class Orden(models.Model):
    """ Guarda las órdenes de compra de los usuarios """
    created = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ordenes_de_compra')
    curso = models.ForeignKey('cursos.Course', on_delete=models.CASCADE, related_name='ordenes_de_compra')

    class Meta:
        unique_together = ['usuario', 'curso']


    @property
    def pago_vigente(self) -> 'Pago':
        p = self.pagos.order_by('-created').first()
        return p


class Pago(BasePayment):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='pagos')

    def get_failure_url(self):
        return reverse('pago-fallido', kwargs={'pk': self.id})

    def get_success_url(self):
        return reverse('pago-exitoso', kwargs={'pk': self.id})

    def get_purchased_items(self):
        yield PurchasedItem(
            name=_(f'Curso "{self.orden.curso.title}"'),
            price=self.orden.curso.price,
            quantity=1,
            currency=self.orden.curso.price_currency,
            sku=self.orden.curso.slug
        )

    @classmethod
    def nuevo_pago_para_orden(cls, oc: Orden):
        return Pago.objects.create(
            orden=oc,
            variant='paypal',
            description=_('Inscripción a curso'),
            total=oc.curso.price,
            currency=oc.curso.price_currency,
            billing_first_name=oc.usuario.name,
            billing_last_name=oc.usuario.last_name,
        )

    @property
    def pagado(self) -> bool:
        return self.status == PaymentStatus.CONFIRMED

    @property
    def en_proceso(self) -> bool:
        return self.status == PaymentStatus.WAITING

    @property
    def fallido(self) ->bool:
        return self.status == PaymentStatus.ERROR or self.status == PaymentStatus.REJECTED
