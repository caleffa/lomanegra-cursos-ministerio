from django.urls import path
from django.contrib.auth.decorators import login_required
from rest_framework.routers import SimpleRouter

from .views import MisTransmisiones
from videocursos.urls import dashboard_tutor_test

urlpatterns = [
    path('mis-transmisiones', dashboard_tutor_test(MisTransmisiones.as_view()), name='mis_transmisiones'),
]
