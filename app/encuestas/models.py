from django.db import models, transaction
from django.db.models import Q
from cursos.models import Course, Area, AllowedDomain
from users.models import User
from ordered_model.models import OrderedModel
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class EncuestaQuerySet(models.QuerySet):
    def targeted_to(self, user):
        target_filter = Q(usuarios_target=user)
        if user.domain:
            domain = AllowedDomain.objects.filter(domain=user.domain).first()
            target_filter = target_filter | Q(dominios_target=domain)
        if user.area:
            target_filter = target_filter | Q(sectores_target=user.area)

        user_courses = Course.objects.filter(enrollments__user=user)

        qf = (target_filter & (Q(cursos__in=user_courses) | Q(cursos=None))) | Q(usuarios_target=None, sectores_target=None, dominios_target=None, cursos__in=user_courses)
        return self.filter(qf)

    def pending_for(self, user):
        targeted = self.targeted_to(user)
        finalizadas = EncuestaTracking.objects.filter(usuario=user, finalizada=True).values_list("encuesta__pk")
        return targeted.exclude(pk__in=finalizadas)

    def mandatory(self):
        return self.filter(obligatoria=True)

    def on_login(self):
        return self.filter(donde=Encuesta.LOGIN)

    def open_now(self):
        qf = Q(vencimiento__gte=timezone.now()) | Q(vencimiento=None)
        qf = qf & Q(inicio__lte=timezone.now())
        return self.filter(qf)

    def snoozed(self, user):
        return self.pending_for(user).filter(trackings__snoozed=True, trackings__finalizada=False, trackings__usuario=user)

    def not_snoozed(self, user):
        snoozed_trackings = EncuestaTracking.objects.filter(usuario=user, finalizada=False, snoozed=True)
        return self.pending_for(user).exclude(trackings__in=snoozed_trackings)

    def on_course_start(self, course):
        return self.filter(cursos=course, donde=Encuesta.INICIO_CURSO)

    def on_course_end(self, course):
        return self.filter(cursos=course, donde=Encuesta.FIN_CURSO)


class Encuesta(models.Model):
    '''
    Modelo para representar encuestas que se les presentan a los usuarios. Pueden ser obligatorias o no, y aparecer en distintos puntos.
    Aquellas que aparecen en el login y son obligatorias no permiten al usuario realizar ninguna acción en la aplicación hasta que
    respondan la encuesta. Si aparecen en el login y no son obligatorias, se le permite al usuario posponerlas. En ese caso, en cada
    nuevo login del usuario, se le volverá a pedir que conteste la encuesta hasta que esta llegue a su fecha de vencimiento (si es que
    tiene).

    Si la encuesta aparece al inicio de un curso y es obligatoria, no permite al usuario avanzar en el curso sin antes contestar la
    encuesta. Si no es obligatoria, se le pregunta cuando ingresa al curso y se le permite posponerla. Si la pospone, se le repregunta
    cuando haga el siguiente login a la aplicación.

    Si la encuesta aparece al final de un curso y es obligatoria, no permite al usuario descargar el certificado de finalización del curso
    hasta que complete la encuesta. Si no es obligatoria, se le permite posponerla (y se le repregunta en cada siguiente login).


    Se puede decidir a quiénes presentar la encuesta de dos maneras: o bien indicando sectores, usuarios o dominios target (cualquiera que
    esté en alguno de esos targets será targeteado, es decir, es un OR), o bien indicando cursos a los que aplica la encuesta.
    Si no se settean los cursos, quiere decir que solo se consideran los atributos de sectores, usuarios o dominios.
    Si se settean los cursos, quiere decir que solo se le aplica la encuesta a aquellos usuarios que están inscriptos en alguno de los
    cursos a los que aplica la encuesta.
    Si tanto los cursos como alguno de los atributos target están setteados, entonces la encuesta aplica solamente a los usuarios
    inscriptos en alguno de los cursos relacionados que además estén alcanzados por alguno de los atributos de target.
    Si no se settea ninguno de los atributos "target", entonces quiere decir que la encuesta aplica a todos los usuarios de cualquiera
    de los cursos relacionados.
    '''
    LOGIN = 'LOGIN'
    FIN_CURSO = 'FIN_CURSO'
    INICIO_CURSO = 'INICIO_CURSO'
    OPCIONES = (
        (LOGIN, _('Al iniciar sesion')),
        (FIN_CURSO, _('Al finalizar un curso')),
        (INICIO_CURSO, _('Al iniciar o continuar un curso')),
    )
    nombre = models.CharField(max_length=200, null=False)
    texto = models.TextField(max_length=200, null=False)
    obligatoria = models.BooleanField(null=False, default=False)
    donde = models.CharField(max_length=50, null=False, choices=OPCIONES, default=INICIO_CURSO)
    cursos = models.ManyToManyField(Course, blank=True)
    inicio = models.DateTimeField(null=False)
    vencimiento = models.DateTimeField(null=True, blank=True)
    imagen = models.ImageField(null=True, upload_to="encuestas", blank=True)
    mensaje_gracias = models.TextField(blank=True)
    sectores_target = models.ManyToManyField(Area, blank=True)
    usuarios_target = models.ManyToManyField(User, blank=True)
    dominios_target = models.ManyToManyField(AllowedDomain, blank=True)

    objects = EncuestaQuerySet.as_manager()

    def __str__(self):
        return self.nombre

    def user_can_answer_now(self, user):
        '''
        Indicates if user can answer this Survey now. It has to be open and the user must be targeted.
        :param user:
        :return: boolean
        '''
        return self in Encuesta.objects.targeted_to(user).open_now()

    @property
    def has_answers(self):
        '''
        Indica si hay alguna Respuesta para alguna Pregunta de esta encuesta.
        :return: boolean
        '''
        return Respuesta.objects.filter(tracking__encuesta=self).exists()

    def set_pregunta_order(self, orden):
        for orden, pid in enumerate(orden):
            p = Pregunta.objects.get(pk=pid)
            p.to(orden + 1)


class Pregunta(OrderedModel):
    EXCLUYENTE = 'EXCLUYENTE'
    ADITIVA = 'ADITIVA'
    TEXTO = 'TEXTO'
    ESTRELLAS = 'ESTRELLAS'
    PULGARES = 'PULGARES'
    OPCIONES = (
        (EXCLUYENTE, _('Pregunta excluyente')),
        (ADITIVA, _('Pregunta aditiva')),
        (TEXTO, _('Pregunta de texto')),
        (ESTRELLAS, _('Calificación con estrellas')),
        (PULGARES, _('Calificación con pulgares')),
    )
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name='preguntas')
    tipo = models.CharField(max_length=20, choices=OPCIONES)
    texto = models.TextField(blank=False)
    imagen = models.ImageField(null=True, upload_to="encuestas/preguntas", blank=True)

    aditiva_debe_contestar_al_menos_una = models.BooleanField(default=True)

    texto_estrella_1 = models.CharField(max_length=40, blank=True)
    texto_estrella_2 = models.CharField(max_length=40, blank=True)
    texto_estrella_3 = models.CharField(max_length=40, blank=True)
    texto_estrella_4 = models.CharField(max_length=40, blank=True)
    texto_estrella_5 = models.CharField(max_length=40, blank=True)

    texto_pulgar_arriba = models.CharField(max_length=40, blank=True)
    texto_pulgar_abajo = models.CharField(max_length=40, blank=True)
    imagen_pulgar_arriba = models.ImageField(null=True, upload_to="encuestas/preguntas", blank=True)
    imagen_pulgar_abajo = models.ImageField(null=True, upload_to="encuestas/preguntas", blank=True)

    # TODO: si la Pregunta es de tipo EXCLUYENTE o ADITIVA, y tiene menos de
    # dos opciones, deberíamos dejarla como "draft" o mostrarle un error
    # al usuario que la está cargando...?

    order_with_respect_to = 'encuesta'


    def __str__(self):
        return f'{self.order} - {self.texto}'


class OpcionPregunta(models.Model):
    ''' En este modelo guardamos las opciones para tipos de preguntas
    EXCLUYENTE o ADITIVA.
    '''
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='opciones',
        limit_choices_to=(Q(tipo=Pregunta.EXCLUYENTE) | Q(tipo=Pregunta.ADITIVA)),
    )
    texto = models.CharField(max_length=128, blank=False)

    class Meta:
        unique_together = [('pregunta', 'texto')]


class EncuestaTracking(models.Model):
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE, related_name="trackings")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    iniciada = models.BooleanField(default=True)
    fecha_inicio = models.DateTimeField(null=True)
    finalizada = models.BooleanField(default=False)
    fecha_finalizacion = models.DateTimeField(null=True)
    snoozed = models.BooleanField(default=False)

    class Meta:
        unique_together = (('encuesta', 'usuario'))

    def get_next_question(self):
        respuesta_ids = self.respuestas.values_list('pregunta__id', flat=True)
        return self.encuesta.preguntas.exclude(id__in=respuesta_ids).order_by('order').first()

    def __esta_finalizada(self):
        return self.get_next_question() is None

    def snooze(self):
        if not self.encuesta.obligatoria:
            self.snoozed = True
            self.iniciada = False
            self.save()
            return True
        return False

    def iniciar(self):
        self.iniciada = True
        self.fecha_inicio = timezone.now()
        self.save()

    def finalizar(self):
        if not self.finalizada:
            self.finalizada = True
            self.fecha_finalizacion = timezone.now()
            self.save()

    def actualizar_estado(self):
        if self.__esta_finalizada():
            self.finalizar()


class Respuesta(models.Model):
    tracking = models.ForeignKey(EncuestaTracking, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)

    texto = models.CharField(max_length=256, blank=True)
    estrellas = models.PositiveSmallIntegerField(null=True, blank=True)
    pulgar = models.BooleanField(null=True)
    opciones = models.ManyToManyField(OpcionPregunta)

    # TODO: validar consistencia (¿en el save?). Si la pregunta es de tipo
    # EXCLUYENTE, la relacion opciones solo puede tener una opcion para
    # la Respuesta
    # Idem con los demás tipos

    class Meta:
        unique_together = (('tracking', 'pregunta'), )

    @transaction.atomic()
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        self.tracking.actualizar_estado()
