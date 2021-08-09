import random
from django.db import models
from django.db.models import Q, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce
from django.utils.translation import ugettext_lazy as _, gettext
from django.db.models.expressions import RawSQL
from django.db import transaction
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator, ValidationError
from model_utils.fields import MonitorField
from solo.models import SingletonModel
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
import calendar
import time

from users.models import User
from tareas.models import TareaAlumno
from video.models import VimeoAPIException, VideoData
from streaming.models import LiveStreamData
from backoffice.clone import ClonableModelMixin

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, Thumbnail, Anchor
from decimal import Decimal
import logging
logger = logging.getLogger()

# Create your models here.

## Modelos de carga de datos:


class SiteSettings(SingletonModel):
    home_video_vimeo_id = models.PositiveIntegerField(default=0)
    requires_allowed_email = models.BooleanField(
        default=True, verbose_name=_('Requiere emails habilitados'),
        help_text=_('Indica si para que un usuario pueda registrarse se requiere que su email se encuentre '
                    'cargado en "Emails habilitados" con anterioridad. En caso de que no se necesita generar '
                    'un Área para utilizar como área por defecto y configurarla')
    )
    default_area = models.ForeignKey(
        'cursos.Area', on_delete=models.PROTECT, null=True, blank=True, verbose_name=_('Área por defecto'),
        help_text=_('Es el área que se asignará a los usuarios que se registren sin que previamente exista '
                    'un "Email habilitado" para ellos')
    )

    def clean(self):
        super().clean()

        if not self.requires_allowed_email and self.default_area is None:
            raise ValidationError(
                gettext('Cuando no se requieren los emails habilitados debe configurar un área por defecto')
            )


class ReArrangeManagerMixin(models.Manager):

    @transaction.atomic()
    def rearrange_orders(self, parent=None, parent_attr=None, leave_gap=None, move_into_gap=None, subset_filter=None):
        """
        Modificamos el orden de todos las instancias del modelo manejado que estén asociadas a parent
        para que queden con números consecutivos a partir del 1.
        :param parent: objeto al que deben estar relacionados
        :param parent_attr: string. Atributo que tiene la foreign key a parent
        :param leave_gap: int. Si queremos que deje un hueco en la posición esa.
        :param move_into_gap: objeto (existente) que queremos que vaya al gap
        :param subset_filter: expresión para dividir el queryset en subconjuntos que serán ordenados individualmente
        """
        if parent:
            filter_dict = {parent_attr: parent}
            objects = self.filter(**filter_dict)
        else:
            objects = self
        if subset_filter:
            ReArrangeManagerMixin._reorder(objects.filter(subset_filter), leave_gap, move_into_gap)
        else:
            ReArrangeManagerMixin._reorder(objects, leave_gap, move_into_gap)

    @staticmethod
    @transaction.atomic()
    def _reorder(objects, leave_gap=None, move_into_gap=None):
        if objects:
            objects = objects.order_by('order')
            order = 1
            unused_order = objects.aggregate(models.Max('order'))['order__max'] + 1
            if move_into_gap:
                objects = objects.exclude(id=move_into_gap.id)
                move_into_gap.order = unused_order
                move_into_gap.save()
                unused_order += 1
            for obj in objects:
                if leave_gap and order == leave_gap:
                    order += 1
                    for other_obj in objects.all().filter(order=leave_gap):
                        # muevo los que estén en el gap para afuera
                        other_obj.order = unused_order
                        other_obj.save()
                        unused_order += 1
                    if move_into_gap:
                        move_into_gap.order = leave_gap
                        move_into_gap.save()
                for other_obj in objects.all().filter(order=order).exclude(id=obj.id):
                    other_obj.order = unused_order
                    other_obj.save()
                    unused_order += 1
                if obj.order != order:
                    obj.order = order
                    obj.save()
                order += 1
            else:
                if leave_gap and move_into_gap:
                    move_into_gap.order = leave_gap
                    move_into_gap.save()


class CourseQueryset(models.QuerySet):
    def allows_user(self, user):
        qf = Q(enrollments__user=user) | Q(enabled_users=user)
        if user.area:
            qf = qf | Q(enabled_areas=user.area)
        qf = qf | Q(enabled_domains__domain__iexact=user.domain)

        return self.filter(qf).distinct()

    def with_count_of_potential_users(self):
        return self.annotate(
            potential_users=RawSQL('''SELECT COUNT(DISTINCT u.id) FROM
                users_user u
                LEFT JOIN users_user_enabled_courses uec ON uec.user_id = u.id
                LEFT JOIN cursos_courseenrollment ce on ce.user_id = u.id
                LEFT JOIN cursos_alloweddomain ad ON LOWER(ad.domain) = LOWER(u.domain)
                LEFT JOIN cursos_alloweddomain_enabled_courses adec ON adec.alloweddomain_id = ad.id
                LEFT JOIN cursos_allowedemail ae ON ae.user_id = u.id
                LEFT JOIN cursos_area_enabled_courses aec ON aec.area_id = ae.area_id
            WHERE (ce.course_id = cursos_course.id)
            OR (uec.course_id = cursos_course.id)
            OR (adec.course_id = cursos_course.id)
            OR (aec.course_id = cursos_course.id)''', [], output_field=models.IntegerField())
        )

    def started_with_user(self, user):
        return self.allows_user(user).filter(start_date__lte=timezone.now())


class CareerTrackManager(models.Manager):
    def with_courses(self, user):
        categories = Category.objects.with_courses(user)
        return self.filter(categories__in=categories).distinct()


class CareerTrack(models.Model):
    title = models.CharField(max_length=120, verbose_name=_('Título'))
    image = models.ImageField(blank=True, upload_to="career_track_thumbnails")
    order = models.PositiveIntegerField(unique=True)

    objects = CareerTrackManager()

    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')

    def __str__(self):
        return self.title


class CategoryManager(models.Manager):
    def with_courses(self, user):
        courses = Course.objects.started_with_user(user)
        return self.filter(courses__in=courses).distinct()


class Category(models.Model):
    title = models.CharField(max_length=120, verbose_name=_('Título'))
    image = models.ImageField(blank=True, upload_to="category_thumbnails")
    order = models.PositiveIntegerField(unique=True)
    career_tracks = models.ManyToManyField(CareerTrack, related_name='categories', blank=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = _('Subcategoría')
        verbose_name_plural = _('Subcategorías')

    def __str__(self):
        return self.title


class Course(ClonableModelMixin, models.Model):
    CURRENCY_ARS = 'ARS'
    CURRENCY_BRL = 'BRL'
    CURRENCY_USD = 'USD'
    CURRENCIES = [
        (CURRENCY_ARS, _('$ Argentinos')),
        (CURRENCY_BRL, _('R$ Real')),
        (CURRENCY_USD, _('u$s Dólar EEUU')),
    ]
    title = models.CharField(max_length=128, verbose_name=_('Título'))
    description = models.TextField(verbose_name=_('Descripción'))
    slug = models.SlugField(unique=True)
    image = models.ImageField(blank=True, upload_to="course_thumbnails")
    course_list_thumbnail = ImageSpecField(processors=[Thumbnail(width=55, height=55, anchor=Anchor.CENTER)], source='image', format='PNG')
    course_carousel_thumbnail = ImageSpecField(processors=[Thumbnail(width=70, height=70, anchor=Anchor.CENTER)], source='image', format='PNG')
    order = models.PositiveIntegerField(null=True)  # TODO hacer not null y unique
    certificate_template = models.ImageField(null=True, blank=True, upload_to="course_certificate", verbose_name=_('Plantilla del certificado'))
    start_date = models.DateTimeField(null=False, blank=False)
    categories = models.ManyToManyField(Category, related_name='courses')
    tutor = models.ForeignKey('users.User', null=True, related_name='tutored_courses', limit_choices_to={'is_tutor': True}, on_delete=models.SET_NULL, blank=True)

    # Campos para precio
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Costo'), default=Decimal(0))
    price_currency = models.CharField(max_length=3, choices=CURRENCIES, verbose_name=_('Moneda'), default=CURRENCY_BRL)

    # Manager
    objects = ReArrangeManagerMixin.from_queryset(CourseQueryset)()

    class Meta:
        verbose_name = _('Curso')
        verbose_name_plural = _('Cursos')
        ordering = ['order']

    def __str__(self):
        return self.title

    def delete(self, **kwargs):
        ret = super().delete(**kwargs)
        Course.objects.rearrange_orders()
        return ret

    @property
    def first_segment(self):
        # TODO: reimplementar para distinguir por tipo de segmento
        try:
            return Segment.objects.filter(course=self, is_live_stream=False).earliest('order')
        except Segment.DoesNotExist:
            return None

    @property
    def first_segment_url(self):
        first_segment = self.first_segment
        if first_segment:
            return first_segment.get_object_url()
        else:
            return None

    @property
    def first_segment_is_enabled(self):
        segment = self.first_segment
        return segment and segment.is_enabled

    @property
    def users_allowed_to_enroll(self):
        user_domain = Subquery(
            AllowedDomain.objects.filter(domain__iexact=OuterRef('domain'), enabled_courses=self).values('id')[:1],
            output_field=models.IntegerField()
        )
        qs = User.objects.annotate(
            allowed_domain=user_domain
        )
        query_filter = (Q(enabled_courses=self) | Q(allowed_email__area__enabled_courses=self) |
                        Q(enrollments__course=self) | Q(allowed_domain__isnull=False))
        return qs.filter(query_filter)

    def user_allowed_to_enroll(self, user):
        return self.users_allowed_to_enroll.filter(id=user.id).exists()

    @property
    def es_pago(self) -> bool:
        return self.price and self.price > 0

    def usuario_ya_pago(self, user) -> bool:
        oc = self.ordenes_de_compra.filter(usuario=user).prefetch_related('pagos').first()
        if oc:
            for p in oc.pagos.all():
                if p.pagado:
                    return True
        return False

    @property
    def allowed_users(self):
        qf = Q(enrollments__course=self) | Q(enabled_courses__pk=self.pk)
        qf = qf | Q(domain__in=self.enabled_domains.all().values_list('domain'))
        return User.objects.all().filter(qf)

    @property
    def live_segments(self):
        return self.segments.filter(is_live_stream=True)

    @property
    def non_live_segments(self):
        return self.segments.filter(is_live_stream=False)

    @property
    def non_live_segments_count(self):
        return self.non_live_segments.count()

    @property
    def live_now(self):
        return self.segments.filter(broadcasts__is_live=True).distinct()

    @property
    def live_soon(self):
        return self.segments.filter(broadcasts__is_live=False, broadcasts__date__gte=timezone.now()).distinct()

    #Clonado
    @transaction.atomic
    def clone(self, parent_field=None, parent=None):
        original_pk = self.pk
        self.pk = None
        ts = calendar.timegm(time.gmtime())
        self.slug = self.slug + '-' + str(ts)
        self.title = self.title + ' - ' + gettext('Copia')
        self.save()
        original = Course.objects.get(pk=original_pk)
        self.clone_children(original)
        return self

    def clone_children(self, original):
        for seg in original.segments.all():
            seg.clone('course', self)


class Slide(ClonableModelMixin, models.Model):
    image = models.ImageField(upload_to="slides")
    next_slide = models.OneToOneField('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='previous_slide')

    #Clonado
    def clone(self, parent_field=None, parent=None):
        original_pk = self.pk
        self.pk = None
        self.next_slide = None
        self.save()
        original = Slide.objects.get(pk=original_pk)
        parent.next_slide = self
        parent.save()
        if original.next_slide:
            original.next_slide.clone(parent=self)
        


class SegmentQueryset(models.QuerySet):
    def for_user(self, user):
        return self.filter(course__enrollments__user=user)

    def only_live_stream(self):
        return self.filter(is_live_stream=True)

    def with_current_live_broadcast(self):
        return self.only_live_stream().filter(broadcasts__is_live=True).distinct()

    # filtra los segmentos que tienen transmisiones en vivo programadas para el futuro y NO están en vivo en el momento
    def with_following_broadcast(self, dt=None):
        if not dt:
            dt = timezone.localtime()
        return self.only_live_stream().exclude(broadcasts__is_live=True).filter(broadcasts__date__gt=dt).distinct()


class GeniallyData(models.Model):
    genially_id = models.CharField(max_length=128, blank=True, default='')

    class Meta:
        abstract = True


class BaseSegment(models.Model):
    title = models.CharField(max_length=128)
    order = models.PositiveIntegerField()
    VIDEO = 'V'
    SLIDES = 'S'
    LIVE_STREAM = 'L'
    GENIALLY = 'G'
    GENERIC = 'X'
    TYPE_OF_SEGMENT = (
        (VIDEO, _('Video')),
        (SLIDES, _('Slide')),
        (LIVE_STREAM, _('Live')),
        (GENIALLY, _('Genially')),
        (GENERIC, _('Genérico')),
    )
    type_of_segment = models.CharField(
        max_length=1,
        choices=TYPE_OF_SEGMENT,
        default=VIDEO,
    )
    thumb_path = models.URLField(blank=True)
    thumbnail = models.ImageField(null=True, upload_to='segment_thumbnails', blank=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.type_of_segment == self.VIDEO and self.vimeo_id:
            try:
                vimeo_data = self.load_from_vimeo()
                self.thumb_path = vimeo_data.get('thumb_path', self.thumb_path)
            except VimeoAPIException as e:
                logger.exception('Error intentando obtener los datos desde vimeo')
                raise ValidationError(_('No se pudo obtener la información del video desde VIMEO'))
        elif Segment.SLIDES:
            self.thumb_path = ''
            self.duration = None

    @property
    def thumbnail_url(self):
        if self.type_of_segment == self.VIDEO and self.vimeo_id and self.thumb_path:
            return self.thumb_path
        elif self.type_of_segment == self.SLIDES and self.first_slide:
            return self.first_slide.image.url
        else:
            if self.thumbnail:
                return self.thumbnail.url
            else:
                return None


class GenericData(models.Model):
    embed_code = models.TextField(blank=True, default='')

    class Meta:
        abstract = True


class Segment(GenericData, VideoData, LiveStreamData, GeniallyData, ClonableModelMixin, BaseSegment):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='segments')


    first_slide = models.OneToOneField(Slide, null=True, blank=True, on_delete=models.PROTECT, related_name='segment')
    max_retries = models.PositiveIntegerField(default=0)  # Cantidad maxima de intentos de responder el cuestionario que permitimos. Si es 0, es ilimitado.
    min_correct_questions = models.PositiveIntegerField(default=0)  # representa la cantidad de preguntas que hay que responder correctamente para avanzar al siguiente video
    enabled_since = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de habilitación'),
                                         help_text=_('Indica a partir de qué fecha se puede acceder a este segmento'))
    is_live_stream = models.BooleanField(default=False, db_index=True)
    requires_full_watch = models.BooleanField(default=True,  db_index=True,
                                              help_text=_('Indica si se requiere que el alumno mire todo el video antes'
                                                          ' de poder continuar.'))

    # modalidad: abierto (transmisión espontánea) o por fechas preanunciadas
    OPEN_ANNOUNCEMENT_TYPE = 'O'
    FIXED_DATE_ANNOUNCEMENT_TYPE = 'F'
    ANNOUNCEMENT_TYPES = (
        (OPEN_ANNOUNCEMENT_TYPE, 'Open'),
        (FIXED_DATE_ANNOUNCEMENT_TYPE, 'Fixed dates'),
    )
    announcement_type = models.CharField(max_length=1, choices=ANNOUNCEMENT_TYPES, default=OPEN_ANNOUNCEMENT_TYPE)

    objects = ReArrangeManagerMixin.from_queryset(SegmentQueryset)()

    class Meta:
        unique_together = [('course', 'order', 'is_live_stream'),]
        ordering = ['course', 'order']

    def __str__(self):
        return f"{self.course} - {self.order} - {self.title}"

    def get_object_url(self):
        if self.type_of_segment == Segment.VIDEO:
            return reverse('video', kwargs={'course': self.course.slug, 'order': self.order})
        elif self.type_of_segment == Segment.SLIDES:
            return reverse('slide', kwargs={'course': self.course.slug, 'order': self.order})
        elif self.type_of_segment == Segment.LIVE_STREAM:
            return reverse('live', kwargs={'course': self.course.slug, 'order': self.order})
        elif self.type_of_segment == Segment.GENIALLY:
            return reverse('genially', kwargs={'course': self.course.slug, 'order': self.order})
        elif self.type_of_segment == Segment.GENERIC:
            return reverse('generic', kwargs={'course': self.course.slug, 'order': self.order})

    @property
    def is_enabled(self):
        if not self.enabled_since or self.enabled_since < timezone.now():
            return True
        else:
            return False

    @property
    def forums(self):
        return self.forum_set.all()

    @property
    def tareas(self):
        return self.tarea_set.all()

    def is_last(self):
        if self == Segment.objects.filter(course=self.course, is_live_stream=self.is_live_stream).latest('order'):
            return True
        else:
            return False

    def has_documents(self):
        if self.downloadabledocument_set.all():
            return True
        else:
            return False

    def has_questions(self):
        for s in self.sections.all():
            if s.has_questions():
                return True
        return False

    def previous_segment(self):
        if self.order > 1:
            return Segment.objects.filter(
                course=self.course, order__lt=self.order, is_live_stream=self.is_live_stream
            ).latest('order')
        else:
            return None

    def next_segment(self):
        try:
            return Segment.objects.filter(
                course=self.course, order__gt=self.order, is_live_stream=self.is_live_stream
            ).earliest('order')
        except ObjectDoesNotExist:
            return None

    def last_segment(self):
        try:
            return Segment.objects.filter(course=self.course, is_live_stream=self.is_live_stream).last('order')
        except ObjectDoesNotExist:
            return None

    @property
    def slides(self):
        if self.type_of_segment == Segment.SLIDES:
            res = []
            next_slide = self.first_slide
            while next_slide:
                res.append(next_slide)
                next_slide = next_slide.next_slide
            return res
        return []

    def delete(self, using=None, keep_parents=False):
        is_live_stream = self.is_live_stream
        ret = super().delete(using=using, keep_parents=keep_parents)
        Segment.objects.rearrange_orders(
            parent=self.course,
            parent_attr='course',
            subset_filter=Q(is_live_stream=is_live_stream)
        )
        return ret

    def user_has_pending_tareas(self, user):
        tareas = self.tareas.filter(obligatoria=True)
        tas = TareaAlumno.objects.filter(tarea__in=tareas, estudiante=user)
        if tareas.count() > 0 >= tas.count() or tas.filter(aprobada=False):
            return True
        return False

    @property
    def next_broadcast(self):
        return self.broadcasts.filter(date__gte=timezone.now(), is_live=False).order_by('date').first()

    @property
    def currently_live_broadcast(self):
        # debería haber sólo uno?
        return self.broadcasts.currently_live().first()

    @property
    def transmision_date(self):
        bc = self.next_broadcast
        return bc.date if bc else None

    @property
    def is_broadcasting_now(self):
        return self.is_live_stream and self.broadcasts.currently_live().exists()

    @property
    def fixed_dates_broadcast(self):
        now = timezone.localtime()
        dates = (self.broadcasts.after(now).values('date')
                 if self.announcement_type == Segment.FIXED_DATE_ANNOUNCEMENT_TYPE
                 else [])
        return {'dates': dates}

    @property
    def open_broadcast(self):
        date = (self.next_broadcast.date
                if self.announcement_type == Segment.OPEN_ANNOUNCEMENT_TYPE and self.next_broadcast
                else None)
        return {'open_broadcast_date': date}

    def set_as_vimeo(self, vimeo_id):
        self.is_live_stream = False
        self.vimeo_id = vimeo_id

    def set_as_genially(self, genialy_id):
        self.is_live_stream = False
        self.genially_id = genialy_id

    def set_as_generic(self, embed_code):
        self.embed_code = embed_code
        self.is_live_stream

    def set_as_live_stream(self, rtmp_url, stream_key, announcement_type):
        self.is_live_stream = True
        self.announcement_type = announcement_type
        self.rtmp_url = rtmp_url or ''
        self.stream_key = stream_key

    # crea un nuevo broadcast copiando los datos de video y streaming del segmento
    def create_broadcast(self, date=None):
        self.broadcasts.create(
            date=date,
            vimeo_id=self.vimeo_id,
            rtmp_url=self.rtmp_url,
            stream_key=self.stream_key,
        )

    # asigna los datos de video y streaming del segmento al broadcast
    def update_broadcast(self, broadcast):
        broadcast.vimeo_id = self.vimeo_id
        broadcast.rtmp_url = self.rtmp_url
        broadcast.stream_key = self.stream_key
        broadcast.save()

    def start_streaming(self):
        if not self.is_broadcasting_now:
            bc = self.next_broadcast
            if not bc:
                bc = self.broadcasts.create(date=timezone.localtime())
            bc.set_live()

    def stop_streaming(self):
        if self.is_broadcasting_now:
            bc = self.currently_live_broadcast
            bc.set_off()

    #Clonado
    def clone(self, parent_field=None, parent=None):
        original_pk = self.pk
        self.pk = None
        self.first_slide = None
        self.course = parent
        self.save()
        original = Segment.objects.get(pk=original_pk)
        self.clone_children(original)

    def get_or_create_tracking(self,  user):
        return SegmentTracking.objects.get_or_create(
            video=self, user=user,
            defaults={
                'watched_full': not self.requires_full_watch
            }
        )

    def clone_children(self, original):
        for bro in original.broadcasts.all():
            bro.clone('segment', self)

        for dd in original.downloadabledocument_set.all():
            dd.clone('video', self)

        for tar in original.tarea_set.all():
            tar.clone('segmento', self)

        for forum in original.forum_set.all():
            forum.clone('segment', self)
            
        for sec in original.sections.all():
            sec.clone('segment', self)

        if original.first_slide:
            original.first_slide.clone(parent=self)


class SegmentSection(ClonableModelMixin, models.Model):
    '''
    Representa un concepto para agrupar preguntas. Es deseable que haya varias preguntas sobre un mismo concepto.
    En un Segmento (video o slides) puede haber varios conceptos. Entonces se quiere poder agrupar las preguntas
    por cada concepto, en vez de agrupar todas las preguntas al mismo Segmento.
    '''
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE, related_name='sections')
    order = models.PositiveSmallIntegerField()
    questions_to_ask = models.PositiveIntegerField(default=0, help_text=_('''Es la cantidad de preguntas a utilizar para 
        armar el cuestionario. Si es 0 se utilizan siempre todas. Si es N mayor a 0 el cuestionario se arma toman N 
        preguntas de las que haya definidas para este segmento. Si hay definidas menos de N se tomarán todas.'''))

    objects = ReArrangeManagerMixin()

    class Meta:
        unique_together = [('segment', 'order')]
        ordering = ['segment', 'order']

    def has_questions(self):
        if self.question_set.count() > 0:
            return True
        else:
            return False

    def __str__(self):
        return f'{self.segment}:{self.order}'

    def delete(self, using=None, keep_parents=False):
        ret = super().delete(using=using, keep_parents=keep_parents)
        SegmentSection.objects.rearrange_orders(parent=self.segment, parent_attr='segment')
        return ret

    #Clonado
    def clone_children(self, original):
        for ques in original.question_set.all():
            ques.clone('section', self)


class DownloadableDocument(ClonableModelMixin, models.Model):
    video = models.ForeignKey(Segment, on_delete=models.PROTECT)
    name = models.CharField(max_length=128, blank=True)
    document = models.FileField(upload_to="video_documents")
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        import os
        path = os.path.split(self.document.name)
        return self.name if self.name else path[-1]


class Question(ClonableModelMixin, models.Model):
    section = models.ForeignKey(SegmentSection, on_delete=models.PROTECT, null=True)
    text = models.TextField()
    image = models.ImageField(blank=True, upload_to="question_images")
    has_only_one_correct_answer = models.BooleanField(default=True)
    show_correct_options = models.PositiveIntegerField(default=1)
    show_incorrect_options = models.PositiveIntegerField()
    text_after_correct_answer = models.TextField(blank=True)
    text_after_incorrect_answer = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.section.segment.course} - {self.section.segment.title}] {self.text}"
    # TODO: validator if has_only_one_correct_answer  ==> show_correct_options = 1

    #Clonado
    def clone_children(self, original):
        for op in original.option_set.all():
            op.clone('question', self)


class Option(ClonableModelMixin, models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    text = models.CharField(max_length=256)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return f"({'T' if self.is_correct else 'F'}) {self.text}"

## Modelos de tracking de usuarios:

class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_query_name='enrollments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_query_name='enrollments')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_complete = models.BooleanField(default=False)  # Aca por ahora solo marcamos si ya respondió todos los cuestionarios (bien o mal), que es lo mismo que te da has_answered_all_questionnaires
    next_allowed_video = models.ForeignKey(Segment, on_delete=models.PROTECT, null=True)

    class Meta:
        unique_together = (('course', 'user'))

    def has_answered_all_questionnaires(self):
        for video in Segment.objects.filter(course=self.course):
            try:
                vt = SegmentTracking.objects.get(video=video, user=self.user)
                if not vt.has_answered_questionnaire:
                    return False
            except ObjectDoesNotExist:
                return False
        return True

    @property
    def first_segment(self):
        return self.course.first_segment

    @property
    def next_segment(self):
        if self.is_complete:
            return self.first_segment
        else:
            if self.next_allowed_video:
                return self.next_allowed_video
            else:
                return self.first_segment

    @property
    def next_segment_is_enabled(self):
        segment = self.next_segment
        return segment and segment.is_enabled

    def next_url(self):
        # returns the url to the next pending action
        if self.is_complete:
            return reverse('course', kwargs={'course': self.course.slug})
        else:
            if not self.next_allowed_video:
                # voy al primer segmento
                return self.course.first_segment_url
            return self.next_allowed_video.get_object_url()

    def update_next_allowed_video(self, next_segment):
        next_allowed = self.next_allowed_video

        # Si el próximo segmento es None, lo dejo como está
        if next_segment:
            if next_allowed:
                if next_allowed.order < next_segment.order:
                    # Solo actulizo si el próximo segmento pasado es posterior
                    # al próximo habilitado de este enrollment.
                    self.next_allowed_video = next_segment
            else:
                # Si el próximo habilitado es None, entonces lo actualizo sin importar cuál
                # es el próximo segmento pasado
                self.next_allowed_video = next_segment

def emptyPartsWatched():
    return []


class SegmentTracking(models.Model):
    video = models.ForeignKey(Segment, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    started_timestamp = models.DateTimeField(auto_now_add=True)
    last_watch = models.DateTimeField(auto_now=True)
    watched_full = models.BooleanField(default=False)
    watched_full_at = models.DateTimeField(null=True)
    parts_watched = ArrayField(models.PositiveIntegerField(), default=emptyPartsWatched)
    last_part_watched = models.PositiveIntegerField(default=0)
    slides_seen = ArrayField(models.PositiveIntegerField(), default=emptyPartsWatched)
    user_has_downloaded_all_documents = models.BooleanField(default=False)
    last_slide_shown = models.ForeignKey(Slide, on_delete=models.PROTECT, null=True, blank=True)
    has_passed_questionnaire = models.BooleanField(default=False)

    @transaction.atomic
    def update_course_enrollment_status(self):
        course_enrollment = CourseEnrollment.objects.get(course=self.video.course, user=self.user)
        finished_course = False
        must_complete_questionnaire = False

        tareas_pendientes = self.tiene_tareas_obligatorias_pendientes
        cuestionario_completo = self.has_passed_questionnaire
        if cuestionario_completo and not tareas_pendientes:
            if self.video.is_last():
                course_enrollment.is_complete = True
                course_enrollment.save()
                finished_course = True
                course_enrollment.refresh_from_db()
            else:
                course_enrollment.update_next_allowed_video(self.video.next_segment())
                course_enrollment.save()
        else:
            pass

        if not cuestionario_completo:
            must_complete_questionnaire = True

        return course_enrollment, finished_course, must_complete_questionnaire, tareas_pendientes
    
    def get_downloadable_documents_and_tracking(self):
        documents = DownloadableDocument.objects.filter(video=self.video)
        trackings = DownloadableDocumentTracking.objects.filter(document__video=self.video, user=self.user)
        res = {}
        for doc in documents:
            try:
                res[doc] = trackings.get(document=doc)
            except ObjectDoesNotExist:
                res[doc] = None
        return res

    def get_pending_downloads(self):
        # Este método solo devuelve una lista de IDs de los documentos obligatorios que falta descargar
        docs_and_tracking = self.get_downloadable_documents_and_tracking()
        return [doc.id for doc,tracking in docs_and_tracking.items() if not tracking and doc.is_mandatory]

    @property
    def tareas_obligatorias_pendientes(self):
        return self.video.tarea_set.filter(obligatoria=True).annotate(
            completas=Count(
                'tarea_alumnos', distinct=True,
                filter=models.Q(tarea_alumnos__estudiante=self.user, tarea_alumnos__aprobada=True)
            )
        ).filter(completas__lt=1)

    @property
    def tiene_tareas_obligatorias_pendientes(self):
        return self.tareas_obligatorias_pendientes.exists()

    @property
    def has_answered_questionnaire(self):
        return self.has_passed_questionnaire

    @property
    def total_questions_to_ask(self):
        total = 0
        for section in SegmentSection.objects.filter(segment=self.video):
            questions = Question.objects.filter(section=section)
            if section.questions_to_ask > 0:
                total += questions[:section.questions_to_ask].count()
            else:
                total += questions.count()
        return total

    @property
    def total_correct_answered_questions(self):
        total = 0
        questionnaires = Questionnaire.objects.filter(video=self.video, user=self.user, is_complete=True).order_by('-creation_timestamp')
        if questionnaires.exists():
            for ques in questionnaires:
                total = ques.questionnairequestion_set.filter(answered_correctly=True).count()
                if ques.has_passed:
                    break
        return total

    @property
    def total_tries(self):
        total = 0
        questionnaires = Questionnaire.objects.filter(video=self.video, user=self.user, is_complete=True).order_by('creation_timestamp')
        for question in questionnaires:
            total += 1
            if question.has_passed:
                break
        return total
    
    @property
    def last_state_timestamp(self):
        timestamp = None
        questionnaires = Questionnaire.objects.filter(video=self.video, user=self.user).order_by('-creation_timestamp')
        if questionnaires.exists():
            for quest in questionnaires:
                timestamp = quest.creation_timestamp
                if quest.has_passed:
                    break
        return timestamp
        
    @property
    def continue_from(self):
        continue_from = self.last_part_watched - 5
        return continue_from if continue_from > 0 else 0

    def can_answer_questionnaire(self):
        if not self.video.has_questions():
            return False
        if self.watched_full:
            if self.get_pending_downloads():    # this works because empty list casts to False
                if self.user_has_downloaded_all_documents:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False


    class Meta:
        unique_together = (('video', 'user'), )
        # DUDA: es más fácil tener uno solo de cada par usuario-video
        # pero quizás quieren saber si la persona vio dos veces
        # el mismo video?

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.video.type_of_segment in Segment.LIVE_STREAM:
            self.watched_full = True
            self.watched_full_at = timezone.now()
        else:
            if self.video.type_of_segment == Segment.GENIALLY or self.video.type_of_segment == Segment.GENERIC:
                self.watched_full = True
                self.watched_full_at = timezone.now()
            elif self.video.type_of_segment == Segment.VIDEO:
                self.parts_watched = sorted(list(set(self.parts_watched)))

                duration = self.video.duration
                seconds = range(duration+1)

                to_watch = list(set(seconds) - set(self.parts_watched))

                # La duración que se obtiene con la API está redondeada así que tenemos que habilitar
                # la posibilidad de que el último segundo no forme parte de los segundos vistos
                if len(to_watch) == 0 or (len(to_watch) == 1 and to_watch[0] == duration):
                    self.watched_full = True
                    if not self.watched_full_at:
                        self.watched_full_at = datetime.now()
            elif self.video.type_of_segment == Segment.SLIDES:
                # Siempre agrego la ultima slide que vio a la lista de las ya vistas
                if self.last_slide_shown:
                    seen_slides = self.slides_seen
                    seen_slides.append(self.last_slide_shown.id)
                    self.slides_seen = sorted(list(set(seen_slides)))

                    if not self.last_slide_shown.next_slide:
                        self.watched_full = True
                        if not self.watched_full_at:
                            self.watched_full_at = datetime.now()

            if self.watched_full and not self.video.has_questions() and not self.video.downloadabledocument_set.filter(is_mandatory=True):
                course_enrollment = CourseEnrollment.objects.get(course=self.video.course, user=self.user)
                if self.video.is_last():
                    # se termino de ver el ultimo video y no tiene ni documento ni preguntas
                    # entonces termino el curso
                    course_enrollment.is_complete = True
                else:
                    course_enrollment.update_next_allowed_video(self.video.next_segment())
                course_enrollment.save()

        super(SegmentTracking, self).save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class DownloadableDocumentTracking(models.Model):
    document = models.ForeignKey(DownloadableDocument, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    first_download_timestamp = models.DateTimeField(auto_now_add=True)
    times_downloaded = models.PositiveIntegerField(default=1)
    last_download_timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['document', 'user'], ]

    def __str__(self):
        return f"{self.user} - {self.document}"


class QuestionnaireManager(models.Manager):
    def create_questionnaire(self, video, user):
        questionnaire = self.create(video=video, user=user)

        sections = video.sections.all()

        # Orden global de las preguntas del cuestionario
        order = 1

        for section in sections:
            questions = Question.objects.filter(section=section).order_by('?') # Orden random

            # Si hay una cantidad de preguntas definidas
            # armo el cuestionario con esa cantidad de preguntas.
            if section.questions_to_ask:
                questions = questions[:section.questions_to_ask]

            for q in questions:
                questionnaire_question = QuestionnaireQuestion.objects.create(order=order, questionnaire=questionnaire, question=q)
                # TODO: por ahora admitimos una sola respuesta correcta
                options_to_add = []
                correct_answer = Option.objects.filter(question=q, is_correct=True).order_by('?')[0]
                options_to_add.append(correct_answer)

                wrong_answers = Option.objects.filter(question=q, is_correct=False).order_by('?')[:q.show_incorrect_options]
                options_to_add.extend(wrong_answers)

                random.shuffle(options_to_add)

                for option in options_to_add:
                    QuestionnaireOption.objects.create(questionnaire_question=questionnaire_question, option=option)
                order += 1

        return questionnaire


class Questionnaire(ClonableModelMixin, models.Model):
    video = models.ForeignKey(Segment, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    is_complete = models.BooleanField(default=False)
    score = models.IntegerField(null=True)  # TODO: por ahora vamos a usar un valor entre 0 y 100
    questions = models.ManyToManyField(Question, through='QuestionnaireQuestion')
    creation_timestamp = models.DateTimeField(auto_now_add=True)
    has_passed = models.BooleanField(default=False)

    objects = QuestionnaireManager()

    


class QuestionnaireQuestion(models.Model):
    order = models.PositiveIntegerField()
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    options = models.ManyToManyField(Option, through='QuestionnaireOption')
    answered = models.BooleanField(default=False)
    answer_timestamp = MonitorField(monitor='answered')
    answered_correctly = models.BooleanField(null=True, default=None)


class QuestionnaireOption(models.Model):
    questionnaire_question = models.ForeignKey(QuestionnaireQuestion, on_delete=models.PROTECT)
    option = models.ForeignKey(Option, on_delete=models.PROTECT)
    selected_by_user = models.BooleanField(null=True, default=None)


class Area(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name=_('Nombre'),
                            help_text=_('Nombre del área/departamento/sector'))
    enabled_courses = models.ManyToManyField(Course, related_name='enabled_areas', blank=True,
                                             verbose_name=_('Cursos habilitados'),
                                             help_text=_('Son los cursos que podrán realizar los usuarios que pertenezcan'
                                                       ' a esta área'))

    class Meta:
        ordering = ['name']
        verbose_name = _('Área/Departamento/Sector')
        verbose_name_plural = _('Áreas/Departamentos/Sectores')

    def get_enabled_courses_display(self):
        return ' | '.join((c.title for c in self.enabled_courses.all()))
    get_enabled_courses_display.short_description = _('Cursos habilitados')

    def __str__(self):
        return self.name


def no_at_validator(value):
    if value is not None:
        if '@' in value:
            raise ValidationError(message=_('Debe ingresar el dominio sin la "@"'))


class AllowedDomain(models.Model):
    domain = models.CharField(max_length=63, unique=True,
                              validators=[RegexValidator(EmailValidator.domain_regex,
                                                         message=_('El valor ingresado no es un dominio válido')),
                                          no_at_validator],
                              verbose_name=_('Dominio'),
                              help_text=_('Un dominio de internet sin incluir la @. Por ejemplo, para habilitar todos los mails "@gmail.com", ingrese "gmail.com"'))
    enabled_courses = models.ManyToManyField(Course, blank=True, related_name='enabled_domains')

    def get_enabled_courses_display(self):
        return ' | '.join((c.title for c in self.enabled_courses.all()))
    get_enabled_courses_display.short_description = _('Cursos habilitados')

    def __str__(self):
        return self.domain

    class Meta:
        verbose_name = _('Dominio habilitado')
        verbose_name_plural = _('Dominios habilitados')


class AllowedEmail(models.Model):
    email = models.EmailField(unique=True)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, null=True, blank=True,
                             verbose_name=_('Área/Departamento/Sector'),
                             help_text=_('Es el área a la cual pertenece este usuario'))
    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, verbose_name=_('Usuario'),  blank=True,
                                related_name='allowed_email')

    class Meta:
        verbose_name = _('email habilitado')
        verbose_name_plural = _('emails habilitados')

    def __str__(self):
        return self.email


class UsersEvolutionReport(models.Model):
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    present = models.BooleanField(default=False)
    file = models.FileField(upload_to='reports', null=True)

class UsersEvolutionPerCourseReport(models.Model):
    started = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True)
    present = models.BooleanField(default=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports', null=True)