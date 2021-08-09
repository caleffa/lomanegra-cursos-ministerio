from rest_framework import serializers


# serializa una lista de DateTimes
class DateTimeListField(serializers.ListField):
    def __init__(self, **kwargs):
        self.child = serializers.DateTimeField()
        super().__init__(**kwargs)
