from users.models import User
from .models import EncuestaTracking


def reset_user_polls_tracking(email):
    u = User.objects.get(email=email)
    EncuestaTracking.objects.filter(usuario=u).delete()
