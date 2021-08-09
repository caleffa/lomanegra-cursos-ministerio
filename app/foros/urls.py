from django.urls import path
from django.contrib.auth.decorators import login_required
from rest_framework.routers import SimpleRouter

from .views import MyCommentsView, ForumView, ForumMessageViewSet
from videocursos.urls import normal_user_test

router = SimpleRouter()
router.register('api/forum_messages', ForumMessageViewSet)

urlpatterns = [
    path('mis-comentarios', normal_user_test(MyCommentsView.as_view()), name='my_comments'),
    path('<int:forum>', normal_user_test(ForumView.as_view()), name='forum')
] + router.urls
