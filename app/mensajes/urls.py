from django.urls import path
from django.contrib.auth.decorators import login_required

from videocursos.urls import normal_user_test

from .views import InboxView, ConversacionView, send_message, IniciarConversacionView, generar_conversaciones, UnreadMessages

app_name = 'mensajes'
urlpatterns = [
    path('mensajes', normal_user_test(InboxView.as_view()), name='inbox'),
    path('mensajes/<int:page>', normal_user_test(InboxView.as_view()), name='inbox_page'),
    path('conversacion/<int:conversacion>', normal_user_test(ConversacionView.as_view()), name='conversacion'),
    path('enviar-mensaje', normal_user_test(send_message), name='send_message'),
    path('iniciar-conversacion', normal_user_test(IniciarConversacionView.as_view()), name='iniciar_conversacion'),
    path('iniciar-conversacion/<int:preselect>', normal_user_test(IniciarConversacionView.as_view()), name='iniciar_conversacion_preselect'),
    path('generar-conversaciones', generar_conversaciones, name="generar_conversaciones"),
    path('mensajes-sin-leer', UnreadMessages.as_view(), name="get_unread_messages"),
]
