from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from allauth.account import views

from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from .forms import CustomLoginForm

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name", "last_name", "dni", "avatar"]

    def get_success_url(self):
        return reverse("home")

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hide_title'] = True
        return context


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("home")


user_redirect_view = UserRedirectView.as_view()


class CustomLoginView(views.LoginView):
    form_class = CustomLoginForm
