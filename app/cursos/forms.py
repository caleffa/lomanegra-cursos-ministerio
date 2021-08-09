from django import forms
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm
from .models import AllowedEmail, AllowedDomain, SiteSettings


class EveryComplianceSignupForm(SignupForm):
    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': _('Nombre')}
        ), 
        max_length=40, 
        label='Nombre', 
        required=True
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': _('Apellido')}
        ), 
        max_length=40, 
        label='Apellido', 
        required=True
    )

    def save(self, *args, **kwargs):
        instance = super(EveryComplianceSignupForm, self).save(*args, **kwargs)        
        instance.name = self.cleaned_data["name"]
        instance.save()

        # No se necesita más esto, se hace en el save() de User
        # ae = AllowedEmail.objects.filter(email__iexact=instance.email).first()
        # if not ae:
        #     # Si no existe en AllowedEmail entonces validó por dominio. Tengo que crearlo en AllowedEmail
        #     ae = AllowedEmail.objects.create(email=instance.email)
        # ae.user = instance
        # ae.save()

        return instance

    def clean_email(self):
        value = super(EveryComplianceSignupForm, self).clean_email()
        self.validate_allowed_email(value)
        return value

    def validate_allowed_email(self, email):
        site_settings: SiteSettings = SiteSettings.get_solo()

        if not site_settings.requires_allowed_email:
            return
        
        # Ojo, acá asumimos direcciones de email case-insensitive
        allowed_email = AllowedEmail.objects.filter(email__iexact=email).first()
        user_part, domain_part = email.split('@')
        allowed_domain = AllowedDomain.objects.filter(domain__iexact=domain_part).first()

        if not allowed_email and not allowed_domain:
            raise forms.ValidationError(_('Su dirección de email no se encuentra habilitada para esta aplicación'))