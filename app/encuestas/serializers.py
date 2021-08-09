from rest_framework import serializers
from django.db import transaction
import json

from .models import Pregunta, OpcionPregunta


class PreguntaListSerializer(serializers.ListSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/#customizing-multiple-update
    @transaction.atomic
    def update(self, instance, validated_data):
        '''
        El endpoint recibe una lista de preguntas para la encuesta X.
        Qué hay en instance? Debería estar la lista de preguntas de la encuesta X (la que está en DB)
        en validated_data recibimos una nueva lista
        Eso que recibimos es lo que se settea como nueva lista de preguntas de
        :param instance: ? QuerySet de Pregunta ? Pregunta.object.filter(encuesta__id=self.kwargs['encuesta']
        :param validated_data: una lista de objetos de pregunta
        :return:
        '''
        # preguntas_originales = {preg.id: preg for preg in instance}
        # # preguntas_modificadas = {preg['id']: preg if preg.get('id') for preg in validated_data}
        # # preguntas_nuevas = [preg if not preg.get('id') for preg in validated_data]
        # print('Instance:')
        # for p in instance:
        #     print(p)
        # print('preguntas_originales:')
        # print(preguntas_originales)
        # print('Queryset Preguntas:')

        # encuesta = Encuesta.objects.
        ret = []
        order = 0
        for item in validated_data:
            # if Pregunta.objects.get(encuesta__id=self.kwargs['encuesta'], order=order)
            item['order'] = order
            if item.get('id'):
                # update
                ret.append(self.child.update(item))
            else:
                # create
                ret.append(self.child.create(item))
            order += 1

        return ret

class OpcionPreguntaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = OpcionPregunta
        fields = [
            'id',
            'texto'
        ]


class PreguntaSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    opciones = OpcionPreguntaSerializer(many=True, required=False)
    opciones_json = serializers.JSONField(default='')
    imagen_url = serializers.SerializerMethodField()
    imagen_pulgar_arriba_url = serializers.SerializerMethodField()
    imagen_pulgar_abajo_url = serializers.SerializerMethodField()

    class Meta:
        model = Pregunta
        list_serializer_class = PreguntaListSerializer
        fields = [
            'id',
            'encuesta',
            'tipo',
            'texto',
            'imagen',
            'imagen_url',
            'aditiva_debe_contestar_al_menos_una',
            'texto_estrella_1',
            'texto_estrella_2',
            'texto_estrella_3',
            'texto_estrella_4',
            'texto_estrella_5',
            'texto_pulgar_arriba',
            'texto_pulgar_abajo',
            'imagen_pulgar_arriba',
            'imagen_pulgar_arriba_url',
            'imagen_pulgar_abajo',
            'imagen_pulgar_abajo_url',
            'opciones',
            'opciones_json'
        ]

    def get_imagen_url(self, preg):
        return self.get_any_image(preg.imagen)

    def get_imagen_pulgar_arriba_url(self, preg):
        return self.get_any_image(preg.imagen_pulgar_arriba)

    def get_imagen_pulgar_abajo_url(self, preg):
        return self.get_any_image(preg.imagen_pulgar_abajo)

    def get_any_image(self, image):
        if image:
            request = self.context.get('request')
            return request.build_absolute_uri(image.url)
        return None

    def create(self, validated_data):
        tipo = validated_data['tipo']
        opciones = validated_data['opciones_json']
        if (not tipo == Pregunta.EXCLUYENTE or not tipo == Pregunta.ADITIVA) or len(opciones) > 0:
            del validated_data['opciones_json']
            preg = Pregunta.objects.create(**validated_data)
            for opcion in opciones:
                self.create_opcion(opcion, preg)
            return preg

    def update(self, instance, validated_data):
        tipo = validated_data['tipo']
        opciones = validated_data['opciones_json']
        if (not tipo == Pregunta.EXCLUYENTE or not tipo == Pregunta.ADITIVA) or len(opciones) > 0:
            del validated_data['opciones_json']
            preg_qs = Pregunta.objects.filter(pk=int(validated_data['id']))
            preg_qs.update(**validated_data)
            for opcion in opciones:
                if 'id' in opcion:
                    OpcionPregunta.objects.filter(pk=opcion['id']).update(**opcion)
                else:
                    self.create_opcion(opcion, preg_qs.first())
            return preg_qs.first()

    def create_opcion(self, opcion, preg):
        op = OpcionPregunta()
        op.texto = opcion['texto']
        op.pregunta = preg
        op.save()