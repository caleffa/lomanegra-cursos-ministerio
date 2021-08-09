from rest_framework import viewsets, authentication, permissions, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Pregunta, OpcionPregunta, Encuesta
from .serializers import PreguntaSerializer, OpcionPreguntaSerializer


class PreguntaListAPIView(generics.ListAPIView):
    serializer_class = PreguntaSerializer

    def get_queryset(self):
        return Pregunta.objects.filter(encuesta__id=self.kwargs['encuesta'])


class PreguntaEncuestaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer


    def partial_update(self, request, pk=None):
        response = super().partial_update(request, pk)
        pregunta = Pregunta.objects.get(pk=pk)
        if 'imagen' in request.data:
            pregunta.imagen = request.data['imagen']
        if 'imagen_pulgar_arriba' in request.data:
            pregunta.imagen_pulgar_arriba = request.data['imagen_pulgar_arriba']
        if 'imagen_pulgar_abajo' in request.data:
            pregunta.imagen_pulgar_abajo = request.data['imagen_pulgar_abajo']
        pregunta.save()
        return response


class OpcionPreguntaEncuestaViewSet(viewsets.ModelViewSet):
    queryset = OpcionPregunta.objects.all()
    serializer_class = OpcionPreguntaSerializer


class SetPreguntasOrderViewSet(APIView):
    http_method_names = ['post']

    def post(self, request):
        enc = Encuesta.objects.get(pk=request.data.get('encuesta'))
        enc.set_pregunta_order(request.data.get('order'))
        return Response(True)
