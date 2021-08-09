from rest_framework import serializers

from .models import Tarea, Adjunto


class AdjuntoSerializer(serializers.ModelSerializer):

    nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Adjunto
        fields = [
            'id',
            'archivo',
            'nombre'
        ]

    def get_nombre(self, obj):
        array = obj.archivo.name.split("/")
        return array[len(array)-1]


class TareaSerializer(serializers.ModelSerializer):

    adjuntos_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tarea
        fields = [
            'id',
            'segmento',
            'titulo',
            'descripcion',
            'obligatoria',
            'adjuntos',
            'adjuntos_data'
        ]

    def get_adjuntos_data(self, obj):
        serializer = AdjuntoSerializer(many=True, data=obj.adjuntos)
        serializer.is_valid()
        return serializer.data
