from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (TareaCreateView, EliminarDevolucionAPIView, AprobarTareaAlumnoAPIView, 
                    TareasListView)
from videocursos.urls import normal_user_test

router = SimpleRouter()

app_name = 'tareas'
urlpatterns = [
    path('', normal_user_test(TareasListView.as_view()), name='tareas'),
    path('<int:tarea>', normal_user_test(TareaCreateView.as_view()), name='tarea'),
    path('eliminar_devolucion/<int:devolucion>', EliminarDevolucionAPIView.as_view(), name='eliminar-devolucion'),
    path('aprobar_tarea_alumno/<int:tarea_alumno>', AprobarTareaAlumnoAPIView.as_view(), name='aprobar_tarea_alumno')
] + router.urls
