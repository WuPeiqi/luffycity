from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation


class A(models.Model):
    title = models.CharField(max_length=32)
    rele = GenericRelation('C')

class B(models.Model):
    name = models.CharField(max_length=32)


class C(models.Model):
    content_type = models.ForeignKey(ContentType)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    txt = models.CharField(max_length=32)
