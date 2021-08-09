from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from solo.admin import SingletonModelAdmin
from users.models import User
from .models import (SiteSettings, Course, Segment, DownloadableDocument, Question, Option, CourseEnrollment,
                     SegmentTracking, Questionnaire, QuestionnaireQuestion, QuestionnaireOption,
                     DownloadableDocumentTracking, Slide, AllowedEmail, AllowedDomain, Area, SegmentSection,
                     Category, CareerTrack)
from .helpers import reset_user_tracking

from allauth.account.models import EmailConfirmation, EmailAddress
from allauth.account.admin import EmailAddressAdmin
from foros.models import Forum, ForumMessage, ForumMessageHistoryRecord
from encuestas.models import Encuesta, Pregunta, OpcionPregunta, EncuestaTracking, Respuesta
from encuestas.helpers import reset_user_polls_tracking



class DefaultAdmin(admin.AdminSite):
    def has_permission(self, request):
        return request.user.is_active and request.user.is_superuser


# admin.site = DefaultAdmin()

def new_token(modeladmin, request, queryset):
    for ea in queryset:
        ea.send_confirmation(request=request)
new_token.short_description = _('Generar nuevo token de verificación')


class EveryComplianceEmailAddressAdmin(EmailAddressAdmin):
    actions = [new_token]


admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EveryComplianceEmailAddressAdmin)


class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


class SegmentAdmin(admin.ModelAdmin):
    exclude = ['thumb_path']
    list_filter = ['course']
    list_display = ['title', 'order', 'course']


class SegmentSectionAdmin(admin.ModelAdmin):
    list_filter = ['segment']
    list_display = ['segment', 'order', 'questions_to_ask']


class DownloadableDocumentAdmin(admin.ModelAdmin):
    list_display = ('get_course', 'video', '__str__')

    def get_course(self, obj):
        return obj.video.course


class OptionInlineAdmin(admin.TabularInline):
    model = Option
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ['section', 'section__segment']
    list_display = ['text', 'section']
    inlines = [OptionInlineAdmin]


class OptionAdmin(admin.ModelAdmin):
    list_filter = ['question', 'question__section', 'question__section__segment']


class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'is_complete')


class SegmentTrackingAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'watched_full', 'user_has_downloaded_all_documents')


class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('video', 'user', 'is_complete', 'score')


class QuestionnaireQuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'questionnaire', 'answered')


class AreaAdmin(admin.ModelAdmin):
    list_display = ('name','get_enabled_courses_display')
    list_filter = ['enabled_courses']
    filter_horizontal = ['enabled_courses']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('order', 'title')


class CareerTrackAdmin(admin.ModelAdmin):
    list_display = ('order', 'title')


def reset_tracking(modeladmin, request, queryset):
    for u in queryset:
        reset_user_tracking(u.email)
reset_tracking.short_description = _("Borrar trackings de usuarios seleccionados")


def reset_poll_tracking(modeladmin, request, queryset):
    for u in queryset:
        reset_user_polls_tracking(u.email)
reset_poll_tracking.short_description = _("Borrar trackings de ENCUESTAS de usuarios seleccionados")


def generar_token_de_verificacion(modeladmin, request, queryset):
    for u in queryset:
        email_address = EmailAddress.objects.get(user=u, email=u.email)
        ec = EmailConfirmation.create(email_address)
        ec.send(request=request)
generar_token_de_verificacion.short_description = _("Generar nuevo token de verificación")


class DjangoUserAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'last_name', 'email', 'area', 'all_enabled_courses_display', 'is_staff', 'is_tutor', 'is_stakeholder'
    ]
    search_fields = ['name', 'last_name', 'email']
    list_filter = ['is_staff', 'is_tutor', 'is_stakeholder']
    list_per_page = 10
    list_editable = ['is_staff', 'is_tutor', 'is_stakeholder']
    fields = [
        'name', 'last_name', 'email', 'enabled_courses', 'is_staff', 'is_tutor', 'is_stakeholder',
        'all_enabled_courses_display'
    ]
    readonly_fields = ['name', 'last_name', 'email', 'all_enabled_courses_display']
    filter_horizontal = ['enabled_courses']
    list_display_links = ['name', 'last_name', 'email']
    actions = [reset_tracking, reset_poll_tracking, generar_token_de_verificacion]

    def has_add_permission(self, request):
        return False

    def all_enabled_courses_display(self, obj):
        return ' | '.join((c.title for c in Course.objects.allows_user(obj).distinct()))
    all_enabled_courses_display.short_description = _('Cursos habilitados (directa e indirectamente)')


admin.site.unregister(User)
admin.site.register(User, DjangoUserAdmin)

admin.site.register(DownloadableDocumentTracking)
admin.site.register(Questionnaire, QuestionnaireAdmin)
admin.site.register(QuestionnaireQuestion, QuestionnaireQuestionAdmin)
admin.site.register(QuestionnaireOption)
admin.site.register(Slide)
admin.site.register(AllowedEmail)
admin.site.register(AllowedDomain)
admin.site.register(Area, AreaAdmin)
admin.site.register(Encuesta)
admin.site.register(Pregunta)
admin.site.register(OpcionPregunta)
admin.site.register(EncuestaTracking)
admin.site.register(Respuesta)
admin.site.register(SiteSettings, SingletonModelAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(CourseEnrollment, CourseEnrollmentAdmin)
admin.site.register(SegmentTracking, SegmentTrackingAdmin)
admin.site.register(SegmentSection, SegmentSectionAdmin)
admin.site.register(DownloadableDocument, DownloadableDocumentAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(CareerTrack, CareerTrackAdmin)


