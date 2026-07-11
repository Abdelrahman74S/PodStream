from django.db import models
from Accounts.storages import MediaStorage
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Tags(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Podcast(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='podcasts')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='podcasts')    
    tags = models.ManyToManyField(Tags, blank=True, related_name='podcasts')
    cover_image = models.ImageField(upload_to='podcast_covers/', null=True, blank=True , storage=MediaStorage())
    is_published  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE, related_name='episodes')
    title = models.CharField(max_length=255)
    description = models.TextField()
    audio_file = models.FileField(upload_to='podcast_episodes/', storage=MediaStorage())
    duration = models.IntegerField(help_text= "Duration of the episode in seconds")
    file_size = models.BigIntegerField(help_text= "Size of the audio file in bytes")
    transcript = models.TextField(null=True, blank=True)
    episode_number = models.IntegerField()
    is_explicit = models.BooleanField(default=False)
    publish_date = models.DateTimeField()
    listen_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['episode_number']

    def __str__(self):
        return f"{self.podcast.title} - Ep #{self.episode_number}: {self.title}"