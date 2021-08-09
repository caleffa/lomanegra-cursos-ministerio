from django.shortcuts import redirect

from .views import redirect_to_encuesta
from .models import Encuesta


class EncuestaPendienteMiddleware:
    ''' middleware para verificar si el usuario tiene encuestas pendientes.
    Si es una encuesta obligatoria en login, lo redirijimos.
    (esto no aplica si está entrando a una vista de encuestas o del admin)
    '''
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not set(['encuestas', 'admin', 'mensajes', 'admin_light', 'api']) & set(request.resolver_match.namespaces):
            if request.user.is_authenticated:
                encuestas_pendientes = Encuesta.objects.pending_for(request.user).mandatory().on_login().open_now()
                if encuestas_pendientes:
                    return redirect_to_encuesta(request.get_full_path(), encuesta=encuestas_pendientes.first())
