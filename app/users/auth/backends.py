from django.contrib.auth.backends import ModelBackend
from django.utils.translation import ugettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.state import User
from users.models import ExternalUser
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError


class JWTBackend(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.GET.get('token', None)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self._get_user(validated_token)

    def get_user(self, user_id):
        user = User.objects.filter(id=user_id).first()
        return user

    def _get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            external_user = ExternalUser.objects.filter(external_id=user_id).first()
            if not external_user:
                # Creo el User y el ExternalUser
                username = f'user_{user_id}@autogen.com'
                u = User.objects.create(
                    name=validated_token['nombre'],
                    last_name=validated_token['apellido'],
                    dni=validated_token.get('dni', ''),
                    email=username,
                    username=username,
                )
                external_user = ExternalUser.objects.create(user=u, external_id=user_id)

                # El usuario no se debe poder loguear por sí mismo
                u.set_unusable_password()
                u.save()
            user = external_user.user
        except User.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user