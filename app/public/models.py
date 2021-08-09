from django.db import models
from cursos.models import VideoData, GeniallyData, BaseSegment


class PublicSegment(VideoData, GeniallyData, BaseSegment):
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default='')
    external_link = models.URLField(blank=True)
    open_external_link_in = models.CharField(max_length=30, choices=[('_self', '_self'), ('_blank', '_blank')],
                                             blank=True)
