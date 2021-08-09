# urls.py
from django.urls import include, path
from .views import pago_exitoso, pago_fallido, pagar_curso

urlpatterns = [
    path(r'callbacks/', include('payments.urls')),
    path(r'<int:pk>/exito/', pago_exitoso, name='pago-exitoso'),
    path(r'<int:pk>/error/', pago_fallido, name='pago-fallido'),
    path(r'<int:pk>/pagar/', pagar_curso, name='pagar-curso'),
]