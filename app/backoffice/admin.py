from django.contrib import admin
from django.utils.html import format_html
from users.models import User
from cursos.models import Course, AllowedEmail, AllowedDomain, Area, Category, CareerTrack
from encuestas.models import Encuesta, Pregunta
# from cursos.helpers import reset_user_tracking

# from foros.models import Forum, ForumMessage, ForumMessageHistoryRecord
# from encuestas.models import Encuesta, Pregunta, OpcionPregunta, EncuestaTracking, Respuesta
# from encuestas.helpers import reset_user_polls_tracking

from .views import CourseAdminUpdateView, CourseListView, EncuestaAdminListView, EncuestaAdminCreateView, EncuestaAdminUpdateView, CourseAdminCreateView, CourseCloneView


class AdminLight(admin.AdminSite):
    site_header = 'Administración de cursos y usuarios'
    site_title = 'Administración de cursos y usuarios'
    index_title = 'Panel de administración - Atenea'
    index_template = 'admin_light/index.html'
    app_index_template = 'admin_light/app_index.html'
    logout_template = 'admin_light/registration/logged_out.html'
    password_change_template = 'admin_light/registration/password_change_form.html'
    password_change_done_template = 'admin_light/registration/password_change_done.html'
    # login_template = 'admin_light/login.html'

    # https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#adding-views-to-admin-sites
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        urls += [
            path('cursos/course/create', self.admin_view(CourseAdminCreateView.as_view()), name='course-admin-create'),
            path('cursos/course/curso/<int:pk>', self.admin_view(CourseAdminUpdateView.as_view()), name='course-admin-update'),
            path('cursos/course/', self.admin_view(CourseListView.as_view()), name="lista_cursos"),
            path('encuestas', self.admin_view(EncuestaAdminListView.as_view()), name="lista_encuestas"),
            path('encuestas/create', self.admin_view(EncuestaAdminCreateView.as_view()), name='encuesta_admin_create'),
            path('encuestas/<int:pk>', self.admin_view(EncuestaAdminUpdateView.as_view()), name='encuesta_admin_update'),
            path('clonar-curso', CourseCloneView.as_view(), name='clone_course')
        ]
        return urls




admin_light = AdminLight(name='admin_light')


class AdminLightAdminTemplatesMixin:
    change_list_template = 'admin_light/change_list.html'
    change_form_template = 'admin_light/change_form.html'
    add_form_template = None
    delete_confirmation_template = None
    delete_selected_confirmation_template = None
    object_history_template = None
    popup_response_template = None


class AreaAdminLight(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
    list_display = ('name', 'get_enabled_courses_display')
    list_filter = ['enabled_courses']
    filter_horizontal = ['enabled_courses']


# class CourseCertificateAdmin(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
#     list_display = ['title', 'description', 'certificate_template', 'certificate_template_tag']
#     list_editable = ['certificate_template']
#     readonly_fields = ['title', 'description']
#     fields = ['title', 'description', 'certificate_template']
#
#     def certificate_template_tag(self, obj):
#         return format_html(f'<img style="max-width: 100px;" src="{obj.certificate_template.url}" />' if obj.certificate_template else '')
#     certificate_template_tag.short_description = 'Plantilla del certificado (img)'
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def has_add_permission(self, request):
#         return False


class AllowedEmailAdmin(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
    list_display = ['email', 'area']
    search_fields = ['email']
    list_filter = ['area']
    list_editable = ['area']
    fields = ['email', 'area']
    list_per_page = 10

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['email']
        else:
            return []


class AllowedDomainAdmin(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
    list_display = ['domain', 'get_enabled_courses_display']
    fields = ['domain', 'enabled_courses']
    filter_horizontal = ['enabled_courses']
    search_fields = ['domain']
    list_per_page = 10

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['domain']
        else:
            return []


class AllowedEmailInline(admin.TabularInline):
    model = AllowedEmail
    fields = ['area']
    verbose_name = 'Área/Departamento/Sector del usuario'
    verbose_name_plural = 'Área/Departamento/Sector del usuario'
    template = 'admin_light/edit_inline/tabular.html'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class UserAdmin(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
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
    inlines = [AllowedEmailInline]

    def has_add_permission(self, request):
        return False

    def all_enabled_courses_display(self, obj):
        return ' | '.join((c.title for c in Course.objects.allows_user(obj).distinct()))
    all_enabled_courses_display.short_description = 'Cursos habilitados (directa e indirectamente)'


class CategoriesAdmin(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
    list_display = ['order', 'title', 'image']
    search_fields = ['title']
    list_per_page = 10
    list_editable = ['title', 'image']
    ordering = ['order']


class CareerTracksAdmin(AdminLightAdminTemplatesMixin, admin.ModelAdmin):
    list_display = ['order', 'title', 'image']
    search_fields = ['title']
    list_per_page = 10
    list_editable = ['title', 'image']
    ordering = ['order']


admin_light.register(Category, CategoriesAdmin)
admin_light.register(CareerTrack, CategoriesAdmin)
admin_light.register(Area, AreaAdminLight)
admin_light.register(AllowedEmail, AllowedEmailAdmin)
admin_light.register(AllowedDomain, AllowedDomainAdmin)
# admin_light.register(Course, CourseCertificateAdmin)
admin_light.register(User, UserAdmin)