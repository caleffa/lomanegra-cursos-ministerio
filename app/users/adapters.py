from typing import Any

from allauth.account.adapter import DefaultAccountAdapter, get_current_site
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import resolve_url
from encuestas.models import Encuesta


class AccountAdapter(DefaultAccountAdapter):

    def is_open_for_signup(self, request: HttpRequest):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # Es una copia del original pero agrego el request al contexto del template

        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(
            request,
            emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
            "request": request,
        }
        if signup:
            email_template = 'account/email/email_confirmation_signup'
        else:
            email_template = 'account/email/email_confirmation'
        self.send_mail(email_template,
                       emailconfirmation.email_address.email,
                       ctx)

    def get_login_redirect_url(self, request):
        encuestas_pendientes = Encuesta.objects.snoozed(request.user)
        if encuestas_pendientes:
            return resolve_url('encuestas:encuesta', encuesta=encuestas_pendientes.first().pk)
        return super().get_login_redirect_url(request)


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request: HttpRequest, sociallogin: Any):
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
