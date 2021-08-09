from django.db import models, transaction
from django.core.validators import FileExtensionValidator
from datetime import datetime
from backoffice.clone import ClonableModelMixin


class Adjunto(ClonableModelMixin, models.Model):
    archivo = models.FileField(upload_to='adjuntos_tareas',
                               validators=[FileExtensionValidator(
                                   allowed_extensions=['gif','jpg','jpeg','png','doc','docx','pdf','xls','xlsx']
                               )])
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def nombre_archivo(self):
        array = self.archivo.name.split("/")
        return array[len(array) - 1]

    #Clonado
    def clone(self, parent_field=None, parent=None):
        original_pk = self.pk
        self.pk = None
        self.save()
        parent.adjuntos.add(self)


class Tarea(ClonableModelMixin, models.Model):
    segmento = models.ForeignKey('cursos.Segment', null=False, on_delete=models.CASCADE)
    titulo = models.CharField(null=False, max_length=200)
    descripcion = models.TextField(null=False)
    obligatoria = models.BooleanField(null=False)
    adjuntos = models.ManyToManyField(to=Adjunto, blank=True)

    @property
    def adjuntos_prop(self):
        return self.adjuntos.all()

    #Clonado
    def clone_children(self, original):
        for ad in original.adjuntos.all():
            ad.clone(parent=self)


class TareaAlumno(models.Model):
    tarea = models.ForeignKey(Tarea, null=False, on_delete=models.CASCADE, related_name='tarea_alumnos')
    estudiante = models.ForeignKey('users.User', null=False, on_delete=models.CASCADE)
    aprobada = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    timestamp_aprobacion = models.DateTimeField(null=True)

    class Meta:
        unique_together = (('tarea', 'estudiante'))

    @property
    def devoluciones(self):
        return self.devolucion_set.order_by('-timestamp').all()

    @transaction.atomic
    def aprobar(self):
        self.aprobada = True
        self.timestamp_aprobacion = datetime.now()
        self.save()
        tracking = self.tarea.segmento.segmenttracking_set.get(user=self.estudiante)
        tracking.update_course_enrollment_status()


class Devolucion(models.Model):
    tarea_alumno = models.ForeignKey(TareaAlumno, on_delete=models.CASCADE)
    comentario = models.TextField(null=False)
    adjuntos = models.ManyToManyField(to=Adjunto)
    timestamp = models.DateTimeField(auto_now_add=True)
    es_devolucion = models.BooleanField(null=False)

    @property
    def archivos_adjuntos(self):
        return self.adjuntos.all()
