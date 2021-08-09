from django.db import models

class ClonableModelMixin(models.Model):

    class Meta:
        abstract = True

    def clone(self, parent_field=None, parent=None):
        original_pk = self.pk
        self.pk = None
        if parent_field:
            setattr(self, parent_field, parent)
        self.save()
        original = self.__class__.objects.get(pk=original_pk)
        self.clone_children(original)

    def clone_children(self, original):
        pass
