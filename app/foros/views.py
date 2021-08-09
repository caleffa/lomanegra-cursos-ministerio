
from django.views.generic import ListView, FormView
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect

from rest_framework import viewsets, permissions
from . import authentication
from rest_framework import generics
from collections import OrderedDict

from cursos.models import Segment, SegmentTracking, Course
from .models import Forum, ForumMessage, ForumMessageHistoryRecord
from .forms import ForumMessageForm
from .serializers import ForumMessageSerializer, ForumSerializer

import json

class MyCommentsView(ListView):
    model = Forum
    template_name = 'my_comments.html'

    def get_queryset(self):
        segments = None
        if self.request.user.is_superuser:
            forums = Forum.objects.all()
        else:
            if self.request.user.is_tutor:
                tutored_courses_id = Course.objects.filter(tutor=self.request.user).values_list('id')
                segments = Segment.objects.filter(course__in=tutored_courses_id).values_list('id')
            else:
                tracking = SegmentTracking.objects.filter(
                    user=self.request.user  # , watched_full=True
                ).values_list('video_id')
                segments = Segment.objects.filter(id__in=tracking).values_list('id')
            forums = Forum.objects.filter(segment__in=segments)
        return forums

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forums = self.object_list
        courses = Course.objects.filter(id__in=forums.values_list('segment__course__id')).order_by('order')
        courses_with_forum = OrderedDict()
        for course in courses:
            segments_ids = forums.filter(segment__course__id=course.id).values_list('segment__id')
            segments = Segment.objects.filter(id__in=segments_ids).order_by('order')
            segments_with_forum = OrderedDict()
            for segment in segments:
                segments_with_forum[segment.id] = {
                    'segment': segment,
                    'forums': forums.filter(segment__id=segment.id).order_by('order')
                }
                courses_with_forum[course.id] = {
                    'course': course,
                    'segments_with_forum': segments_with_forum
                }
        context['courses_with_forum'] = courses_with_forum
        return context

class ForumView(ListView, FormView):
    model = ForumMessage
    form_class = ForumMessageForm
    template_name = 'forum_view.html'
    context_object_name = 'messages_list'
    paginate_by = 10
    ordering = ['-edited']

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context['forum'] = self.get_forum()
        current_page = int(self.request.GET.get('page', 1))
        first_page = 1
        if (current_page - 3) > 0:
            first_page = current_page - 3
        last_page = first_page + 5
        if last_page > context['page_obj'].paginator.num_pages:
            last_page = context['page_obj'].paginator.num_pages
        first_page = first_page - 1
        context['user_is_tutor'] = context['forum'].segment.course.tutor == self.request.user
        context['page_range'] = list(context['page_obj'].paginator.page_range)[first_page:last_page]
        context['current_page'] = current_page
        context['prev'] = self.request.GET.get('prev')
        context['messages_json'] = json.dumps({m.id: m.body for m in self.object_list})
        return context

    def get_queryset(self):
        qs = super().get_queryset().filter(is_removed=False)
        forum = self.get_forum()
        if forum and self.user_enabled():
            qs = qs.filter(forum=forum)
        else:
            raise PermissionDenied
        return qs
        
    def user_enabled(self):
        forum = self.get_forum()
        segment_tracking = self.request.user.segmenttracking_set.filter(video=forum.segment).first()
        tutor = forum.segment.course.tutor
        if segment_tracking or tutor == self.request.user or self.request.user.is_superuser:
            return True
        return False

    def get_initial(self):
        initial = super().get_initial()
        initial['forum'] = self.get_forum()
        initial['user'] = self.request.user
        initial['segment_tracking'] = self.request.user.segmenttracking_set.filter(video=initial['forum'].segment).first()
        return initial

    def get_forum(self):
        return Forum.objects.filter(pk=int(self.kwargs['forum'])).first()

    def form_valid(self, form):
        forum_message = form.save()
        forum_message.edited = forum_message.created
        forum_message.save()
        history_record = ForumMessageHistoryRecord(
            forum_message = forum_message,
            message = forum_message.body,
            edited_by = self.request.user
        )
        history_record.save()
        prev = self.request.POST.get('prev')
        return HttpResponseRedirect(self.request.path_info + '?prev=' + prev)


class ForumMessageViewSet(viewsets.ModelViewSet):
    queryset = ForumMessage.objects.none()
    authentication_classes = (authentication.CsrfExemptSessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ForumMessageSerializer
    # No permito POST, es sólo para update y delete
    http_method_names = ['patch', 'options', 'delete']

    def perform_destroy(self, instance):
        instance.is_removed = True
        instance.delete_date = timezone.now()
        instance.delete_by = self.request.user
        instance.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ForumMessage.objects.filter(is_removed=False)
        else:
            return ForumMessage.objects.filter(Q(user=user) | Q(forum__segment__course__tutor=user))


class ForumViewSet(viewsets.ModelViewSet):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer


class ForumOrderList(generics.ListAPIView):
    serializer_class = ForumSerializer

    def get_queryset(self):
        segment = self.kwargs['segment']
        return Forum.objects.filter(segment__id=segment).order_by('order')

