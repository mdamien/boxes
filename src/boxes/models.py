from django.db import models
from django.core.urlresolvers import reverse

class Box(models.Model):
    name = models.CharField(max_length=300)

    def url(self):
        return reverse('boxes.views.box',args=(self.pk,))
    
    def __str__(self):
        return self.name

class Idea(models.Model):
    box = models.ForeignKey(Box)
    title = models.CharField(max_length=300)
    content = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now=True)

    def url(self):
        return reverse('boxes.views.idea',args=(self.box.pk, self.pk,))
    
    def __str__(self):
        return self.title
