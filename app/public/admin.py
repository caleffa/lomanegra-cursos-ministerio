from django.contrib import admin
from .models import PublicSegment


class PublicSegmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'vimeo_id', 'genially_id', 'external_link', 'order']
    list_editable = ['order']
    ordering = ['order']
    sortable_by = ['order', 'title']


admin.site.register(PublicSegment, PublicSegmentAdmin)
