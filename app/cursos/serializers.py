from django.db import transaction
from django.db.models import Q, F, Max
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django import forms
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import SegmentTracking, Course, Category, Segment, SegmentSection, DownloadableDocument, Question, Option, Slide
from users.serializers import UserSerializer
from foros.models import Forum
from tareas.models import Tarea
from streaming.models import Broadcast
from common.serializers import DateTimeListField


# http://blog.qax.io/write-once-fields-with-django-rest-framework/
class WriteOnceMixin:
    """Adds support for write once fields to serializers.

    To use it, specify a list of fields as `write_once_fields` on the
    serializer's Meta:
    ```
    class Meta:
        model = SomeModel
        fields = '__all__'
        write_once_fields = ('collection', )
    ```

    Now the fields in `write_once_fields` can be set during POST (create),
    but cannot be changed afterwards via PUT or PATCH (update).
    Inspired by http://stackoverflow.com/a/37487134/627411.
    """

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()

        # We're only interested in PATCH/PUT.
        if 'update' in getattr(self.context.get('view'), 'action', ''):
            return self._set_write_once_fields(extra_kwargs)

        return extra_kwargs

    def _set_write_once_fields(self, extra_kwargs):
        """Set all fields in `Meta.write_once_fields` to read_only."""
        write_once_fields = getattr(self.Meta, 'write_once_fields', None)
        if not write_once_fields:
            return extra_kwargs

        if not isinstance(write_once_fields, (list, tuple)):
            raise TypeError(
                'The `write_once_fields` option must be a list or tuple. '
                'Got {}.'.format(type(write_once_fields).__name__)
            )

        for field_name in write_once_fields:
            kwargs = extra_kwargs.get(field_name, {})
            kwargs['read_only'] = True
            extra_kwargs[field_name] = kwargs

        return extra_kwargs


class SegmentTrackingSerializer(serializers.ModelSerializer):
    parts_watched = serializers.ListField(
        child=serializers.IntegerField()
    )

    class Meta:
        model = SegmentTracking
        fields = ['id', 'video', 'parts_watched', 'watched_full', 'continue_from', 'last_part_watched']
        read_only_fields = ['continue_from']
        write_only_fields = ['last_part_watched']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = []


class DownloadableDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadableDocument
        fields = [
            'id',
            'video',
            'name',
            'document',
            'is_mandatory',
        ]


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = [
            'id',
            'question',
            'text',
            'is_correct'
        ]


class QuestionSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id',
            'section',
            'text',
            'image',
            'image_url',
            'has_only_one_correct_answer',
            'show_correct_options',
            'show_incorrect_options',
            'text_after_correct_answer',
            'text_after_incorrect_answer'
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None


class SegmentSectionSerializer(serializers.ModelSerializer):
    question_set = QuestionSerializer(many=True, required=False)
    order = serializers.IntegerField(min_value=1)

    class Meta:
        model = SegmentSection
        fields = ['id', 'order', 'segment', 'questions_to_ask', 'question_set']
        validators = []

    def create(self, validated_data):
        ss = SegmentSection()
        self.set_values(ss, validated_data)
        return ss

    def update(self, instance, validated_data):
        if 'segment' in validated_data:
            if instance.segment != validated_data['segment']:
                raise ValidationError(_('No se puede modificar el segmento al que pertenece una sección.'))
        self.set_values(instance, validated_data)
        return instance

    @transaction.atomic()
    def set_values(self, ss, validated_data):
        ss.questions_to_ask = validated_data['questions_to_ask']
        if 'segment' in validated_data:
            ss.segment = validated_data['segment']

        new_order = validated_data['order']
        count = SegmentSection.objects.filter(segment=ss.segment).count()
        if ss.id:
            # es un update
            move_into_gap = ss
        else:
            count += 1
            move_into_gap = None
        if new_order > count:
            new_order = count
        SegmentSection.objects.rearrange_orders(parent=ss.segment, parent_attr='segment',
                                                leave_gap=new_order, move_into_gap=move_into_gap)
        ss.order = new_order
        ss.save()
        return ss


class SlideSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slide
        fields = ['id', 'image', 'segment']

    def create(self, validated_data):
        slide = Slide()
        slide.image = validated_data['image']
        slide.save()
        segment = validated_data['segment']
        if not segment.first_slide is None:
            has_next_slide = True
            if not segment.first_slide.next_slide is None:
                next_slide = segment.first_slide.next_slide
            else:
                next_slide = segment.first_slide
                has_next_slide = False
            while has_next_slide:
                if next_slide.next_slide is None:
                    has_next_slide = False
                else:
                    next_slide = next_slide.next_slide
            next_slide.next_slide = slide
            next_slide.save()
        else:
            segment.first_slide = slide
            segment.save()
        return super().create(validated_data)

class DateSerializer(serializers.Serializer):
    date = serializers.DateTimeField()

class FixedDatesBroadcastSerializer(serializers.Serializer):
    dates = DateSerializer(many=True)

class OpenBroadcastSerializer(serializers.Serializer):
    open_broadcast_date = serializers.DateTimeField()

class SegmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='title', read_only=True)
    order = serializers.IntegerField(min_value=1)
    is_broadcasting_now = serializers.BooleanField(read_only=True)
    thumbnail_manual_url = serializers.SerializerMethodField()
    fixed_dates_broadcast = FixedDatesBroadcastSerializer(required=False)
    open_broadcast = OpenBroadcastSerializer(required=False)

    class Meta:
        model = Segment
        fields = [
            'id',
            'order',
            'title',
            'type_of_segment',
            'vimeo_id',
            'genially_id',
            'course',
            'max_retries',
            'min_correct_questions',
            'thumbnail_url',
            'enabled_since',
            'thumbnail',
            'thumbnail_manual_url',
            'name',
            'rtmp_url',
            'stream_key',
            'announcement_type',
            'fixed_dates_broadcast',
            'open_broadcast',
            'is_broadcasting_now',
            'requires_full_watch',
            'embed_code'
        ]
        validators = []

        # TODO: agregar mixin WriteOnceMixin
        # write_once_fields = ('course', )

    def get_thumbnail_manual_url(self, instance):
        if instance.thumbnail:
            return instance.thumbnail.url
        return None

    def after_save(self, instance):
        instance.clean()
        instance.save()

    def validate(self, attrs):
        type_of_segment = attrs.get('type_of_segment') or self.context.get('type_of_segment')
        if type_of_segment == Segment.LIVE_STREAM:
            announcement_type = attrs.get('announcement_type')
            if announcement_type == Segment.FIXED_DATE_ANNOUNCEMENT_TYPE and (attrs.get('open_broadcast')
                or not attrs.get('fixed_dates_broadcast')):
                raise forms.ValidationError(
                    _('Datos no correspondientes a la modalidad de transmisión en fechas específicas')
                )
            if announcement_type == Segment.OPEN_ANNOUNCEMENT_TYPE and (attrs.get('fixed_dates_broadcast')
                or not attrs.get('open_broadcast')):
                raise forms.ValidationError(
                    _('Datos no correspondientes a la modalidad de transmisión abierta')
                )
        if type_of_segment == Segment.GENIALLY:
            genially_id = attrs.get('genially_id', None)
            if not genially_id:
                raise forms.ValidationError(
                    _('El ID del Genially es requerido')
                )
        if type_of_segment == Segment.GENERIC:
            embed_code = attrs.get('embed_code', None)
            if not embed_code:
                raise forms.ValidationError(
                    _('El código HTML para embeber es requerido')
                )
        return attrs

    @transaction.atomic()
    def create(self, validated_data):
        segment = Segment()
        self.set_values(segment, validated_data)
        self.after_save(segment)
        return segment

    @transaction.atomic()
    def update(self, instance, validated_data):
        if 'course' in validated_data:
            raise ValidationError(_('No se puede modificar el curso al que pertenece un segmento.'))
        self.set_values(instance, validated_data)
        self.after_save(instance)
        return instance

    def set_values(self, seg, validated_data):
        # en caso de ser un segmento LIVE_STREAM se indica en el context desde el ViewSet
        # en lugar de enviarlo desde el frontend
        type_of_segment = validated_data.get('type_of_segment') or self.context.get('type_of_segment')

        seg.title = validated_data['title']
        seg.requires_full_watch = validated_data['requires_full_watch']
        seg.type_of_segment = type_of_segment
        seg.max_retries = validated_data.get('max_retries', seg.max_retries)
        seg.min_correct_questions = validated_data.get('min_correct_questions', seg.min_correct_questions)
        if validated_data.get('enabled_since'):
            seg.enabled_since = validated_data['enabled_since']
        else:
            seg.enabled_since = None
        if 'course' in validated_data:
            seg.course = validated_data['course']
        if 'vimeo_id' in validated_data:
            seg.set_as_vimeo(validated_data['vimeo_id'])
        if 'genially_id' in validated_data:
            seg.set_as_genially(validated_data['genially_id'])
        if 'embed_code' in validated_data:
            seg.set_as_generic(validated_data['embed_code'])
        if 'thumbnail' in validated_data:
            seg.thumbnail = validated_data['thumbnail']

        if type_of_segment == Segment.LIVE_STREAM:
            seg.set_as_live_stream(
                validated_data.get('rtmp_url'),
                validated_data.get('stream_key'),
                validated_data.get('announcement_type')
            )

        new_order = validated_data['order']
        count = Segment.objects.filter(course=seg.course).count()
        if seg.id:
            move_into_gap = seg
        else:
            count += 1
            move_into_gap = None
        if new_order > count:
            new_order = count
        Segment.objects.rearrange_orders(
            parent=seg.course,
            parent_attr='course',
            leave_gap=new_order,
            move_into_gap=move_into_gap,
            subset_filter=Q(is_live_stream=seg.is_live_stream)
        )
        seg.order = new_order
        seg.save()
        self._update_broadcasts(seg, validated_data)
        return seg

    def _update_broadcasts(self, seg, validated_data):
        if seg.type_of_segment == Segment.LIVE_STREAM:
            now = timezone.localtime()

            if seg.announcement_type == Segment.FIXED_DATE_ANNOUNCEMENT_TYPE:
                # primero se eliminan todos los broadcasts con fecha futura del segmento
                seg.broadcasts.not_live().after(now).delete()
                dates = validated_data.get('fixed_dates_broadcast', {}).get('dates', [])
                dates = [d.get('date') for d in dates]
                future_dates = filter(lambda d: d > now, dates)
                for date in future_dates:
                    seg.create_broadcast(date=date)
            elif seg.announcement_type == Segment.OPEN_ANNOUNCEMENT_TYPE:
                following_date = validated_data.get('open_broadcast', {}).get('open_broadcast_date')
                if following_date:
                    # si existe un broadcast futuro (no puede haber más de uno), se modificará en lugar de crear uno nuevo
                    future_broadcast, _ = seg.broadcasts.not_live().after(now).update_or_create(
                        segment=seg, defaults={'date': following_date}
                    )
                    seg.update_broadcast(future_broadcast)
                else:
                    # si no se indicó una fecha futura, se elimina en caso de existir
                    seg.broadcasts.not_live().after(now).delete()


class CourseSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    tutor = UserSerializer()
    segments = SegmentSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'slug',
            'start_date',
            'categories',
            'tutor',
            'segments',
            'price',
            'price_currency'
        ]


# Estos serializers son para representar los segmentos de un curso en un árbol usando angular2-tree

class OptionTreeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='text')
    hasChildren = serializers.ReadOnlyField(default=False)
    type = serializers.ReadOnlyField(default='Option')

    class Meta:
        model = Option
        fields = ['id', 'name', 'type', 'is_correct', 'hasChildren']


class QuestionTreeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='text')
    type = serializers.ReadOnlyField(default='Question')
    children = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'name', 'type', 'children']

    @staticmethod
    def get_children(obj):
        options = {
            'name': 'Opciones',
            'type': 'OptionsTitle',
        }
        if obj.option_set.all():
            options['children'] = OptionTreeSerializer(obj.option_set.all(), many=True).data
        return [options]


class SegmentSectionTreeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    type = serializers.ReadOnlyField(default='SegmentSection')
    children = serializers.SerializerMethodField()

    class Meta:
        model = SegmentSection
        fields = ['id', 'name', 'type', 'children']

    @staticmethod
    def get_name(obj):
        return f'Cuestionario {obj.order}'

    @staticmethod
    def get_children(obj):
        questions = {
            'name': 'Preguntas',
            'type': 'QuestionsTitle',
        }
        if obj.question_set.all():
            questions['children'] = QuestionTreeSerializer(obj.question_set.all(), many=True).data
        return [questions]


class DownloadableDocumentTreeSerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(default='DownloadableDocument')
    hasChildren = serializers.ReadOnlyField(default=False)

    class Meta:
        model = DownloadableDocument
        fields = ['id', 'name', 'hasChildren', 'type']

class SlideTreeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='image.url')
    type = serializers.ReadOnlyField(default="Slide")
    thumbnail = serializers.ReadOnlyField(source='image.url')

    class Meta:
        model = Slide
        fields = ['id', 'image', 'name', 'type', 'thumbnail']

class SegmentTreeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    type = serializers.ReadOnlyField(default='Segment')
    thumbnail = serializers.ReadOnlyField(source='thumbnail_url')
    children = serializers.SerializerMethodField()

    class Meta:
        model = Segment
        fields = ['id', 'name', 'type', 'children', 'thumbnail']

    @staticmethod
    def get_name(obj):
        return f'{obj.order} - {obj.title}'

    def get_sections(self, obj):
        sections = {
            'name': 'Cuestionarios',
            'type': 'QuestionnairesTitle',
        }
        if obj.sections.all():
            sections['children'] = SegmentSectionTreeSerializer(obj.sections.all(), many=True).data
        return sections

    def get_documents(self, obj):
        documents = {
            'name': 'Documentos',
            'type': 'DocumentsTitle',
        }
        if obj.downloadabledocument_set.all():
            documents['children'] = DownloadableDocumentTreeSerializer(obj.downloadabledocument_set.all(),
                                                                       many=True).data
        return documents

    def get_tareas(self, obj):
        tareas = {
            'name': 'Tareas',
            'type': 'TasksTitle',
        }
        if obj.tarea_set.all():
            tareas['children'] = TareaTreeSerializer(obj.tarea_set.all(), many=True).data
        return tareas

    def get_children(self, obj):
        sections = self.get_sections(obj)

        documents = self.get_documents(obj)

        tareas = self.get_tareas(obj)

        forums = self.get_forums(obj)

        if obj.type_of_segment == Segment.SLIDES:
            slides = self.get_slides(obj)
            return [slides, sections, documents, forums, tareas]

        return [sections, documents, forums, tareas]

    def get_forums(self, obj):
        forums = {
            'name': 'Foros',
            'type': 'ForumsTitle',
        }
        if obj.forum_set.all():
            forums['children'] = ForumTreeSerializer(obj.forum_set.all(), many=True).data
        return forums

    def get_slides(self, obj):
        slides = {
            'name': 'Diapositivas',
            'type': 'SlidesTitle',
        }
        if obj.slides:
            slides['children'] = SlideTreeSerializer(obj.slides, many=True).data
        return slides


class LiveStreamSegmentTreeSerializer(SegmentTreeSerializer):
    type = serializers.ReadOnlyField(default='LiveStream')

    def get_children(self, obj):
        documents = self.get_documents(obj)

        tareas = self.get_tareas(obj)

        forums = self.get_forums(obj)

        return [documents, forums, tareas]


class CourseSegmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['children']

    @staticmethod
    def get_children(obj):
        segments = {
            'id': obj.id,
            'name': 'Segmentos',
            'type': 'SegmentsTitle',
            'children': SegmentTreeSerializer(obj.non_live_segments.order_by('order'), many=True).data
        }

        live_streams = {
            'id': obj.id,
            'name': 'Transmisiones en vivo',
            'type': 'LiveStreamsTitle',
            'children': LiveStreamSegmentTreeSerializer(obj.live_segments.order_by('order'), many=True).data
        }
        return [segments, live_streams]

class ForumTreeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    type = serializers.ReadOnlyField(default='Forum')
    hasChildren = serializers.ReadOnlyField(default=False)

    class Meta:
        model = Forum
        fields = ['id', 'name', 'type', 'hasChildren']

    @staticmethod
    def get_name(obj):
        return obj.title


class TareaTreeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    type = serializers.ReadOnlyField(default='Tarea')
    hasChildren = serializers.ReadOnlyField(default=False)

    class Meta:
        model = Tarea
        fields = ['id', 'name', 'titulo', 'hasChildren', 'type']

    @staticmethod
    def get_name(obj):
        return obj.titulo
