from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseServerError
from .models import Course, Segment, SegmentSection, DownloadableDocument, Option, Question, Slide
from .serializers import (CourseSegmentTreeSerializer, SegmentSerializer, SegmentSectionSerializer,
                          DownloadableDocumentSerializer, OptionSerializer, QuestionSerializer, SlideSerializer)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSegmentTreeSerializer


class SegmentViewSet(viewsets.ModelViewSet):
    queryset = Segment.objects.all()
    serializer_class = SegmentSerializer


class LiveStreamSegmentViewSet(viewsets.ModelViewSet):
    queryset = Segment.objects.only_live_stream()
    serializer_class = SegmentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"type_of_segment": Segment.LIVE_STREAM})
        return context

    @detail_route(methods=['post'])
    def start_streaming(self, request, pk=None):
        seg = self.get_object()
        if seg.is_broadcasting_now:
            return HttpResponseServerError(_("Ya existe una transmisión en vivo para el segmento"))
        seg.start_streaming()
        return Response(SegmentSerializer(seg).data)

    @detail_route(methods=['post'])
    def stop_streaming(self, request, pk=None):
        seg = self.get_object()
        if not seg.is_broadcasting_now:
            return HttpResponseServerError(_("No existe una transmisión en vivo para el segmento"))
        seg.stop_streaming()
        return Response(SegmentSerializer(seg).data)

class SegmentSectionViewSet(viewsets.ModelViewSet):
    queryset = SegmentSection.objects.all()
    serializer_class = SegmentSectionSerializer


class DownloadableDocumentViewSet(viewsets.ModelViewSet):
    queryset = DownloadableDocument.objects.all()
    serializer_class = DownloadableDocumentSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class SlideViewSet(viewsets.ModelViewSet):
    queryset = Slide.objects.all()
    serializer_class = SlideSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if hasattr(instance, 'segment'):
            segment = instance.segment
            if instance.next_slide:
                segment.first_slide = instance.next_slide
            else:
                segment.first_slide = None
            segment.save()
        elif instance.previous_slide and instance.next_slide:
            next_slide = instance.next_slide
            prev_slide = instance.previous_slide
            instance.next_slide = None
            instance.save()
            prev_slide.next_slide = next_slide
            prev_slide.save()
        return super().destroy(request, *args, **kwargs)


class SegmentOrderList(generics.ListAPIView):
    serializer_class = SegmentSerializer

    def get_filters(self):
        return models.Q(is_live_stream=False)

    def get_queryset(self):
        course = self.kwargs['course']
        return Segment.objects.filter(course__id=course).filter(self.get_filters()).order_by('order')


class LiveStreamOrderList(SegmentOrderList):
    def get_filters(self):
        return models.Q(is_live_stream=True)


class SegmentSectionOrderList(generics.ListAPIView):
    serializer_class = SegmentSectionSerializer

    def get_queryset(self):
        segment = self.kwargs['segment']
        return SegmentSection.objects.filter(segment__id=segment).order_by('order')
