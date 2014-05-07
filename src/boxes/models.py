from django.db import models
from django.core.urlresolvers import reverse

class Box(models.Model):
    name = models.CharField(max_length=300)

    def url(self):
        return reverse('boxes.views.box',args=(self.pk,))

    def __str__(self):
        return self.name


