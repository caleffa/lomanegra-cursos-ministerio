from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, TemplateView
from django.contrib.auth import authenticate, login
from .models import PublicSegment


class PublicView(TemplateView):
    template_name = 'public/public.html'

    def dispatch(self, request, *args, **kwargs):
        user = authenticate(request)
        if user is not None:
            login(request, user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_home_page'] = True
        return context


class RedirectException(Exception):
    def __init__(self, redirect_to):
        self.redirect_to = redirect_to


class PublicSegmentDetailView(DetailView):
    model = PublicSegment
    context_object_name = 'segment'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.external_link:
            raise RedirectException(obj.external_link)
        return obj

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except RedirectException as e:
            return redirect(e.redirect_to)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Videos informativos'
        return context


class PublicSegmentListView(ListView):
    queryset = PublicSegment.objects.order_by('order')
    context_object_name = 'segments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Videos informativos'
        return context