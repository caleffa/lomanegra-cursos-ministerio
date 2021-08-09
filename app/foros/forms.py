from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ForumMessage

class ForumMessageForm(forms.ModelForm):
    class Meta:
        model = ForumMessage
        fields = ['forum', 'user', 'segment_tracking', 'replies_to', 'body']
        widgets = {
            'forum': forms.HiddenInput(),
            'user': forms.HiddenInput(),
            'segment_tracking': forms.HiddenInput(),
            'replies_to': forms.HiddenInput()
        }
        labels = {
            'body': ''
        }
        error_messages = {
            'body': { 'required': _('El comentario no puedo estar vacío') }
        }
