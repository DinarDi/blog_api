from django.contrib import admin

from .models import Post, Comment, UserPostRelation


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'title', 'status']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created']


@admin.register(UserPostRelation)
class UserPostRelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'like', 'in_bookmarks']
