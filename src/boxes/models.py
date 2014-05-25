from django.db import models
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import hashlib, random
from boxes import helpers

class Box(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=300, blank=True)

    ACCESS_BY_SESSION = 0
    ACCESS_BY_EMAIL = 1
    ACCESS_BY_GOOGLE = 2
    ACCESS_MODES = (
       (ACCESS_BY_SESSION,'session'),
       (ACCESS_BY_EMAIL,'email'),
       (ACCESS_BY_GOOGLE,'google'),
    )
    access_mode = models.IntegerField(choices=ACCESS_MODES, default=ACCESS_BY_SESSION)
    
    user_key = models.CharField(max_length=40) 
 
    #access restriction by email
    email_suffix = models.CharField(max_length=100, blank=True, null=True)
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
        key = helpers.randascii(5)
        keys = self.email_keys.split(',')
        keys.append(key)
        self.email_keys = ','.join(keys)

        self.save()
        return key

    def key_valid(self, key):
        return key in [key for key in self.email_keys.split(',') if key != '']

    def is_access_by_session(self):
        return self.access_mode == self.ACCESS_BY_SESSION
    
    def is_access_by_email(self):
        return self.access_mode == self.ACCESS_BY_EMAIL
    
    def is_access_by_google(self):
        return self.access_mode == self.ACCESS_BY_GOOGLE

    def url(self):
        return reverse('boxes.views.box',args=(self.pk,))

    def get_absolute_url(self):
        return self.url()
    
    def __str__(self):
        return self.name

class Idea(models.Model):
    box = models.ForeignKey(Box)
    title = models.CharField(max_length=300)
    content = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    cached_score = models.IntegerField(default=0)
    user_key = models.CharField(max_length=40) #session_key, email_key, user_id 

    def color(self):
        return helpers.color(self.user_key)

    def score(self):
        return self.cached_score

    def compute_score(self):
        score = Vote.objects.filter(idea=self).aggregate(Sum('vote')).get('vote__sum')
        if score is None:
            return 0
        return score

    def compute_hot_score(self):
        return helpers.hot_score(self.score(), self.date.replace(tzinfo=None))

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

    user_key = models.CharField(max_length=40) #session_key, email_key, user_id 

    def from_str(vote):
        return {'up':1,'down':-1}.get(vote)


class Comment(models.Model):
    idea = models.ForeignKey(Idea)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    user_key = models.CharField(max_length=40) #session_key, email_key, user_id 

    def color(self):
        return helpers.color(self.user_key)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.content
