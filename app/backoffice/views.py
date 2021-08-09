from django.views.generic import TemplateView, UpdateView, ListView, CreateView
from datetime import datetime

from cursos.models import Course
from encuestas.models import Encuesta
from users.models import User
from django.shortcuts import get_object_or_404, redirect


class AltaCursosView(TemplateView):
    template_name = 'alta_cursos.html'


class CourseAdminMixin:
    def get_form(self, form_class=None):
        from django.forms.fields import SplitDateTimeField
        from django.contrib.admin.widgets import AdminSplitDateTime
        form = super().get_form(form_class=form_class)
        form.fields['start_date'] = SplitDateTimeField(widget=AdminSplitDateTime())
        return form


class CourseAdminCreateView(CourseAdminMixin, CreateView):
    model = Course
    fields = [
        'title',
        'description',
        'slug',
        'image',
        'order',
        'certificate_template',
        'start_date',
        'categories',
        'tutor',
        'price',
        'price_currency',
    ]
    template_name = 'course_update.html'

    def get_success_url(self):
        return '/admin_light/cursos/course/curso/' + str(self.object.id)


class CourseAdminUpdateView(CourseAdminMixin, UpdateView):
    model = Course
    fields = [
        'title',
        'description',
        'slug',
        'image',
        'order',
        'certificate_template',
        'start_date',
        'categories',
        'tutor',
        'price',
        'price_currency',
    ]
    template_name = 'course_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = Course.objects.get(pk=self.kwargs['pk'])
        context['users_with_tracking'] = User.objects.filter(enrollments__course=course)
        return context

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        Course.objects.rearrange_orders(leave_gap=form.cleaned_data['order'], move_into_gap=self.object)
        return super().form_valid(form)


class CourseListView(ListView):
    model = Course
    template_name = 'course_list.html'
    context_object_name = 'courses_list'
    paginate_by = 20


class EncuestaAdminListView(ListView):
    model = Encuesta
    template_name = 'encuesta_list.html'
    context_object_name = 'encuestas_list'
    paginate_by = 20


class EncuestaAdminCreateView(CreateView):
    model = Encuesta
    fields = [
        'nombre',
        'texto',
        'donde',
        'cursos',
        'inicio',
        'vencimiento',
        'obligatoria',
        'mensaje_gracias',
        'sectores_target',
        'dominios_target',
        'usuarios_target'
    ]
    template_name = 'encuestas/encuesta_admin.html'

    def get_success_url(self):
        return '/admin_light/encuestas/' + str(self.object.id)


class EncuestaAdminUpdateView(UpdateView):
    model = Encuesta
    fields = [
        'nombre',
        'texto',
        'donde',
        'cursos',
        'inicio',
        'vencimiento',
        'obligatoria',
        'mensaje_gracias',
        'sectores_target',
        'dominios_target',
        'usuarios_target'
    ]
    template_name = 'encuestas/encuesta_admin.html'

    def get_initial(self):
        initial = super(EncuestaAdminUpdateView, self).get_initial()
        encuesta = Encuesta.objects.filter(pk=self.kwargs['pk']).first()
        initial['nombre'] = encuesta.nombre
        initial['texto'] = encuesta.texto
        initial['donde'] = encuesta.donde
        initial['inicio'] = encuesta.inicio
        initial['vencimiento'] = encuesta.vencimiento
        initial['obligatoria'] = encuesta.obligatoria
        initial['sectores_target'] = encuesta.sectores_target
        initial['dominios_target'] = encuesta.dominios_target
        initial['usuarios_target'] = encuesta.usuarios_target
        return initial

    def get_success_url(self):
        return '/admin_light/encuestas/' + str(self.object.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        encuesta = Encuesta.objects.filter(pk=self.kwargs['pk']).first()
        context['cursos_ids'] = encuesta.cursos.values_list('id', flat=True)
        context['sectores_ids'] = encuesta.sectores_target.values_list('id', flat=True)
        context['dominios_ids'] = encuesta.dominios_target.values_list('id', flat=True)
        context['usuarios_ids'] = encuesta.usuarios_target.values_list('id', flat=True)
        return context


class CourseCloneView(TemplateView):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, pk=request.POST.get('c'))
        new_course = course.clone()
        return redirect('/admin_light/cursos/course/curso/' + str(new_course.pk))
