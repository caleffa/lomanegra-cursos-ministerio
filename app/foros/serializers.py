from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import ForumMessage, ForumMessageHistoryRecord, Forum

class ForumSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='title', read_only=True)

    class Meta:
        model = Forum
        fields = [
            'id',
            'order',
            'title',
            'name',
            'segment'
        ]

class ForumMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumMessage
        fields = ['id', 'body']

    @transaction.atomic()
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user

        instance = super().update(instance, validated_data)

        ForumMessageHistoryRecord.objects.create(
            forum_message=instance,
            message=instance.body,
            edited_by=user
        )

        return instance
