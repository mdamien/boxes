from django.contrib import admin
from .models import Box, Idea, Comment

class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'access_mode', 'email_suffix')
    search_fields = ('name', 'slug')
    list_filter = ('access_mode',)

class IdeaAdmin(admin.ModelAdmin):
    list_display = ('title', 'box', 'date', 'cached_score', 'user_key') 
    search_fields = ('title', 'box', 'user_key')
    list_filter = ('date',)

class CommentAdmin(admin.ModelAdmin):
    list_display = ('title', 'box', 'date', 'cached_score', 'user_key') 
    list_display = ('content', 'idea', 'date', 'user_key') 
    search_fields = ('content', 'user_key')
    list_filter = ('date',)

admin.site.register(Box, BoxAdmin)
admin.site.register(Idea, IdeaAdmin)
admin.site.register(Comment, CommentAdmin)
