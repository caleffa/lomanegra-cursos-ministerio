from django.contrib import admin
from .models import Forum, ForumMessage, ForumMessageHistoryRecord


class ForumAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'segment']
    list_filter = ['segment', 'segment__course']
    list_editable = ['order']


class ForumMessageHistoryRecordAdmin(admin.ModelAdmin):
    list_display = ['forum_message', 'message', 'created', 'edited_by']
    list_filter = ['forum_message__forum__segment__course', 'forum_message__forum']

admin.site.register(Forum, ForumAdmin)
admin.site.register(ForumMessage)
admin.site.register(ForumMessageHistoryRecord, ForumMessageHistoryRecordAdmin)
