from django.urls import path

from .views import AltaCursosView, CourseAdminUpdateView, CourseListView
from videocursos.urls import normal_user_test

urlpatterns = [
    path('alta-cursos', normal_user_test(AltaCursosView.as_view()), name='alta_cursos'),
    # path('curso/<int:pk>', CourseAdminUpdateView.as_view(), name='course-admin-update'),
    path('lista-cursos', normal_user_test(CourseListView.as_view()), name="lista_cursos")
]
