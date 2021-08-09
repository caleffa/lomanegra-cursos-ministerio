# -*- coding: UTF-8 -*-
from django.shortcuts import get_object_or_404, render, redirect, resolve_url
from django.http import Http404, HttpResponseForbidden, FileResponse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.urls import resolve
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormMixin, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, authentication, permissions, response, status
from rest_framework.decorators import action
from sendfile import sendfile

from allauth.account import views as allauth_views
from allauth.account import app_settings as allauth_app_settings
from .helpers import reset_user_tracking_for_course, reset_course_tracking

from .serializers import SegmentTrackingSerializer
from .forms import EveryComplianceSignupForm
from .models import Course, Segment, SegmentTracking, Questionnaire, QuestionnaireQuestion, \
    QuestionnaireOption, CourseEnrollment, SiteSettings, Question, \
    DownloadableDocument, DownloadableDocumentTracking, Slide, UsersEvolutionReport, UsersEvolutionPerCourseReport, \
    Category, CareerTrack
from users.models import User
from encuestas.models import Encuesta
from encuestas.views import redirect_to_encuesta

import os
import unicodedata
from operator import itemgetter
from wsgiref.util import FileWrapper
import reports
from collections import OrderedDict
import django_excel as excel
import io
import xlsxwriter
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import logging
logger = logging.getLogger()


class MultipleSessionsView(TemplateView):
    template_name = 'account/multiple_sessions.html'


class LandingView(TemplateView):
    template_name = 'account/landing.html'


class EveryComplianceEmailVerificationSentView(allauth_views.EmailVerificationSentView):
    def get_context_data(self, **kwargs):
        context = super(EveryComplianceEmailVerificationSentView, self).get_context_data(**kwargs)

        context['support_email'] = getattr(settings, 'SUPPORT_EMAIL', None)

        return context


# Override email verification sent
allauth_views.email_verification_sent = EveryComplianceEmailVerificationSentView.as_view()


class EveryComplianceSignupView(allauth_views.SignupView):
    form_class = EveryComplianceSignupForm

    def get_form(self, form_class=None):
        form = super(EveryComplianceSignupView, self).get_form(form_class=form_class)
        form.fields['password1'].help_text = _(f'''La contraseña debe contener al menos 8 caracteres. 
        No puede estar formada exclusivamente por números. 
        Tampoco debe ser un valor común como \'12345678\' ni coincidir con el nombre o email del usuario.''')

        return form


allauth_views.signup = EveryComplianceSignupView.as_view()


class SegmentTrackingViewset(viewsets.ModelViewSet):
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = SegmentTrackingSerializer
    # No permito POST, los voy a crear cuando el pibe entra al curso
    # No permito DELETE
    http_method_names = ['get', 'patch', 'options']
    queryset = SegmentTracking.objects.all()

    def get_queryset(self):
        user = self.request.user
        return SegmentTracking.objects.filter(user=user)

    @action(methods=['get'], detail=False, url_path='video/(?P<video_id>\d+)')
    def video(self, request, video_id = None):
        vt = self.get_queryset().filter(video_id=video_id).first()

        if vt is None:
            raise Http404

        serializer = SegmentTrackingSerializer(many=False, instance=vt)
        return response.Response(data=serializer.data, status=status.HTTP_200_OK)


class HomeView(ListView):
    model = Course
    template_name = "pages/home.html"
    ordering = ['order']

    def get(self, *args, **kwargs):
        usr = self.request.user
        if usr.is_stakeholder and not usr.is_staff and not usr.is_tutor:
            return redirect('dashboard')
        else:
            return redirect('categories')
        return super(HomeView, self).get(*args, **kwargs)

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset()
        return qs.filter(enrollments__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        enrolled_courses = OrderedDict()
        current_live_segments = []
        following_live_segments = []
        if user.is_authenticated:
            current_live_segments = Segment.objects.for_user(user).with_current_live_broadcast()
            following_live_segments = Segment.objects.for_user(user).with_following_broadcast()
            enrolled_courses_queryset = CourseEnrollment.objects.filter(user=user)
            for course in Course.objects.filter(enrollments__in=enrolled_courses_queryset):
                try:
                    ce = CourseEnrollment.objects.get(course=course, user=user)
                    enrolled_courses[course] = ce
                except ObjectDoesNotExist:
                    enrolled_courses[course] = None

            # Busco adonde mandar al usuario para "continuar viendo", issue 53
            unfinished_course_enrollments = enrolled_courses_queryset.filter(is_complete=False)
            user_segment_trackings = SegmentTracking.objects.filter(user=user)
            try:
                last_track = user_segment_trackings.latest('last_watch')
                enrollment = unfinished_course_enrollments.get(course=last_track.video.course)
                context['continue_url'] = enrollment.next_url()
                context['next_segment'] = enrollment.next_segment
                context['next_segment_is_enabled'] = enrollment.next_segment_is_enabled
            except ObjectDoesNotExist:
                # el track mas reciente es de un curso ya terminado. pruebo con todos los cursos 
                for course, enrollment in enrolled_courses.items():
                    if enrollment and not enrollment.is_complete:
                        context['continue_url'] = enrollment.next_url()
                        context['next_segment'] = enrollment.next_segment
                        context['next_segment_is_enabled'] = enrollment.next_segment_is_enabled
                        break

            if 'continue_url' not in context:
                for course, enrollment in enrolled_courses.items():
                    if not enrollment:
                        context['has_not_started_yet'] = True
                        try:
                            first_segment = course.first_segment
                            context['next_segment'] = first_segment
                            context['next_segment_is_enabled'] = first_segment.is_enabled
                            context['continue_url'] = first_segment.get_object_url()
                            break
                        except ObjectDoesNotExist:
                            pass
            if 'continue_url' not in context:
                # terminó todos los cursos
                context['all_courses_finished'] = True
                for course, enrollment in enrolled_courses.items():
                    try:
                        first_segment = course.first_segment
                        context['next_segment'] = first_segment
                        context['next_segment_is_enabled'] = first_segment.is_enabled
                        context['continue_url'] = first_segment.get_object_url()
                        break
                    except ObjectDoesNotExist:
                        pass

        context['enrolled_courses'] = enrolled_courses
        context['current_live_segments'] = current_live_segments
        context['following_live_segments'] = following_live_segments

        context['sitesettings'] = SiteSettings.get_solo()

        context['current_time'] = timezone.now()

        return context


def authenticate_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('public'))

    user = authenticate(request)
    if user is None:
        return HttpResponseForbidden()
    else:
        login(request, user)
        return redirect(reverse('public'))


class CareerTrackListView(ListView):
    model = CareerTrack
    context_object_name = 'career_tracks_list'
    template_name = 'cursos/career_tracks_list.html'
    ordering = ('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb'] = { 'first': {'title': _('Cursos')} }
        return context

    def get_queryset(self, **kwargs):
        return CareerTrack.objects.with_courses(self.request.user)


class PublicCareerTrackListView(CareerTrackListView):
    template_name = 'cursos/public_career_tracks_list.html'

    def get_queryset(self, **kwargs):
        return CareerTrack.objects.order_by('order').all()


class CareerTrackCategoriesListView(ListView):
    model = Category
    template_name = 'cursos/career_track_categories_list.html'

    def get_queryset(self):
        ct_id = self.kwargs.get('category', None)
        qs = Category.objects.with_courses(self.request.user).filter(career_tracks__id__in=[ct_id])
        return qs

    def get_enrollment(self, cour):
        return CourseEnrollment.objects.filter(course=cour, user=self.request.user).first()

    def get_courses(self, cat):
        return cat.courses.started_with_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ct_id = self.kwargs.get('category', None)
        context['career_track'] = CareerTrack.objects.get(pk=int(ct_id))

        categories_list = []
        # enrollments = CourseEnrollment.objects.filter(user=self.request.user)
        for cat in self.object_list.order_by('order'):
            category = cat.__dict__
            category['courses'] = []
            category['has_courses'] = False
            for cour in self.get_courses(cat):
                category['has_courses'] = True
                enrollment = self.get_enrollment(cour)
                course = cour.__dict__
                course['enrollment'] = enrollment
                course['next_segment_enabled'] = False
                course['next_url'] = ''
                course['next_segment'] = Segment.objects.first()
                if enrollment and enrollment.next_segment:
                    course['next_segment_enabled'] = enrollment.next_segment.is_enabled
                    course['next_url'] = enrollment.next_url
                    course['next_segment_title'] = enrollment.next_segment.title
                    course['next_segment_date'] = enrollment.next_segment.enabled_since
                category['courses'].append(course)
            categories_list.append(category)
        context['categories_list'] = categories_list
        return context


class PublicCareerTrackCategoriesListView(CareerTrackCategoriesListView):
    template_name = 'cursos/public_career_track_categories_list.html'

    def get_enrollment(self, cour):
        return None

    def get_courses(self, cat):
        return cat.courses.filter(start_date__lte=timezone.now())

    def get_queryset(self):
        ct_id = self.kwargs.get('category', None)
        qs = Category.objects.filter(career_tracks__id__in=[ct_id])
        return qs

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('category_courses', **kwargs)
        return super().get(*args, **kwargs)


class CoursesListView(ListView):
    model = Course
    template_name = 'cursos/courses_list.html'

    def get_queryset(self):
        qs = Course.objects.allows_user(self.request.user)
        url_name = self.request.resolver_match.url_name
        if url_name == 'enrolled_courses':
            qs = qs.filter(enrollments__user=self.request.user)
        elif url_name == 'not_started_courses':
            qs = qs.filter(start_date__gt=timezone.now())

        search_term = self.request.GET.get('t', None)
        if search_term:
            qs = qs.filter(
                Q(title__unaccent__icontains=search_term) | Q(description__unaccent__icontains=search_term) |
                Q(categories__title__unaccent__icontains=search_term)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = OrderedDict()
        enrollments = CourseEnrollment.objects.filter(user=self.request.user)
        for course in self.object_list.order_by('order'):
            courses[course] = {
                'enrollment': enrollments.filter(course=course).first()
            }

        breadcrumb = None
        url_name = self.request.resolver_match.url_name
        if url_name == 'enrolled_courses':
            breadcrumb = {
                'first': { 'title': _('Mis cursos') }
            }
        elif url_name == 'not_started_courses':
            breadcrumb = {
                'first': { 'title': _('Próximos cursos') }
            }
        else:
            category = Category.objects.all().filter(id=self.kwargs.get('category', None)).first()
            if category:
                breadcrumb = {
                    'first': { 'title': _('Cursos'), 'url': reverse('categories') },
                    'second': { 'title': category.title }
                }
            else:
                breadcrumb = {
                    'first': { 'title': _('Cursos') }
                }

        context['courses'] = courses
        context['breadcrumb'] = breadcrumb
        context['current_time'] = timezone.now()
        context['settings'] = settings
        return context


class CourseEnrollmentCreateView(CreateView):
    model = CourseEnrollment
    fields = []
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        self.object = None
        course = get_object_or_404(Course, pk=self.kwargs['course'])
        user = request.user

        if not course.user_allowed_to_enroll(user):
            return HttpResponseForbidden()

        if course.es_pago:
            if not course.usuario_ya_pago(user):
                self.request.session['return_page'] = reverse('course', kwargs={'course': course.slug})
                return redirect(reverse("pagar-curso", kwargs={'pk': course.id}))

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, course)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, course):
        form.instance.user = self.request.user
        form.instance.course = course
        form.save()
        next_page = reverse('course', kwargs={'course': course.slug})
        return redirect(next_page)
        

class CourseUnenrollDeleteView(DeleteView):
    model = CourseEnrollment
    template_name = 'cursos/course_unenroll.html'

    def get_object(self, queryset=None):
        enrollment = get_object_or_404(CourseEnrollment, course_id=self.kwargs['course'], user=self.request.user)
        return enrollment
    
    def post(self, request, *args, **kwargs):
        enrollment = self.get_object()
        reset_user_tracking_for_course(self.request.user.email, enrollment.course)
        next_page = request.POST.get('next')
        if request.POST.get('search'):
            next_page += '?t=' + request.POST.get('search')
        return redirect(next_page)

class CourseListView(ListView):
    model = Course

    def get_queryset(self):
        qs = super(CourseListView, self).get_queryset()
        return qs.allows_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        courses = OrderedDict()
        enrolled_courses_queryset = CourseEnrollment.objects.filter(user=self.request.user)
        video_trackings_queryset = SegmentTracking.objects.filter(user=self.request.user)
        for course in self.object_list.order_by('order'):
            try:
                course_enrollment = enrolled_courses_queryset.get(course=course)
            except ObjectDoesNotExist:
                course_enrollment = None
            videos = OrderedDict()
            for video in course.non_live_segments.order_by('order'):
                try:
                    video_tracking = video_trackings_queryset.get(video=video)
                except ObjectDoesNotExist:
                    video_tracking = None
                videos[video] = video_tracking
            
            courses[course] = {
                'enrollment': course_enrollment,
                'videos': videos,
                'next_segment': course_enrollment.next_segment if course_enrollment else course.first_segment,
                'next_url': course_enrollment.next_url if course_enrollment else course.first_segment_url
            }

        context['courses'] = courses

        return context


class CourseFinishedView(DetailView):
    model = CourseEnrollment
    context_object_name = 'course_enrollment'
    template_name = 'cursos/course_finished.html'

    def get_object(self, queryset=None):
        user = self.request.user

        course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
        course_enrollment = get_object_or_404(CourseEnrollment, user=user, is_complete=True, course=course)

        return course_enrollment

    #def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #    course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
    #    category = course.categories.last()
    #    if category.user_finished(self.request.user):
    #        context['category_id'] = category.id
    #    return context

class CourseDetailView(DetailView):
    model = Course
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        course = self.get_object(**kwargs)
        if course.start_date <= timezone.now():
            # Si hay alguna encuesta de inicio de este curso que el usuario nunca respondió, llevarlo a ella
            encuestas_curso = Encuesta.objects.open_now().on_course_start(course).not_snoozed(request.user)
            if encuestas_curso:
                return redirect_to_encuesta(request.get_full_path(), encuesta=encuestas_curso.first())
            return super().get(request, *args, **kwargs)
        else: 
            return redirect(reverse('enrolled_courses'))

    def get_queryset(self):
        qs = super(CourseDetailView, self).get_queryset()
        return qs.allows_user(self.request.user)

    def get_object(self, **kwargs):
        course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
        return course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        course_data = {}
        if self.request.user.is_authenticated:
            course_enrollment = CourseEnrollment.objects.filter(user=self.request.user, course=course).first()
            context['enrollment'] = course_enrollment
            context['next_segment'] = course_enrollment.next_segment if course_enrollment else course.first_segment
            context['segments'] = course.segments.all()
        return context


class RedirectToVideoView(Exception):
    pass


class RedirectToGenericView(Exception):
    pass


class RedirectToSlideView(Exception):
    pass


class RedirectToGenially(Exception):
    pass


class RedirectToEncuestaView(Exception):
    def __init__(self, encuesta_a_redirigir):
        self.redirect_to = encuesta_a_redirigir


class SegmentView(SingleObjectMixin, View):
    model = SegmentTracking
    context_object_name = 'tracking'

    def get(self, request, *args, **kwargs):
        '''
        Ni SingleObjectMixin ni View tienen método get, pero esta View no la usamos directamente, sino que es una vista
        genérica de la cual heredan VideoDetailView y SlideDetailView. Esas dos heredan también de DetailView, entonces
        este get hace override del get de DetailView.
        '''
        try:
            # este super termina llamando al get de DetailView
            return super().get(request, *args, **kwargs)
        except RedirectToVideoView:
            return redirect('video', **kwargs) # TODO: mmmm, esto de pasar los kwargs no me gusta
        except RedirectToSlideView:
            return redirect('slide', **kwargs)
        except RedirectToGenially:
            return redirect('genially', **kwargs)
        except RedirectToGenericView:
            return redirect('generic', **kwargs)
        except RedirectToEncuestaView as e:
            return redirect_to_encuesta(self.request.get_full_path(), encuesta=e)

    def get_segment(self, course, order):
        return get_object_or_404(Segment, course=course, order=order, is_live_stream=False)

    def get_tracking(self, order, course_enrollment, video):
        if order > 1:
            if course_enrollment.next_allowed_video and course_enrollment.next_allowed_video.order >= video.order:
                tracking, _ = video.get_or_create_tracking(self.request.user)
                return tracking
            else:
                logger.error('Trying to access locked segment', exc_info=True, extra={'request': self.request})
                raise PermissionDenied
        else:
            tracking, _ = video.get_or_create_tracking(self.request.user)
            return tracking

    def get_object(self, **kwargs):
        course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
        course_enrollment = get_object_or_404(CourseEnrollment, course=course, user=self.request.user)
        # if created:
        #     first_segment = course.first_segment
        #     course_enrollment.next_allowed_video = first_segment
        #     course_enrollment.save()

        # Si hay alguna encuesta de inicio de este curso que el usuario nunca respondió, llevarlo a ella
        encuestas_curso = Encuesta.objects.open_now().on_course_start(course).not_snoozed(self.request.user)
        if encuestas_curso:
            raise RedirectToEncuestaView(encuestas_curso.first())

        order = self.kwargs['order']
        video = self.get_segment(course, order)
        if not video.is_enabled:
            raise PermissionDenied
        tracking = self.get_tracking(order, course_enrollment, video)
        return tracking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['video'] = self.object.video
        context['host'] = os.environ.get('VIRTUAL_HOST', None)
        context['questions'] = Question.objects.filter(section__segment=self.object.video)
        course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
        context['course_enrollment'] = CourseEnrollment.objects.get(course=course, user=self.request.user)
        context['pending_downloads'] = self.object.get_pending_downloads()
        context['user_has_pending_tareas'] = self.object.video.user_has_pending_tareas(self.request.user)
        return context


class LiveDetailView(SegmentView, DetailView):
    template_name = 'cursos/livetracking_detail.html'

    def get_segment(self, course, order):
        return get_object_or_404(Segment, course=course, order=order, is_live_stream=True)

    def get_tracking(self, order, course_enrollment, video):
        tracking, _ = video.get_or_create_tracking(self.request.user)
        return tracking

    def get(self, request, *args, **kwargs):
        tracking = self.get_object(**kwargs)
        if tracking.video.course.start_date <= timezone.now():  # TODO: este check no debería estar en get_object de SegmentView?
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()


class GeniallyDetailView(SegmentView, DetailView):
    template_name = 'cursos/genially_detail.html'

    def get_object(self, **kwargs):
        tracking = super().get_object(**kwargs)
        if tracking.video.type_of_segment == Segment.SLIDES:
            raise RedirectToSlideView
        if tracking.video.type_of_segment == Segment.VIDEO:
            raise RedirectToVideoView
        if tracking.video.type_of_segment == Segment.GENERIC:
            raise RedirectToGenericView
        return tracking


class VideoDetailView(SegmentView, DetailView):
    template_name = 'cursos/videotracking_detail.html'

    def get(self, request, *args, **kwargs):
        tracking = self.get_object(**kwargs)
        if tracking.video.course.start_date <= timezone.now():      # TODO: este check no debería estar en get_object de SegmentView?
            return super().get(request, *args, **kwargs)
        else: 
            return HttpResponseForbidden()

    def get_object(self, **kwargs):
        tracking = super().get_object(**kwargs)
        if tracking.video.type_of_segment == Segment.SLIDES:
            raise RedirectToSlideView
        if tracking.video.type_of_segment == Segment.GENIALLY:
            raise RedirectToGenially
        if tracking.video.type_of_segment == Segment.GENERIC:
            raise RedirectToGenericView
        return tracking


class GenericDetailView(SegmentView, DetailView):
    template_name = 'cursos/generic_detail.html'

    def get_object(self, **kwargs):
        tracking = super().get_object(**kwargs)
        if tracking.video.type_of_segment == Segment.VIDEO:
            raise RedirectToVideoView
        if tracking.video.type_of_segment == Segment.GENIALLY:
            raise RedirectToGenially
        if tracking.video.type_of_segment == Segment.SLIDES:
            raise SlideDetailView
        return tracking


class SlideDetailView(SegmentView, DetailView):
    # Si hacés GET sin pasar valor en el argumento slide, te muestra la slide apuntada por last_slide_shown en SegmentTracking
    # Si hacés un GET pasando un valor en el argumento slide, ese valor tiene que ser el ID de la slide que querés ver
    # pero tenemos que ver que sea una slide inmediatamente posterior a last_slide_shown, o bien una anterior.
    template_name = 'cursos/slidetracking_detail.html'

    def get_object(self, **kwargs):
        tracking = super().get_object(**kwargs)
        if tracking.video.type_of_segment == Segment.VIDEO:
            raise RedirectToVideoView
        if tracking.video.type_of_segment == Segment.GENIALLY:
            raise RedirectToGenially
        if tracking.video.type_of_segment == Segment.GENERIC:
            raise RedirectToGenericView
        if not tracking.last_slide_shown:
            tracking.last_slide_shown = tracking.video.first_slide
            tracking.save()
        return tracking

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'slide' in self.kwargs:
            slide_id = self.kwargs['slide']
            if self.object.last_slide_shown.next_slide and self.object.last_slide_shown.next_slide.id == slide_id:
                new_slide = Slide.objects.get(id=slide_id)
                self.object.last_slide_shown = new_slide
                self.object.save()
                context['slide'] = new_slide
            elif self.object.video.first_slide.id == slide_id:
                context['slide'] = self.object.video.first_slide
            elif slide_id in self.object.slides_seen:
                show_slide = Slide.objects.get(id=slide_id)
                context['slide'] = show_slide
            else:
                logger.error('Trying to access locked slide', exc_info=True, extra={'request': self.request})
                raise PermissionDenied
        else:
            context['slide'] = self.object.last_slide_shown

        context['is_first_slide'] = self.object.video.first_slide == context['slide']
        context['is_last_slide'] = False if context['slide'].next_slide else True

        # Vuelvo a buscar esto a la DB porque puede haber cambiado el next_allowed_video
        context['course_enrollment'] = CourseEnrollment.objects.get(course=self.object.video.course, user=self.request.user)
        
        return context


class MaxRetrialsExhaustedView(DetailView):
    model = Questionnaire
    template_name = 'cursos/max_retrials_exhausted.html'

    def get_object(self, **kwargs):
        course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
        video = get_object_or_404(Segment, course=course, order=self.kwargs['order'])
        tracking = get_object_or_404(SegmentTracking, video=video, user=self.request.user)
        if not tracking.can_answer_questionnaire():
            logger.error('Cannot answer questionnaire', exc_info=True, extra={'request': self.request})
            raise PermissionDenied
        all_questionnaires = Questionnaire.objects.filter(video=video, user=self.request.user)

        if all_questionnaires:
            last_questionnaire = all_questionnaires.latest('creation_timestamp')
        else:
            raise Http404

        return last_questionnaire


class MaxRetriesExhausted(Exception):
    pass


from django import forms
class QuestionnaireAnswerForm(forms.Form):
    option = forms.ModelChoiceField(queryset=QuestionnaireOption.objects.none(), widget=forms.RadioSelect)
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('options')
        super().__init__(*args, **kwargs)
        self.fields['option'].queryset = qs


class QuestionnaireView(FormMixin, DetailView):
    model = Questionnaire
    form_class = QuestionnaireAnswerForm

    def get_object(self, **kwargs):
        course = get_object_or_404(Course, slug__iexact=self.kwargs['course'])
        video = get_object_or_404(Segment, course=course, order=self.kwargs['order'])
        tracking = get_object_or_404(SegmentTracking, video=video, user=self.request.user)
        if not tracking.can_answer_questionnaire():
            logger.error('Cannot answer questionnaire', exc_info=True, extra={'request': self.request})
            raise PermissionDenied
        all_questionnaires = Questionnaire.objects.filter(video=video, user=self.request.user)
        if self.request.method == 'GET':
            if all_questionnaires:
                last_questionnaire = all_questionnaires.latest('creation_timestamp')
                if last_questionnaire.is_complete:
                    if video.max_retries == 0 or len(all_questionnaires) < video.max_retries:
                        # El usuario ya respondió el cuestionario de este video pero quiere responder de nuevo
                        return Questionnaire.objects.create_questionnaire(video, self.request.user)
                    else:
                        # No debería haber llegado acá
                        raise MaxRetriesExhausted
                else:
                    # No terminó de responder la última vez
                    return last_questionnaire
            else:
                # Nunca respondió
                return Questionnaire.objects.create_questionnaire(video, self.request.user)
        else:
            if all_questionnaires:
                last_questionnaire = all_questionnaires.latest('creation_timestamp')
                if not last_questionnaire.is_complete:
                    return last_questionnaire
                else:
                    logger.error('Last questionnaire is complete', exc_info=True, extra={'request': self.request})
                    raise PermissionDenied
            else:
                logger.error('There are no questionnaires', exc_info=True, extra={'request': self.request})
                raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.object.questionnairequestion_set.filter(answered=False).earliest('order')
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['options'] = self.object.questionnairequestion_set.filter(answered=False).earliest('order').questionnaireoption_set.all()
        return kwargs

    def get(self, request, *args, **kwargs):
        try:
            return super(QuestionnaireView, self).get(request, *args, **kwargs)
        except MaxRetriesExhausted:
            return redirect('failed', **kwargs) # TODO: mmmm, esto de pasar los kwargs no me gusta


    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        #print(form)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        selected_option = form.cleaned_data['option']
        questionnaire_question = selected_option.questionnaire_question
        selected_option.selected_by_user = True
        selected_option.save()
        QuestionnaireOption.objects.filter(questionnaire_question=questionnaire_question).exclude(id=selected_option.id).update(selected_by_user=False)

        questionnaire_question.answered = True
        # TODO corregir si hay mas de una opcion correcta
        if selected_option.option.is_correct:
            questionnaire_question.answered_correctly = True
        else:
            questionnaire_question.answered_correctly = False
        questionnaire_question.save()

        if self.object.questionnairequestion_set.filter(answered=False).count() == 0:
            context = {}
            # Termino de responder las preguntas de este video
            self.object.is_complete = True
            number_of_questions = self.object.questionnairequestion_set.all().count()
            correct_questions = self.object.questionnairequestion_set.filter(answered_correctly=True).count()
            self.object.score = int((correct_questions / number_of_questions) * 100)

            tracking = get_object_or_404(SegmentTracking, video=self.object.video, user=self.object.user)
            if correct_questions >= self.object.video.min_correct_questions:
                self.object.has_passed = True
                tracking.has_passed_questionnaire = True
                tracking.save()
            self.object.save()

            course_enrollment, finished_course, \
            must_complete_questionnaire, tareas_pendientes = tracking.update_course_enrollment_status()

            context['course_enrollment'] = course_enrollment
            context['finished_course'] = finished_course
            context['must_retake_questionnaire'] = must_complete_questionnaire
            context['last_question'] = questionnaire_question
            context['last_answer'] = selected_option
            context['questionnaire'] = self.object
            context['finished_questionnaire'] = True
            context['has_next_video'] = not self.object.video.is_last()
            context['has_pending_assignments'] = tareas_pendientes

        else:
            # Todavía faltan preguntas
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            context['last_question'] = questionnaire_question
            context['last_answer'] = selected_option

        return self.render_to_response(context)



        #return super().form_valid(form)


    def get_success_url(self):
        if not self.object.is_complete:
            return reverse('questionnaire', kwargs={'course': self.object.video.course.slug, 'order': self.object.video.order})
        else:
            # TODO redirigir a placa de fin
            return reverse('home')


class ViewDocumentView(DetailView):
    model = DownloadableDocument

    def get_object(self, queryset=None):
        document = super(ViewDocumentView, self).get_object(queryset=queryset)
        video = document.video
        tracking = get_object_or_404(SegmentTracking, video=video, user=self.request.user)
        # if tracking.watched_full:
        download_tracking, created = DownloadableDocumentTracking.objects.get_or_create(document=document,
                                                                                        user=self.request.user)
        if not created:
            download_tracking.times_downloaded += 1
            download_tracking.save()
        dowloaded_documents_tracking = DownloadableDocumentTracking.objects.select_related('document').filter(document__video=video,
                                                                                    user=self.request.user)
        mandatory_downloadable_documents = set(DownloadableDocument.objects.filter(video=video,is_mandatory=True))

        for d in dowloaded_documents_tracking:
            try:
                mandatory_downloadable_documents.remove(d.document)
            except KeyError:
                pass
        if len(mandatory_downloadable_documents) == 0:
            tracking.user_has_downloaded_all_documents = True
            tracking.save()

            if not video.has_questions():
                course_enrollment = CourseEnrollment.objects.get(course=video.course, user=self.request.user)

                if video.is_last():
                    course_enrollment.is_complete = True

                course_enrollment.update_next_allowed_video(video.next_segment())
                course_enrollment.save()

        return document

def download_document(request, documentpk):
    return redirect('view_document', **{'pk': documentpk})


class CertificateView(DetailView):
    model = CourseEnrollment
    template_name = 'cursos/ver_certificado.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Si hay alguna encuesta de fin de este curso que el usuario nunca respondió, llevarlo a ella
        encuestas_curso = Encuesta.objects.open_now().on_course_end(obj.course).not_snoozed(self.request.user)
        if encuestas_curso:
            raise RedirectToEncuestaView(encuestas_curso.first())
        return obj

    def get_context_data(self, **kwargs):
        context = super(CertificateView, self).get_context_data(**kwargs)
        context['document_url'] = resolve_url('diploma', **{'course_enrollment': self.object.pk})

        return context


class CourseCompletionCertificateView(View):
    def get(self, request, course_enrollment=None):
        course_enrollment = get_object_or_404(CourseEnrollment, id=course_enrollment)

        # Si hay alguna encuesta de fin de este curso que el usuario nunca respondió, llevarlo a ella
        encuestas_curso = Encuesta.objects.open_now().on_course_end(course_enrollment.course).not_snoozed(request.user)
        if encuestas_curso:
            raise RedirectToEncuestaView(encuestas_curso.first())

        # Si no completó el curso lo mando a la home
        # if not course_enrollment.is_complete:
        #     return reverse('home')

        def rep_func(stream):
            return reports.dummy_diploma(course_enrollment, stream)

        stream = reports.report_to_stream(rep_func)

        # content = None

        filename = _('constancia-') + course_enrollment.course.slug + '.pdf'
        response = HttpResponse(content=stream.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response['Content-Length'] = stream.getbuffer().nbytes
        response['Cache-Control'] = "no-cache, no-store, must-revalidate"

        # response = FileResponse(open('static/pdf/Certificado.pdf'), as_attachment=True, filename='finalizacion.pdf')

        return response


def xls_sheet_from_stats_data(stats_data, name=None):
    sheet_data = stats_data['table_data']
    sheet_data.insert(0, stats_data['table_header'])
    sheet = excel.pe.Sheet(sheet_data)
    if name:
        sheet.name = name

    return sheet


def xls_from_stats_data(stats_data, name=None):
    sheet = xls_sheet_from_stats_data(stats_data, name=name)
    return excel.make_response(sheet, "xlsx")

def in_memory_xls_from_stats_data(stats_data, name=None):
    data = []
    data.append(stats_data['table_header'])
    for row in stats_data['table_data']:
        data.append(row)
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    last_row = 0
    for row_num, columns in enumerate(data):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num, col_num, cell_data)
        last_row = row_num + 1
    worksheet.autofilter('A1:M'+str(last_row))
    workbook.close()
    output.seek(0)
    return output


def html_from_stats_data(request, stats_data):
    return render(request, 'stats_table.html', stats_data)

def stats_data_enrollments():
    # Indicador 1: Cantidad de Usuarios Alumnos Registrados. 
    header = [_("Nombre"), _("Apellido"), _("email"), _("Curso"), _("Fecha y hora de inicio del curso")]
    data = []
    for enrollment in CourseEnrollment.objects.all():
        data.append([enrollment.user.name, enrollment.user.last_name, enrollment.user.email, enrollment.course.title, enrollment.timestamp])
    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_potential_users(courseID):
    # Indicador 1: Cantidad de Usuarios Alumnos Registrados. 
    header = [_("Nombre"), _("Apellido"), _("email"), _("Curso")]
    course = Course.objects.get(pk=courseID)
    users = course.users_allowed_to_enroll.order_by('last_name', 'name', 'email').distinct()
    return {
        'table_header': header,
        'table_data': [
            [u.name, u.last_name, u.email, course.title] for u in users
        ]
    }

def stats_data_users_per_course(user):
    # Indicador 2: Cantidad de Usuarios que iniciaron cada curso.
    header = [_("Curso"), _("Cantidad de usuarios")]
    data = []

    for course in Course.objects.all().annotate(num_enrollments=Count('enrollments')):
        data.append([course.title, course.num_enrollments])

    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_potential_users_per_course(user):
    #Usuarios potenciales por curso
    header = [_("Curso"), _("Usuarios habilitados")]
    data = [
       [course.title, course.potential_users]
        for course in Course.objects.with_count_of_potential_users().order_by('id')
    ]
    return {
        'table_header': header,
        'table_data': data
    }


def stats_data_progress_summary_per_course(course):
    # Indicador 3: Para cada Curso, cantidad de Usuarios  que terminaron cada Segmento. ( ejemplo: 15 usuarios terminaron el segmento 1 de 4, 4 usuarios terminaron el segmento 2 de 4, 1 usuario termino el segmento 3 de 4, ningún usuario termino el segmento 4 de 4).
    header = [_("Tarea"), _("Segmento"), _("Cantidad de usuarios que lo completaron")]
    data = []

    watched_fully = Count('segmenttracking', filter=Q(segmenttracking__watched_full=True))
    document_downloaded = Count('segmenttracking', filter=Q(segmenttracking__watched_full=True, segmenttracking__user_has_downloaded_all_documents=True))
    questions_answered = Count('segmenttracking', filter=Q(segmenttracking__watched_full=True, segmenttracking__has_passed_questionnaire=True))

    for video in Segment.objects.prefetch_related('sections', 'downloadabledocument_set').filter(course=course).order_by('order').annotate(
            watched_fully=watched_fully, document_downloaded=document_downloaded, questions_answered=questions_answered):
        data.append([_("Segmento"), video.title, video.watched_fully])
        if video.has_documents():
            data.append([_("Descarga de documentos"), video.title, video.document_downloaded])
        if video.has_questions():
            data.append([_("Cuestionario"), video.title, video.questions_answered])
    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_progress_summary_per_course_treemap(course):
    # Repito el indicador 3 pero en un formato apto para un Treemap de Google Charts
    header = [_("Tarea"), _("Segmento"), _("Cantidad de usuarios que lo completaron")]
    data = []
    data.append([_("Curso completo"), '', 0])

    watched_fully = Count('segmenttracking', filter=Q(segmenttracking__watched_full=True))
    document_downloaded = Count('segmenttracking',
                                filter=Q(segmenttracking__watched_full=True, segmenttracking__user_has_downloaded_all_documents=True))
    questions_answered = Count('segmenttracking',
                               filter=Q(segmenttracking__watched_full=True, segmenttracking__has_passed_questionnaire=True))

    for video in Segment.objects.prefetch_related('sections', 'downloadabledocument_set').filter(course=course).order_by('order').annotate(
            watched_fully=watched_fully, document_downloaded=document_downloaded, questions_answered=questions_answered):
        data.append([video.title, "Curso completo", 0])
        if video.has_questions():
            data.append([_(f"Cuestionario {video.order}"), video.title, video.questions_answered])
        # TODO: esto presupone que es necesario descargar los documentos antes de contestar el cuestionario
        if video.has_documents():
            data.append([_(f"Descarga de documentos {video.order}"), video.title, video.document_downloaded])
        data.append([_(f"Segmento {video.order}"), video.title, video.watched_fully])
    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_dropout_ranking(course):
    # Indicador 4: Ranking de puntos de abandono de cada curso. O sea, en que instancia del curso la persona dejo de avanzar al siguiente elemento. Ejemplo: Puesto 1: 50 personas iniciaron y no completaron el segmento 3. Puesto 2: 20 personas iniciaron y no completaron el segmento 2.
    dropout_counters = {}
    for enrollment in CourseEnrollment.objects.select_related('next_allowed_video').filter(course=course, is_complete=False):
        if enrollment.next_allowed_video:
            try:
                if enrollment.next_allowed_video in dropout_counters:
                    dropout_counters[enrollment.next_allowed_video] += 1
                else:
                    dropout_counters[enrollment.next_allowed_video] = 1
            except ObjectDoesNotExist:
                pass
    data = []
    for video, dropouts in dropout_counters.items():
        data.append([video.title, dropouts])
    data = sorted(data, key=itemgetter(1), reverse=True)
    header = [_("Segmento"), _("Cantidad de usuarios que lo iniciaron pero no lo completaron")]
    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_failed_questions(course):
    # Indicador 5: Ranking de preguntas/cuestionarios que debieron ser reiterados para ser culminadas correctamente. Ejemplo: Puesto 1: Pregunta 1-Segmento 2 “Cual es la norma……. “ ; Puesto 2 Pregunta 3-Segmento 4 “Cual es la norma……. “.
    # Vamos a devolver cuántas veces respondieron mal cada pregunta
    questions_data = {}
    for wrong_answer in QuestionnaireQuestion.objects.select_related('question__section__segment__course').filter(question__section__segment__course=course, answered_correctly=False):
        if wrong_answer.question in questions_data:
            questions_data[wrong_answer.question] += 1
        else:
            questions_data[wrong_answer.question] = 1
    data = []
    for question, failed_attempts in questions_data.items():
        data.append([f"{question.text} (video {question.section.segment})", failed_attempts])
    data = sorted(data, key=itemgetter(1), reverse=True)
    header = [_("Pregunta"), _("Cantidad de respuestas incorrectas")]
    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_users_completed(user):
    # Indicador 6: Cantidad de Usuarios que culminaron cada curso.
    header = [_("Curso"), _("Cantidad de usuarios registrados en el curso"), _("Cantidad de usuarios que culminaron el curso")]
    data = []
    finished = Count('enrollments', filter=Q(enrollments__is_complete=True))
    enrolled = Count('enrollments')
    for course in Course.objects.annotate(finished=finished, enrolled=enrolled):
        data.append([course.title, course.enrolled, course.finished])
    return {
        'table_header': header,
        'table_data': data
    }

def stats_data_users_evolution(course=None):
    header = [
        _("Nombre"),
        _("Apellido"),
        _("Mail"),
        _("Curso"),
        _("Capitulo"),
        _("Estado"),

        _("Fecha de Estado Capitulo"),
        _("Incluye Evaluacion"),
        _("Estado"),
        _("Resultado"),

        _("Linea de Aprobacion"),
        _("Numero de Intentos requeridos"),
        _("Fecha de Estado Evaluacion")]
    data = []
    
    tracking_qs = SegmentTracking.objects
    if course:
        tracking_qs = tracking_qs.filter(video__course=course)

    segmen_trackings = tracking_qs.select_related(
        'user', 'video', 'video__course'
    ).order_by('user__email', 'video__course__order', 'video__order')

    for tracking in segmen_trackings:

        state = None
        date_state = None
        if tracking.watched_full_at:
            state = _('Finalizado')
            date_state = get_fromatted_date(tracking.watched_full_at)
        else:
            state = _('En curso')
            date_state = get_fromatted_date(tracking.started_timestamp)
        
        has_evaluation = None
        aproval_line = None
        result = None
        evaluation_state = None
        required_tries = None
        evaluation_date = None
        evaluation_date_formatted = None
        if tracking.video.has_questions():
            has_evaluation = 'SI'
            result = str(get_result(tracking)) + '%'
            aproval_line = str(get_aproval_line(tracking)) + '%'
            required_tries = tracking.total_tries
            evaluation_date_formatted = get_last_state_date(tracking)

            if Questionnaire.objects.filter(video=tracking.video, user=tracking.user).exists():
                # Si entró alguna vez al cuestionario entonces se considera que empezó a responderlo
                if tracking.has_answered_questionnaire:
                    if get_result(tracking) >= get_aproval_line(tracking):
                        evaluation_state = _('Aprobado')
                    elif required_tries == tracking.video.max_retries:
                        evaluation_state = _('Reprobado')
                    else: 
                        evaluation_state = _('Incompleto')
                else:
                    evaluation_state = _('Incompleto')
            else:
                evaluation_state = _('Sin iniciar')
        else:
            has_evaluation = _('NO')
            result = '-'
            aproval_line = '-'
            evaluation_state = '-'
            required_tries = '-'
            evaluation_date_formatted = '-'

        data.append([tracking.user.name, tracking.user.last_name, tracking.user.email, 
            tracking.video.course.title, tracking.video.title, state, date_state,
            has_evaluation, evaluation_state, result, aproval_line, required_tries, 
            evaluation_date_formatted])
    
    return {
        'table_header': header,
        'table_data': data
    }

def get_result(tracking):
    result = None
    if tracking.total_questions_to_ask == 0 or tracking.total_correct_answered_questions == 0:
        result = 0
    else:
        result = int((tracking.total_correct_answered_questions * 100) / tracking.total_questions_to_ask)
    return result

def get_aproval_line(tracking):
    aproval_line = None
    if tracking.video.min_correct_questions == 0:
        aproval_line = 0
    else:
        aproval_line = int((tracking.video.min_correct_questions * 100) / tracking.total_questions_to_ask)
    return aproval_line

def get_last_state_date(tracking):
    date = tracking.last_state_timestamp
    if date:
        return get_fromatted_date(date)
    else:
        return '-'

def get_fromatted_date(date):
    return str(date.day) + '/' + str(date.month) + '/' + str(date.year)

def xls_enrollments(request):
    return xls_from_stats_data( stats_data_enrollments() )

def html_enrollments(request):
    stats_data = stats_data_enrollments()
    return html_from_stats_data(request, stats_data)

def xls_potential_users(request, courseID):
    return xls_from_stats_data( stats_data_potential_users(courseID) )

def html_potential_users(request, courseID):
    stats_data = stats_data_potential_users(courseID)
    return html_from_stats_data(request, stats_data)

def xls_users_per_course(request):
    return xls_from_stats_data( stats_data_users_per_course(request.user) )

def html_users_per_course(request):
    stats_data = stats_data_users_per_course(request.user)
    return html_from_stats_data(request, stats_data)

def xls_progress_summary_per_course(request, courseID):
    course = get_object_or_404(Course, id=courseID)
    return xls_from_stats_data( stats_data_progress_summary_per_course(course) )

def xls_potential_users_per_course(request):
    return xls_from_stats_data( stats_data_potential_users_per_course(request.user) )

def html_potential_users_per_course(request):
    stats_data = stats_data_potential_users_per_course(request.user)
    return html_from_stats_data(request, stats_data) 

def html_progress_summary_per_course(request, courseID):
    course = get_object_or_404(Course, id=courseID)
    return html_from_stats_data(request, stats_data_progress_summary_per_course(course) )

def xls_dropout_ranking(request, courseID):
    course = get_object_or_404(Course, id=courseID)
    return xls_from_stats_data( stats_data_dropout_ranking(course) )

def html_dropout_ranking(request, courseID):
    course = get_object_or_404(Course, id=courseID)
    return html_from_stats_data(request, stats_data_dropout_ranking(course) )

def xls_failed_questions(request, courseID):
    course = get_object_or_404(Course, id=courseID)
    return xls_from_stats_data( stats_data_failed_questions(course) )

def html_failed_questions(request, courseID):
    course = get_object_or_404(Course, id=courseID)
    return html_from_stats_data(request, stats_data_failed_questions(course) )

def xls_users_completed(request):
    return xls_from_stats_data( stats_data_users_completed(request.user) )

def html_users_completed(request):
    return html_from_stats_data(request, stats_data_users_completed(request.user) )

def xls_users_evolution(request):
    last_evorep = UsersEvolutionReport.objects.filter(present=True).order_by('-started').first()
    return FileResponse(last_evorep.file.file, as_attachment=True)

def xls_users_evolution_per_course(request, courseID):
    course = Course.objects.filter(pk=courseID).first()
    last_report = UsersEvolutionPerCourseReport.objects.filter(present=True, course=course).order_by('-started').first()
    return FileResponse(last_report.file.file, as_attachment=True)

def html_users_evolution(request):
    return html_from_stats_data(request, stats_data_users_evolution() )

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['metrics'] = []
        current_url = resolve(self.request.path_info).url_name
        if current_url == 'dashboard':
            context['metrics'] = self.get_admin_metrics()
        self.add_tutor_metrics(context['metrics'])
        return context


    def get_admin_metrics(self):
        some_evorep = UsersEvolutionReport.objects.filter(present=True).exists()
        enrollments = CourseEnrollment.objects.all()
        metrics = [
            {
                'id': 1,
                'name': _('Cantidad de usuarios registrados'),
                'html_url': reverse('html_enrollments'),
                'xls_url': reverse('xls_enrollments'),
                'chart_number': enrollments.aggregate(users=Count('user', distinct=True))['users'],
            },
            {
                'id': 2,
                'name': _('Usuarios por curso'),
                'data': stats_data_users_per_course(self.request.user),
                'chart_type': 'column',
                'chart_columns': [
                    ('string', _('Curso')),
                    ('number', _('Usuarios')),
                ],
                'html_url': reverse('html_users_per_course'),
                'xls_url': reverse('xls_users_per_course')
            },
            {
                'id': 3,
                'name': _('Usuarios habilitados por curso'),
                'data': stats_data_potential_users_per_course(self.request.user),
                'chart_type': 'column',
                'chart_columns': [
                    ('string', _('Curso')),
                    ('number', _('Usuarios')),
                ],
                'html_url': reverse('html_potential_users_per_course'),
                'xls_url': reverse('xls_potential_users_per_course')
            },
            {
                'id': 4,
                'name': _('Cantidad de Usuarios que culminaron cada curso'),
                'data': stats_data_users_completed(self.request.user),
                'chart_type': 'column',
                'chart_columns': [
                    ('string', _('Curso')),
                    ('number', _('Usuarios registrados')),
                    ('number', _('Usuarios que culminaron el curso')),
                ],
                'html_url': reverse('html_users_completed'),
                'xls_url': reverse('xls_users_completed')
            },
            {
                'id': 5,
                'name': _('Evolución de Usuarios'),
                'img': 'img/xsl-icon.png',
                'html_url': None,  # reverse('html_users_evolution'),
                'xls_url': reverse('xls_users_evolution') if some_evorep else None
            },
        ]
        return metrics
    
    def add_tutor_metrics(self, metrics):
        courses = Course.objects.with_count_of_potential_users()
        current_url = resolve(self.request.path_info).url_name
        if current_url == 'dashboard_tutor':
            courses = self.request.user.tutored_courses.with_count_of_potential_users()
        for course in courses:
            metrics.append({
                'id': f"6_{course.id}",
                'name': _('Progreso'),
                'subtitle': course.title,
                'data': stats_data_progress_summary_per_course_treemap(course),
                'chart_type': 'treemap',
                'chart_columns': [
                    ('string', _('Tarea')),
                    ('string', _('Segmento')),
                    ('number', _('Cantidad de usuarios que lo completaron'))
                ],
                'html_url': reverse('html_progress_summary_per_course', args=[course.pk]),
                'xls_url': reverse('xls_progress_summary_per_course', args=[course.pk])
            })
            metrics.append({
                'id': f"7_{course.id}",
                'name': _('Puntos de abandono'),
                'subtitle': course.title,
                'data': stats_data_dropout_ranking(course),
                'chart_type': 'pie',
                'chart_columns': [
                    ('string', _('Segmento')),
                    ('number', _('Cantidad de usuarios que lo completaron')),
                ],
                'html_url': reverse('html_dropout_ranking', args=[course.pk]),
                'xls_url': reverse('xls_dropout_ranking', args=[course.pk])
            })
            metrics.append({
                'id': f"8_{course.id}",
                'name': _('Preguntas mal respondidas'),
                'subtitle': course.title,
                'data': stats_data_failed_questions(course),
                'chart_type': 'pie',
                'chart_columns': [
                    ('string', _('Pregunta')),
                    ('number', _('Cantidad de respuestas incorrectas')),
                ],
                'html_url': reverse('html_failed_questions', args=[course.pk]),
                'xls_url': reverse('xls_failed_questions', args=[course.pk])
            })
            if current_url == 'dashboard_tutor':
                metrics.append({
                    'id': f"9_{course.id}",
                    'name': _('Usuarios habilitados'),
                    'subtitle': course.title,
                    'html_url': reverse('html_potential_users', args=[course.pk]),
                    'xls_url': reverse('xls_potential_users', args=[course.pk]),
                    'chart_number': course.potential_users
                })
                some_report = UsersEvolutionPerCourseReport.objects.filter(present=True, course=course).exists()
                metrics.append({
                    'id': f"10_{course.id}",
                    'name': _('Evolución de Usuarios'),
                    'subtitle': course.title,
                    'img': 'img/xsl-icon.png',
                    'html_url': None,
                    'xls_url': reverse('xls_users_evolution_per_course', args=[course.pk]) if some_report else None
                }),

        return metrics



class DownloadableDocumentListView(ListView):
    model = DownloadableDocument
    template_name = 'cursos/todas_las_descargas.html'

    def get_queryset(self):
        segment_trackings_for_user_watched_full = SegmentTracking.objects.filter(
            user=self.request.user, watched_full=True
        ).values_list('video_id')
        filtered_segments_ids = Segment.objects.filter(id__in=segment_trackings_for_user_watched_full).values_list('id')
        documents = DownloadableDocument.objects.filter(video__in=filtered_segments_ids)
        return documents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = self.object_list
        courses = Course.objects.filter(id__in=documents.values_list('video__course__id')).order_by('order')
        courses_with_documents = OrderedDict()
        for course in courses:
            segments_ids_for_course_with_documents = documents.filter(
                video__course__id=course.id
            ).values_list('video__id')
            segments = Segment.objects.filter(id__in=segments_ids_for_course_with_documents).order_by('order')
            segments_with_documents = OrderedDict()
            for segment in segments:
                segments_with_documents[segment.id] = {
                    'segment': segment,
                    'documents': documents.filter(video__id=segment.id).order_by('name')
                }
                courses_with_documents[course.id] = {
                    'course': course,
                    'segments_with_documents': segments_with_documents
                }
        context['courses_with_documents'] = courses_with_documents
        return context

class CourseCompletionCertificateListView(ListView):
    model = CourseEnrollment
    template_name = 'cursos/mis_certificados.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update({
            'page_title': 'Constancias'
        })
        return ctx

    def get_queryset(self):
        courses_enrollments = CourseEnrollment.objects.filter(
            user=self.request.user,
            is_complete=True
        )
        return courses_enrollments

class DeleteCourseTracking(APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post']

    def post(self, request):
        course = Course.objects.get(pk=request.POST.get('course'))
        reset_course_tracking(course)
        return Response(True)

class DeleteUserCourseTracking(APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['post']

    def post(self, request):
        course = Course.objects.get(pk=request.POST.get('course'))
        emails = request.POST.getlist('user_emails[]')
        for email in emails:
            reset_user_tracking_for_course(email, course)
        return Response(True)

