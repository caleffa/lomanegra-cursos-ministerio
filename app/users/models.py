from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator, ValidationError
from django.db import transaction
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit


def no_at_validator(value):
    if value is not None:
        if '@' in value:
            raise ValidationError(message=_('Debe ingresar el dominio sin la "@"'))


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Nombre"), blank=True, max_length=255)
    last_name = models.CharField(_("Apellido"), blank=True, max_length=255)
    dni = models.CharField(_("DNI"), blank=True, max_length=9)
    avatar = models.ImageField(_("Imagen de perfil"), blank=True, null=True, upload_to="avatars")
    avatar_thumbnail = ImageSpecField(processors=[ResizeToFit(width=55, height=55, mat_color=(255, 255, 255, 0))],
                                      source='avatar', format='PNG')
    # area = models.ForeignKey('cursos.Area', on_delete=models.PROTECT, null=True, blank=True,
    #                          verbose_name='Área/Departamento/Sector',
    #                          help_text='El área/departamento/sector al que pertenece este usuario.')
    enabled_courses = models.ManyToManyField('cursos.Course', related_name='enabled_users', blank=True,
                                             verbose_name=_('Cursos habilitados'), help_text=_('Son los cursos que tiene habilitados este socio de manera directa. Tener en cuenta que también podrá acceder a los cursos que estén habilitados para su área/departamento/sector y a los cursos en los que ya esté inscripto.'))
    domain = models.CharField(max_length=63, db_index=True, null=True, blank=True,
                              validators=[RegexValidator(EmailValidator.domain_regex,
                                                         message=_('El valor ingresado no es un dominio válido')),
                                          no_at_validator],
                              verbose_name=_('Dominio'))
    is_tutor = models.BooleanField(default=False, verbose_name=_('Es Tutor'))
    is_stakeholder = models.BooleanField(default=False, verbose_name=_('Es Stakeholder'))

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def has_perm(self, perm, obj=None):
        if self.is_active and (self.is_staff or self.is_superuser):
            return True
        else:
            return super(User, self).has_perm(perm, obj=obj)

    def has_module_perms(self, app_label):
        if self.is_active and (self.is_staff or self.is_superuser):
            return True
        else:
            return super(User, self).has_module_perms(app_label)



    @property
    def area(self):
        if hasattr(self, 'allowed_email') and self.allowed_email:
            return self.allowed_email.area
        return None

    @transaction.atomic()
    def save(self, *args, **kwargs):
        user_part, domain_part = self.email.split('@')
        self.domain = domain_part.lower()
        super(User, self).save(*args, **kwargs)

        # Claramente AllowedEmail debería estar en la app de usuarios...
        from cursos.models import AllowedEmail, SiteSettings
        site_settings: SiteSettings = SiteSettings.get_solo()

        if not (hasattr(self, 'allowed_email') and self.allowed_email):
            ae = AllowedEmail.objects.filter(email__iexact=self.email).first()
            if ae:
                ae.user = self
                ae.save()
            else:
                area = None
                if not site_settings.requires_allowed_email:
                    area = site_settings.default_area
                ae = AllowedEmail.objects.create(email=self.email, user=self, area=area)


class ExternalUser(models.Model):
    user = models.OneToOneField(User, related_name='external_user', on_delete=models.CASCADE)
    external_id = models.CharField(max_length=128, db_index=True)
