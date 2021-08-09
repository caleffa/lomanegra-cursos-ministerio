from django.urls import path

from .views import EncuestaView
from videocursos.urls import normal_user_test, dashboard_admin_test

app_name = 'encuestas'
urlpatterns = [
    path('<int:encuesta>', normal_user_test(EncuestaView.as_view()), name='encuesta')
]