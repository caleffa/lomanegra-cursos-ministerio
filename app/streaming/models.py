from django.db import models, transaction
from django.utils import timezone
from video.models import VideoData
from backoffice.clone import ClonableModelMixin

import logging
logger = logging.getLogger()


class LiveStreamData(models.Model):
    rtmp_url = models.CharField(max_length=512, blank=True)
    stream_key = models.UUIDField(null=True, blank=True, default=None)

    class Meta:
        abstract = True


class BroadcastQueryset(models.QuerySet):
    def currently_live(self):
        return self.filter(is_live=True)

    def not_live(self):
        return self.filter(is_live=False)

    def will_transmit_after(self, dt=None):
        return self.filter(date__isnull=False, date__gt=dt)

    def after(self, dt=None):
        if not dt:
            dt = timezone.localtime()
        return self.filter(date__gt=dt)


class Broadcast(VideoData, LiveStreamData, ClonableModelMixin, models.Model):
    segment = models.ForeignKey('cursos.Segment', on_delete=models.PROTECT, related_name='broadcasts')

    date = models.DateTimeField(null=True, blank=True) # para cuándo está programada la transmisión
    is_live = models.BooleanField(default=False, db_index=True) # si esta transmisión está funcionando ahora

    started = models.DateTimeField(null=True, blank=True) # el momento en que efectivamente comienza la transmisión
    ended = models.DateTimeField(null=True, blank=True) # el momento en que efectivamente termina la transmisión

    objects = models.Manager.from_queryset(BroadcastQueryset)()

    def set_off(self):
        self.is_live = False
        self.ended = timezone.localtime()
        self.save()

    @transaction.atomic
    def set_live(self):
        # Obtengo los broadcasts anteriores a este que aún estén 'en vivo'
        dangling_live = Broadcast.objects.filter(segment=self.segment, date__lt=self.date, is_live=True)
        for bc in dangling_live:
            bc.set_off()

        self.is_live = True
        self.started = timezone.localtime()
        self.save()
