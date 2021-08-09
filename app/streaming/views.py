from django.views.generic import ListView
from rest_framework import viewsets
from cursos.models import Segment, Course
from .serializers import SegmentSerializer


class SegmentIsLiveViewSet(viewsets.ModelViewSet):
    serializer_class = SegmentSerializer
    queryset = Segment.objects.only_live_stream()
    http_method_names = ['get', 'options']


class MisTransmisiones(ListView):
    template_name = 'streaming/mis_transmisiones.html'
    context_object_name = 'courses'

    def get_queryset(self):
        qs = Course.objects.filter(tutor=self.request.user, segments__is_live_stream=True).order_by('title').distinct()
        return qs
