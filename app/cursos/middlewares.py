from django.contrib.auth import logout
from django.core.cache import cache # Default cache
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.signals import user_logged_out


def get_cache_key(user):
    return "user_pk_%s_restrict" % user.pk


def logout_handler(sender, user, request, **kwargs):
    cache_key = get_cache_key(request.user)
    cache_value = cache.get(cache_key)

    # Si estoy logouteando la sesión que estaba guardada en la cache. Entonces tengo que borrarla
    # para permitir nuevos logins.
    if cache_value is not None and cache_value == request.session.session_key:
        cache.delete(cache_key)


user_logged_out.connect(logout_handler, dispatch_uid='one-session-per-user-on-logout')


class OneSessionPerUserMiddleware:
    # Called only once when the web server starts
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.user.is_authenticated:
            # Levanto el mismo setting que se usa para expirar la sesión
            cache_timeout = getattr(settings, 'SESSION_SECURITY_EXPIRE_AFTER', 10*60)
            cache_key = get_cache_key(request.user)
            cache_value = cache.get(cache_key)

            # Si existe el valor en la cache entonces el usuario ya está logueado.
            # Si no, entonces esta es su única sesión. Guardamos la key en la cache y continuamos.
            if cache_value is not None and cache_value != request.session.session_key:
                logout(request)
                return HttpResponseRedirect(reverse('multiple-sessions'))
            else:
                cache.set(cache_key, request.session.session_key, cache_timeout)

        response = self.get_response(request)

        # This is where you add any extra code to be executed for each request/response after
        # the view is called.
        # For this tutorial, we're not adding any code so we just return the response

        return response
