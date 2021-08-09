from django.db import models

from cursos.models import Segment, SegmentTracking
from users.models import User
from backoffice.clone import ClonableModelMixin

class Forum(ClonableModelMixin, models.Model):
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = [('segment', 'title'), ('segment', 'order')]
        ordering = ['segment', 'order', 'title']

    def __str__(self):
        return f'{self.segment} | {self.title}'

class ForumMessage(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    segment_tracking = models.ForeignKey(SegmentTracking, on_delete=models.CASCADE, null=True, blank=True)
    body = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, blank=True, auto_now=True)
    is_removed = models.BooleanField(default=False)
    delete_date = models.DateTimeField(null=True, blank=True)
    delete_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='deleted_forum_messages')
    replies_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.user}: {self.body}'

class ForumMessageHistoryRecord(models.Model):
    forum_message = models.ForeignKey(ForumMessage, on_delete=models.CASCADE)
    message = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
