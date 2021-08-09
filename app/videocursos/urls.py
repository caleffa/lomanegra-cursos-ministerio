"""videocursos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.views.i18n import JavaScriptCatalog

from django.views.generic import TemplateView
from rest_framework import routers

from cursos.views import (HomeView, CourseListView, VideoDetailView, GeniallyDetailView, QuestionnaireView, SegmentTrackingViewset,
                          download_document, CourseCompletionCertificateView, CourseDetailView, xls_enrollments,
                          xls_users_per_course, xls_progress_summary_per_course, xls_dropout_ranking,
                          xls_failed_questions, xls_users_completed, xls_users_evolution, html_enrollments,
                          html_users_per_course, html_progress_summary_per_course, html_dropout_ranking,
                          html_failed_questions, html_users_completed, DashboardView, GenericDetailView,
                          CourseFinishedView, SlideDetailView, MaxRetrialsExhaustedView, DownloadableDocumentListView,
                          CourseCompletionCertificateListView, ViewDocumentView, CertificateView, MultipleSessionsView,
                          CareerTrackListView, CoursesListView, CourseEnrollmentCreateView,
                          xls_potential_users_per_course, html_potential_users_per_course, html_potential_users,
                          xls_potential_users, xls_users_evolution_per_course, LandingView, CourseUnenrollDeleteView,
                          DeleteCourseTracking, DeleteUserCourseTracking, LiveDetailView, authenticate_view,
                          CareerTrackCategoriesListView, PublicCareerTrackListView, PublicCareerTrackCategoriesListView)

from cursos import api_views as cursos_api_views
from encuestas import api_views as encuestas_api_views
from users.views import CustomLoginView
from backoffice.admin import admin_light
from foros.views import ForumOrderList, ForumViewSet
from tareas.views import TareaViewSet, AdjuntoViewSet
from streaming.views import SegmentIsLiveViewSet

router = routers.SimpleRouter()
router.register('track/vp', SegmentTrackingViewset)
router.register('course', cursos_api_views.CourseViewSet)
router.register('segment', cursos_api_views.SegmentViewSet)
router.register('livestream', cursos_api_views.LiveStreamSegmentViewSet)
router.register('segmentsection', cursos_api_views.SegmentSectionViewSet)
router.register('downloadabledocument', cursos_api_views.DownloadableDocumentViewSet)
router.register('option', cursos_api_views.OptionViewSet)
router.register('question', cursos_api_views.QuestionViewSet)
router.register('slide', cursos_api_views.SlideViewSet)
router.register('pregunta', encuestas_api_views.PreguntaEncuestaViewSet)
router.register('opcion_pregunta', encuestas_api_views.OpcionPreguntaEncuestaViewSet)
router.register('forum', ForumViewSet)
router.register('tarea', TareaViewSet)
router.register('adjunto', AdjuntoViewSet)
router.register('segment_is_live', SegmentIsLiveViewSet)

normal_user_test = user_passes_test(lambda u: u.is_authenticated and (not u.is_stakeholder or u.is_staff or u.is_tutor),
                                    login_url='/dashboard', redirect_field_name=None)
dashboard_test = user_passes_test(lambda u: u.is_authenticated and (u.is_stakeholder or u.is_staff or u.is_tutor),
                                  login_url='/', redirect_field_name=None)
dashboard_admin_test = user_passes_test(lambda u: u.is_authenticated and (u.is_stakeholder or u.is_staff),
                                        login_url='/', redirect_field_name=None)
dashboard_tutor_test = user_passes_test(lambda u: u.is_authenticated and u.is_tutor,
                                        login_url='/', redirect_field_name=None)


def anonymous_user(user):
    return not user.is_authenticated


categories_public_test = user_passes_test(anonymous_user, login_url=reverse_lazy('categories'), redirect_field_name=None)


apipatterns = ([
    path('course_segments/<int:course>', cursos_api_views.SegmentOrderList.as_view(), name='course-segments-list'),
    path('course_live_streams/<int:course>', cursos_api_views.LiveStreamOrderList.as_view(), name='course-live-streams-list'),
    path('segment_sections/<int:segment>', cursos_api_views.SegmentSectionOrderList.as_view(), name='segments-section-list'),
    path('encuesta/<int:encuesta>/preguntas', encuestas_api_views.PreguntaListAPIView.as_view(), name='encuesta-pregunta-list'),
    path('set_preguntas_order', encuestas_api_views.SetPreguntasOrderViewSet.as_view()),
    path('forums/<int:segment>', ForumOrderList.as_view(), name='forum-list'),
] + router.urls, 'api')


urlpatterns = [
    # re_path(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    # re_path(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path(
        "users/",
        include("users.urls", namespace="users"),
    ),
    path('publico/cursos-cortos/<int:category>/', PublicCareerTrackCategoriesListView.as_view(), name='public-career-track-categories-list'),
    path('publico/cursos-cortos/', categories_public_test(PublicCareerTrackListView.as_view()), name='public-career-track-list'),
    path('publico/', include('public.urls')),
    path("foros/", include("foros.urls")),
    path("transmisiones/", include("streaming.urls")),
    path("tareas/", include("tareas.urls", namespace="tareas")),
    path("encuestas/", include("encuestas.urls")),
    path("mensajes/", include("mensajes.urls")),
    path('api/', include(apipatterns)),
    path('accounts/landing/', LandingView.as_view(), name='landing'),
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path("accounts/", include("allauth.urls")),
    path("accounts/multiple_sessions", MultipleSessionsView.as_view(), name='multiple-sessions'),
    path('admin/', admin.site.urls),
    path('admin_light/', admin_light.urls),
    # path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    path('authenticate/', authenticate_view, name='authenticate'),
    path('home', login_required(HomeView.as_view()), name='home'),
    path('', login_required(CareerTrackListView.as_view()), name='categories'),
    path('categoria/<int:category>', login_required(CareerTrackCategoriesListView.as_view()), name='category_courses'),
    path('inscripcion/<int:course>', login_required(CourseEnrollmentCreateView.as_view()), name='enroll_course'),
    path('desinscripcion/<int:course>', login_required(CourseUnenrollDeleteView.as_view()), name='unenroll_course'),
    path('cursos', normal_user_test(CourseListView.as_view()), name='cursos'),
    path('curso/<slug:course>', normal_user_test(CourseDetailView.as_view()), name='course'),
    path('cursos/<slug:course>/<int:order>', normal_user_test(VideoDetailView.as_view()), name='video'),
    path('cursos/<slug:course>/genially/<int:order>', normal_user_test(GeniallyDetailView.as_view()), name='genially'),
    path('cursos/<slug:course>/live/<int:order>', normal_user_test(LiveDetailView.as_view()), name='live'),
    path('cursos/<slug:course>/slides/<int:order>', normal_user_test(SlideDetailView.as_view()), name='slide'),
    path('cursos/<slug:course>/generic/<int:order>', normal_user_test(GenericDetailView.as_view()), name='generic'),
    path('cursos/<slug:course>/slides/<int:order>/<int:slide>', normal_user_test(SlideDetailView.as_view()), name='slide_specific'),
    path('cursos/<slug:course>/<int:order>/cuestionario', normal_user_test(QuestionnaireView.as_view()), name='questionnaire'),
    path('cursos/<slug:course>/<int:order>/failed', normal_user_test(MaxRetrialsExhaustedView.as_view()), name='failed'),
    path('cursos/<int:course_enrollment>/diploma', normal_user_test(CourseCompletionCertificateView.as_view()), name='diploma'),
    path('cursos/<int:pk>/ver_diploma', normal_user_test(CertificateView.as_view()), name='view-diploma'),
    path('cursos/<slug:course>/diploma', normal_user_test(CourseFinishedView.as_view()), name='get-diploma'),
    path('downloads', normal_user_test(DownloadableDocumentListView.as_view()), name='downloads'),
    path('descargar_documento/<int:documentpk>', normal_user_test(download_document), name='download_document'),
    path('ver_documento/<int:pk>', normal_user_test(ViewDocumentView.as_view()), name='view_document'),
    path('mis_constancias', normal_user_test(CourseCompletionCertificateListView.as_view()), name='diplomas'),
    path('borrar_tracking_curso', normal_user_test(DeleteCourseTracking.as_view()), name='borrar-tracking-curso'),
    path('borrar_tracking_usuario_curso', normal_user_test(DeleteUserCourseTracking.as_view()), name='borrar-tracking-usuario-curso'),

    #path('busqueda-cursos', login_required(CoursesListView.as_view()), name='courses_search'),
    path('mis-cursos', login_required(CoursesListView.as_view()), name='enrolled_courses'),
    path('proximos-cursos', login_required(CoursesListView.as_view()), name='not_started_courses'),

    path('dashboard', dashboard_admin_test(DashboardView.as_view()), name='dashboard'),
    path('dashboard/xls_enrollments', dashboard_admin_test(xls_enrollments), name='xls_enrollments'),
    path('dashboard/xls_users_per_course', dashboard_admin_test(xls_users_per_course), name='xls_users_per_course'),
    path('dashboard/xls_potential_users_per_course', dashboard_admin_test(xls_potential_users_per_course), name='xls_potential_users_per_course'),
    path('dashboard/xls_users_completed', dashboard_admin_test(xls_users_completed), name='xls_users_completed'),
    path('dashboard/evolucion_usuarios', dashboard_admin_test(xls_users_evolution), name='xls_users_evolution'),
    path('dashboard/html_enrollments', dashboard_admin_test(html_enrollments), name='html_enrollments'),
    path('dashboard/html_users_per_course', dashboard_admin_test(html_users_per_course), name='html_users_per_course'),
    path('dashboard/html_potential_users_per_course', dashboard_admin_test(html_potential_users_per_course), name='html_potential_users_per_course'),
    path('dashboard/html_users_completed', dashboard_admin_test(html_users_completed), name='html_users_completed'),

    path('dashboard/tutor', dashboard_tutor_test(DashboardView.as_view()), name='dashboard_tutor'),
    path('dashboard/xls_potential_users/<int:courseID>', dashboard_tutor_test(xls_potential_users), name='xls_potential_users'),
    path('dashboard/html_potential_users/<int:courseID>', dashboard_tutor_test(html_potential_users), name='html_potential_users'),
    path('dashboard/evolucion_usuarios_por_curso/<int:courseID>', dashboard_tutor_test(xls_users_evolution_per_course), name='xls_users_evolution_per_course'),

    path('dashboard/html_progress_summary_per_course/<int:courseID>', dashboard_test(html_progress_summary_per_course), name='html_progress_summary_per_course'),
    path('dashboard/xls_progress_summary_per_course/<int:courseID>', dashboard_test(xls_progress_summary_per_course), name='xls_progress_summary_per_course'),
    path('dashboard/html_dropout_ranking/<int:courseID>', dashboard_test(html_dropout_ranking), name='html_dropout_ranking'),
    path('dashboard/xls_dropout_ranking/<int:courseID>', dashboard_test(xls_dropout_ranking), name='xls_dropout_ranking'),
    path('dashboard/html_failed_questions/<int:courseID>', dashboard_test(html_failed_questions), name='html_failed_questions'),
    path('dashboard/xls_failed_questions/<int:courseID>', dashboard_test(xls_failed_questions), name='xls_failed_questions'),

    path(r'session_security/', include('session_security.urls')),

    path(r'pagos/', include('pagos.urls')),

]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns

# descomentar para profiling
# urlpatterns += [path('silk', include('silk.urls', namespace='silk'))]
