from rest_framework import serializers
from cursos.models import Segment


class SegmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Segment
        fields = [
            'is_broadcasting_now'
        ]
        read_only_fields = [
            'is_broadcasting_now'
        ]
