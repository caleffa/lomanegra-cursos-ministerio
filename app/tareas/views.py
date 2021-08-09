from rest_framework import views, status, response
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions
from django.db.models import Q
from django.views.generic import ListView

from .models import Tarea, Adjunto, Devolucion, TareaAlumno
from .serializers import TareaSerializer, AdjuntoSerializer
from cursos.models import Course, CourseEnrollment, SegmentTracking

class TareasListView(ListView):
    model = Course
    template_name = 'tareas_page.html'

    def get_queryset(self):
        qs = super(TareasListView, self).get_queryset()
        user = self.request.user
        tarea_segment_ids = Tarea.objects.all().values_list('segmento__course__id', flat=True)
        tracking_segment_id = SegmentTracking.objects.filter(user=user).values_list('video__id', flat=True)
        if user.is_tutor:
            return qs.filter(tutor=user, id__in=tarea_segment_ids)
        else:
            enrollments = CourseEnrollment.objects.filter(user=user)
            return qs.filter(enrollments__in=enrollments, id__in=tarea_segment_ids).filter(id__in=tracking_segment_id)

class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer


class AdjuntoViewSet(viewsets.ModelViewSet):
    queryset = Adjunto.objects.all()
    serializer_class = AdjuntoSerializer


class TareaCreateView(CreateView):
    model = Devolucion
    template_name = 'tarea.html'
    fields = [
        'tarea_alumno',
        'comentario',
        'es_devolucion'
    ]

    def get_success_url(self):
        prev = self.request.POST.get('prev')
        return '/tareas/' + str(self.kwargs['tarea']) + '?prev=' + prev

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prev'] = self.request.GET.get('prev')
        context['tarea'] = Tarea.objects.get(pk=self.kwargs['tarea'])
        context['tutor'] = context['tarea'].segmento.course.tutor
        context['es_tutor'] = context['tutor'] == self.request.user
        if context['es_tutor']:
            context['tarea_alumnos'] = context['tarea'].tarea_alumnos.all()
        else:
            tarea_alumno = context['tarea'].tarea_alumnos.filter(estudiante=self.request.user)
            if tarea_alumno:
                context['tarea_alumnos'] = tarea_alumno
            else:
                context['tarea_alumnos'] = [TareaAlumno.objects.create(
                    tarea=context['tarea'],
                    estudiante=self.request.user
                )]
        return context

    def form_valid(self, form):
        ta = TareaAlumno.objects.get(pk=self.request.POST.get('tarea_alumno'))
        if not ta.aprobada:
            self.object = form.save()
            for f in self.request.FILES.getlist('archivos'):
                adjunto = Adjunto.objects.create(archivo=f)
                self.object.adjuntos.add(adjunto)
        return HttpResponseRedirect(self.get_success_url())


class EliminarDevolucionAPIView(views.APIView):

    permission_classes = [permissions.IsAuthenticated,]
    http_method_names = ['delete']

    def delete(self, request, *args, **kwargs):
        user = request.user

        filt = Q(tarea_alumno__estudiante=user) | Q(tarea_alumno__tarea__segmento__course__tutor=user,
                                                    es_devolucion=True)
        ids = Devolucion.objects.filter(filt).values_list('id', flat=True)
        if self.kwargs['devolucion'] in ids:
            devolucion = Devolucion.objects.get(pk=self.kwargs['devolucion'])
            devolucion.delete()
            return response.Response(data=True, status=status.HTTP_200_OK)
        else:
            return response.Response(data=False, status=status.HTTP_401_UNAUTHORIZED)


class AprobarTareaAlumnoAPIView(views.APIView):

    permission_classes = [permissions.IsAuthenticated,]
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        user = request.user
        tarea_alumno = TareaAlumno.objects.get(pk=self.kwargs['tarea_alumno'])
        if tarea_alumno.tarea.segmento.course.tutor == user:
            tarea_alumno.aprobar()
            return response.Response(data=True, status=status.HTTP_200_OK)
        else:
            return response.Response(data=False, status=status.HTTP_401_UNAUTHORIZED)


