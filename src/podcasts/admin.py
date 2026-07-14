from django.contrib import admin
from .models import Podcast, Episode ,Category , Tags

@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator','tags__name','is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'podcast', 'episode_number', 'publish_date', 'listen_count')
    list_filter = ('publish_date', 'is_explicit')
    search_fields = ('title', 'description', 'podcast__title')
    readonly_fields = ('duration', 'file_size', 'transcript', 'listen_count')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)