from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import hashlib, random
from datetime import datetime
from math import log

epoch = datetime(1970, 1, 1)

def epoch_seconds(date):
    """Returns the number of seconds from the epoch to date."""
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

def hot_score(score, date):
    """The hot formula from reddit"""
    order = log(max(abs(score), 1), 10)
    sign = 1 if score > 0 else -1 if score < 0 else 0
    seconds = epoch_seconds(date) - 1134028003
    return round(order + sign * seconds / 45000, 7)

def color(seed):
    """Return a random hue associated with the seed"""
    rand = random.Random(seed)
    return int(rand.random()*255)

class Box(models.Model):
    name = models.CharField(max_length=300)

    ACCESS_BY_SESSION = 0
    ACCESS_BY_EMAIL = 1
    ACCESS_BY_GOOGLE = 2
    ACCESS_MODES = (
       (ACCESS_BY_SESSION,'session'),
       (ACCESS_BY_EMAIL,'email'),
       (ACCESS_BY_GOOGLE,'google'),
    )
    access_mode = models.IntegerField(choices=ACCESS_MODES, default=ACCESS_BY_SESSION)
    
    #access restriction by email
    email_suffix = models.CharField(max_length=100)
    email_list = models.TextField(blank=True) #comma-separated hashed mail list
    email_keys = models.TextField(blank=True) #comma-separated access keys list

    def email_register(self,email):
        #validate email
        validate_email(email)
        if not email.endswith('@'+self.email_suffix):
            raise ValidationError("email address has to end with @%s" % self.email_suffix)

        email_list = self.email_list.split(',')
        hashed_email = hashlib.sha1(email.encode('utf-8')).hexdigest()
        if hashed_email in email_list:
            raise ValidationError("Access code already sent to this email")

        email_list.append(hashed_email)
        random.shuffle(email_list)
        self.email_list = ','.join(email_list)

        #generate key
        key = hashlib.sha1(str(random.SystemRandom().random()).encode('utf-8')).hexdigest()[:5]
        keys = self.email_keys.split(',')
        keys.append(key)
        self.email_keys = ','.join(keys)

        self.save()

        return key

    def key_valid(self, key):
        return key in [key for key in self.email_keys.split(',') if key != '']

    def is_access_by_session(self):
        return self.access_mode == self.ACCESS_BY_SESSION

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

    def color(self):
        return color(self.session_key)

    def score(self):
        return self.cached_score

    def compute_score(self):
        score = Vote.objects.filter(idea=self).aggregate(Sum('vote')).get('vote__sum')
        if score is None:
            return 0
        return score

    def compute_hot_score(self):
        return hot_score(self.score(), self.date.replace(tzinfo=None))

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

    #access_key = session_key in case of an anonymous box
    access_key = models.CharField(max_length=40)

    def from_str(vote):
        return {'up':1,'down':-1}.get(vote)


class Comment(models.Model):
    idea = models.ForeignKey(Idea)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    session_key = models.CharField(max_length=40)

    def color(self):
        return color(self.session_key)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.content
