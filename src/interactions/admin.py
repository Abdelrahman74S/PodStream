from django.contrib import admin
from .models import Subscription, Playlist, Comment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'podcast', 'subscribed_at', 'notify_new_episodes')
    list_filter = ('notify_new_episodes', 'subscribed_at')
    search_fields = ('user__username', 'podcast__title')

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'user__username', 'description')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'episode', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'episode__title', 'text')
