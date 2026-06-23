from django.contrib import admin

from .models import Comment, Post, PostLike


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'created_at', 'updated_at']
    search_fields = ['title', 'content', 'author__username']
    list_filter = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'author', 'parent', 'created_at', 'updated_at']
    search_fields = ['content', 'author__username', 'post__title']
    list_filter = ['created_at']


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'created_at']
    search_fields = ['post__title', 'user__username']
    list_filter = ['created_at']