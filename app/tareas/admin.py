from django.contrib import admin
from .models import Tarea, Adjunto, TareaAlumno, Devolucion

admin.site.register(Tarea)
admin.site.register(Adjunto)
admin.site.register(TareaAlumno)
admin.site.register(Devolucion)
