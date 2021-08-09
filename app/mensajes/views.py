import json
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.db.models import Q
from collections import OrderedDict
from django.core.paginator import Paginator
from django.shortcuts import redirect
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .helpers import generar_conversacion
from .tasks import task_generar_conversacion
from .models import Conversacion, Mensaje, GeneradorConversaciones
from cursos.models import Course, CourseEnrollment, Area, AllowedDomain
from users.models import User


class InboxView(ListView):
    template_name = 'mensajes/inbox.html'
    model = Conversacion
    context_object_name = 'conversaciones'
    ordering = ('-fecha_ultimo_mensaje')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = self.object_list.filter(
            Q(iniciador=self.request.user) | Q(destinatario=self.request.user)
        )
        paginator = Paginator(object_list, 20)
        page_number = 1
        if self.kwargs.get('page') and paginator.num_pages >= int(self.kwargs.get('page')):
            page_number = int(self.kwargs.get('page'))
        breadcrumb = OrderedDict() 
        breadcrumb['first']= { 'title': _('Inbox') }
        if paginator.num_pages > 1:
            context['pagination_data'] = {
                'current_page': page_number,
                'total_pages': paginator.num_pages,
                'last_page': page_number - 1,
                'next_page': page_number + 1
            }
            breadcrumb['page1'] = page_number
            breadcrumb['page2'] = paginator.num_pages
        conversaciones = OrderedDict()
        for conv in paginator.page(page_number):
            readed = conv.last_message_readed(self.request.user)
            if readed == None or readed:
                conversaciones[conv] = True
            else:
                conversaciones[conv] = False
        context['conversaciones'] = conversaciones
        context['breadcrumb'] = breadcrumb
        return context


class ConversacionView(TemplateView):
    template_name = 'mensajes/conversacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conv = Conversacion.objects.filter(pk=self.kwargs.get('conversacion')).first()
        if conv:
            context['conversacion'] = conv
            context['mensajes'] = conv.mensajes.order_by('fecha_creacion')
            if conv.curso:
                context['course_url'] = reverse('course', kwargs={'course': conv.curso.slug})
            self.set_mensajes_as_read(conv.mensajes)
        context['breadcrumb'] = {
            'first': { 'title': _('Inbox'), 'url': reverse('mensajes:inbox') },
            'second': { 'title': conv.asunto }
        }
        return context
    
    def set_mensajes_as_read(self, mensajes): 
        for men in mensajes.filter(receptor=self.request.user):
            men.leido = True
            men.fecha_leido = datetime.now()
            men.save()


def send_message(request):
    conversacion = Conversacion.objects.filter(pk=request.POST.get('conv_id')).first()
    mensaje = Mensaje()
    mensaje.conversacion = conversacion
    mensaje.emisor = request.user
    if not conversacion.iniciador == request.user:
        mensaje.receptor = conversacion.iniciador
    else:
        mensaje.receptor = conversacion.destinatario
    mensaje.cuerpo = request.POST.get('cuerpo')
    mensaje.save()
    return redirect(reverse('mensajes:conversacion', args=(conversacion.id,)))


class IniciarConversacionView(TemplateView):
    template_name = 'mensajes/iniciar_conversacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config = OrderedDict()
        if self.kwargs.get('preselect', None):
            config["preSelect"] = self.kwargs.get('preselect', None)
        if self.request.user.is_staff:
            config["isAdmin"] = True,
            config["allAreas"] = self.get_json(Area.objects.all())
            config["allDomains"] = self.get_json(AllowedDomain.objects.all())
            config["allUsers"] = self.get_users_json(True)
            config["allCourses"] = self.get_json(Course.objects.all())
        else:
            config["isAdmin"] = False
        if self.request.user.is_tutor:
            config["isTutor"] = True
            config["tutorUsers"] = self.get_users_json(False)
            config["tutorCourses"] = self.get_tutored_courses_json()
        else:
            config["isTutor"] = False
        config["myCourses"] = self.get_json(Course.objects.all(), False, True)
        context['config'] = json.dumps(config)
        context['breadcrumb'] = {
            'first': { 'title': _('Inbox'), 'url': reverse('mensajes:inbox') },
            'second': { 'title': _('Nuevo mensaje') }
        }
        return context

    def get_users_json(self, all):
        if all:
            usuarios = User.objects.exclude(username=self.request.user.username)
        else:
            usuarios = User.objects.all().filter(enrollments__course__tutor=self.request.user)
        return self.get_json(usuarios, is_user=True)
    
    def get_tutored_courses_json(self):
        return self.get_json(self.request.user.tutored_courses.all())

    def get_json(self, query_set, is_user=False, is_course=False):
        dicList = []
        for val in query_set:
            newElement = OrderedDict()
            if is_user:
                newElement['name'] = val.name + ' ' + val.last_name
            else: 
                newElement['name'] = val.__str__()
            newElement['id'] = val.id
            if is_course:
                if not val.tutor == None:
                    newElement['tutor'] = val.tutor.name + ' ' + val.tutor.last_name
            dicList.append(newElement)
        return dicList

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        receptor_valid = None
        create_as = None
        if request.user.is_staff and request.user.is_tutor:
            if request.POST.get('send_as') == 'Admin':
                receptor_valid = self.valid_admin()
                create_as = 'Admin'
            elif request.POST.get('send_as') == 'Tutor':
                receptor_valid = self.valid_tutor()
                create_as = 'Tutor'
        elif request.user.is_staff:
            receptor_valid = self.valid_admin()
            create_as = 'Admin'
        elif request.user.is_tutor:
            receptor_valid = self.valid_tutor()
            create_as = 'Tutor'
        if request.POST.get('send_as') == 'Alumno':
            receptor_valid = self.valid_student()
            create_as = 'Student'
        if not receptor_valid:
            context['error'] = _('Seleccione un destinatario')
        elif not request.POST.get('asunto'):
            context['error'] = _('Ingrese un asunto')
        elif not request.POST.get('cuerpo'):
            context['error'] = _('Ingrese un mensaje')
        else:
            self.create_generator(create_as)
            return redirect('mensajes:inbox')

        return super(TemplateView, self).render_to_response(context)

    def valid_admin(self):
        if self.valid_list('all_areas') or self.valid_list('all_domains') or self.valid_list('all_users') or self.valid_list('all_courses'):
            return True
        return False

    def valid_tutor(self):
        if self.valid_list('tutor_users') or self.valid_list('tutor_courses'):
            return True
        return False

    def valid_student(self):
        if self.request.POST.get('my_courses'):
            return True
        return False
    
    def valid_list(self, list_name):
        if self.request.POST.get(list_name) and not len(json.loads(self.request.POST.get(list_name))) == 0:
            return True
        return False

    def create_generator(self, create_as):
        generador = GeneradorConversaciones()
        generador.iniciador = self.request.user
        generador.asunto = self.request.POST.get('asunto')
        generador.cuerpo = self.request.POST.get('cuerpo')
        if self.request.POST.get('courses_options') == 'enrolled':
            generador.curso_solo_inscriptos = True
        else:
            generador.curso_solo_inscriptos = False
        if self.request.POST.get('related_course'):
            related_course = self.request.POST.get('related_course')
            generador.curso = Course.objects.filter(pk=json.loads(related_course)).first()
        generador.save()
        if create_as == 'Admin':
            generador.permite_responder = False
            if self.valid_list('all_areas'):
                all_areas = self.request.POST.get('all_areas')
                generador.areas_destino.set(Area.objects.filter(pk__in=json.loads(all_areas)))
            if self.valid_list('all_domains'):
                all_domains = self.request.POST.get('all_domains')
                generador.dominios_destino.set(AllowedDomain.objects.filter(pk__in=json.loads(all_domains)))
            if self.valid_list('all_users'):
                all_users = self.request.POST.get('all_users')
                generador.usuarios_destino.set(User.objects.filter(pk__in=json.loads(all_users)))
            if self.valid_list('all_courses'):
                all_courses = self.request.POST.get('all_courses')
                generador.cursos_destino.set(Course.objects.filter(pk__in=json.loads(all_courses)))
        elif create_as == 'Tutor':
            generador.permite_responder = True
            if self.valid_list('tutor_users'):
                tutor_users = self.request.POST.get('tutor_users')
                generador.usuarios_destino.set(User.objects.filter(pk__in=json.loads(tutor_users)))
            if self.valid_list('tutor_courses'):
                tutor_courses = self.request.POST.get('tutor_courses')
                generador.cursos_destino.set(Course.objects.filter(pk__in=json.loads(tutor_courses)))
        elif create_as == 'Student':
            generador.permite_responder = True
            my_courses = json.loads(self.request.POST.get('my_courses'))
            generador.usuarios_destino.set(User.objects.filter(tutored_courses__pk=my_courses))
        generador.save()
        task_generar_conversacion.delay(generador.id)


def generar_conversaciones(request):
    # TODO: validar usuario? validar autenticación?
    # TODO: no entiendo esto. Y no está autenticado.
    for gc in GeneradorConversaciones.objects.filter(conv_generadas=None):
        generar_conversacion(gc)
    return redirect('/')


class UnreadMessages(APIView):
    """
    Para obtener un contador de mensajes sin leer.
    """
    permission_classes = [IsAuthenticated, ]
    http_method_names = ['get']

    def get(self, request, format=None):
        unread = Mensaje.objects.all().filter(Q(receptor=request.user) & Q(leido=False)).count()
        return Response(unread)
