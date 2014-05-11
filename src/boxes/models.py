from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Sum

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
    date = models.DateTimeField(auto_now_add=True)
    cached_score = models.IntegerField(default=0)
    session_key = models.CharField(max_length=40)

    def score(self):
        return self.cached_score

    def compute_score(self):
        score = Vote.objects.filter(idea=self).aggregate(Sum('vote')).get('vote__sum')
        if score is None:
            return 0
        return score

    def update_cached_score(self):
        self.cached_score = self.compute_score()
        self.save()

    def url(self):
        return reverse('boxes.views.idea',args=(self.box_id, self.pk,))
    
    def __str__(self):
        return self.title

class Vote(models.Model):
    idea = models.ForeignKey(Idea)
    UP = 1
    DOWN = -1
    VOTES = (
       (UP,'up'),
       (DOWN,'down'),
    )
    vote = models.IntegerField(choices=VOTES)
    session_key = models.CharField(max_length=40)

    def from_str(vote):
        return {'up':1,'down':-1}.get(vote)
